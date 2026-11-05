# Deployment

BOA runs on AWS Elastic Beanstalk (EB) on Amazon Linux. A CodeBuild job builds the Vue frontend and packages the repo; EB installs the Python dependencies, runs the platform hooks, and starts gunicorn behind Apache. Travis CI runs the lint, build, and test checks on every push. The pipeline itself (source, CodeBuild project, EB environments, environment properties) is configured in AWS, not in this repo.

Key files: `buildspec.yml` (CodeBuild), `scripts/code_pipeline/pre_build_phase.sh` and `post_build_phase.sh`, `.ebextensions/*.config` (EB options, packages, files), `.platform/hooks/predeploy/` and `.platform/hooks/postdeploy/`, `Procfile` (process), `application.py` (WSGI entry), `boac/configs.py` (config loading), `boac/logger.py`, `scripts/deploy_boac_config.sh`, `.travis.yml` and `tox.ini` (CI).

Related docs: schema migrations are in `scripts/db/CLAUDE.md`. The cache refresh job and `/api/ping` are in `.claude/docs/data-refresh-and-terms.md`.

## Build (CodeBuild, `buildspec.yml`)

| Phase | What runs |
|---|---|
| `install` | Runtimes `nodejs: 22` and `python: 3.11`, then `npm install` |
| `pre_build` | `chmod 755 ./scripts/*.sh`, then `pre_build_phase.sh`: writes `.env.local` with `VITE_APP_GOOGLE_ANALYTICS_ID` from the build's `GOOGLE_ANALYTICS_ID` variable |
| `build` | `npm run build-vue` = `vite build --outDir='dist/static'` (`package.json`) |
| `post_build` | `post_build_phase.sh`: writes `config/build-summary.json` with `build.artifact` (`CODEBUILD_SOURCE_VERSION`) and `build.gitCommit` (first 7 chars of `CODEBUILD_RESOLVED_SOURCE_VERSION`) |

- **Artifact contents.** `.ebextensions/`, `.platform/`, `Procfile`, `application.py`, `boac/`, `config/`, `consoler.py`, `dist/`, `fixtures/`, `requirements.txt`, `scripts/`. `src/`, `node_modules/`, `tests/`, and `bea/` are not shipped, so the server never needs Node.
- **Python packages are not installed in CodeBuild.** EB's Python platform installs `requirements.txt` on each instance during the deploy.
- `GET /api/version` (`boac/api/config_controller.py`) returns `version` plus the `build` block from `config/build-summary.json`, or `build: null` when the file is missing (e.g. locally). `config/*.json` is git-ignored.
- No frontend code reads `VITE_APP_GOOGLE_ANALYTICS_ID`. Google Analytics gets its ID from `GA_MEASUREMENT_ID` via `GET /api/config` (`gaMeasurementId`, used in `src/lib/ga.ts`).

## Deploy flow on each instance

EB applies the bundle in its standard order for Linux platforms. The BOA-specific pieces are:

```
bundle unpacked into the staging directory
  → .ebextensions/00_ami.config   yum packages (gcc-c++, git, postgresql15); EB options (below);
                                  security-group ingress on 443; writes /tmp/amazon-cloudwatch-agent.json
  → .ebextensions/01_create_apache_conf.config
                                  writes /tmp/ssl.conf and the instance's self-signed TLS certificate
  → .ebextensions/02_logs.config  adds /var/app/current/boa.log* to EB's bundled logs
  → pip install -r requirements.txt   (EB platform)
  → .platform/hooks/predeploy/
      01_download_local_configs.sh   copy s3://<deploy-config bucket>/boac/${EB_ENVIRONMENT}.py
                                     → config/production-local.py; append EB_ENVIRONMENT = '<name>';
                                     chown webapp, chmod 400
      02_secure_sshd_configs.sh      download sed rules from the same bucket, apply to a copy of
                                     sshd_config, validate with `sshd -t`, then swap it in
      03_download_private_key.sh     download the TLS private key → /etc/ssl/certs/, root-only 400
  → staging moved to /var/app/current; Procfile starts gunicorn; Apache starts
  → .platform/hooks/postdeploy/
      01_update_apache_config.sh     mv /tmp/ssl.conf → /etc/httpd/conf.d/ssl.conf; restart httpd
      02_start_awslogsd.sh           amazon-cloudwatch-agent-ctl append-config from /tmp/…json, start
```

Nothing in the repo runs database migrations. `pre_deploy_*` and `post_deploy_*` scripts under `scripts/db/migrate/` ship with the bundle (`scripts/**`) but are run by hand, before or after the deploy as their prefix says (see `scripts/db/CLAUDE.md`).

## Request path

| Hop | Config |
|---|---|
| Load balancer (ALB) | Listeners on the default port and on 443 (HTTPS, ACM certificate named in `00_ami.config`). Forwards to instances over HTTPS on 443. Health check: `/api/ping` (`HealthCheckPath` and `Application Healthcheck URL`) |
| Apache on the instance | `ProxyServer: apache`. `ssl.conf` listens on 443 with the self-signed cert and key, proxies `/` to `http://localhost:8000/`, and has a rewrite rule sending requests whose `X-Forwarded-Proto` isn't `https` to `https://` |
| Static files | EB serves `/assets` from `dist/static/assets` and `/favicon.ico` from `dist/static/favicon.ico` without hitting Flask |
| gunicorn (`Procfile`) | `gunicorn --bind 127.0.0.1:8000 --workers=6 --threads=5 --keep-alive=30 application` |
| Flask | `application.py` builds `application = create_app()` (`boac/factory.py`). Every non-API path returns `INDEX_HTML` (`dist/static/index.html`), which `register_routes` reads once at startup (`boac/routes.py`) |

The `_mod_wsgi` branches in `application.py` (copying the shell environment into `os.environ`) don't run under gunicorn.

## Configuration on servers

`load_configs` (`boac/configs.py`) loads, in order: `config/default.py`, `config/{BOAC_ENV}.py` if it exists, then `{BOAC_LOCAL_CONFIGS}/{BOAC_ENV}-local.py` (default directory `../config`, relative to the `boac` package, i.e. the repo's `config/`). `BOAC_ENV` defaults to `development`.

- On EB, `BOAC_ENV`, `EB_ENVIRONMENT`, and `EC2_INSTANCE_ID` are environment properties set in AWS, not in the repo. There is no `config/production.py`; per-environment values and secrets come only from the downloaded `config/production-local.py`, which `load_configs` picks up when `BOAC_ENV` is `production`.
- `EB_ENVIRONMENT` is appended to that file by the predeploy hook, so it becomes `app.config['EB_ENVIRONMENT']`. `GET /api/config` exposes it as `ebEnvironment`, and `os.environ['EC2_INSTANCE_ID']` as `ec2InstanceId`. `DismissibleFooterAlert.vue` uses `ebEnvironment` (minus its `boac-` prefix, upper-cased) in the screen-reader label of the `fixedWarningOnAllPages` footer.
- **Changing config without a redeploy.** Run `sudo scripts/deploy_boac_config.sh` on the instance. It reads `EB_ENVIRONMENT` from the current `production-local.py`, re-downloads that environment's file from the same S3 location, re-appends `EB_ENVIRONMENT`, and sets owner `webapp` and mode 400. Restart the app afterwards; it does not restart anything.
- Locally, `BOAC_LOCAL_CONFIGS` points at an encrypted volume holding `development-local.py` (`README.md`). Never read those files.

## Logs

| Log | Where | Shipped to |
|---|---|---|
| App log | `LOGGING_LOCATION = 'boa.log'` (`config/default.py`), relative to the working directory, so `/var/app/current/boa.log`. `RotatingFileHandler`, 100 MB × 20 backups (`boac/logger.py`). Default level `DEBUG`; `boto3`, `botocore`, `cas`, `s3transfer`, `werkzeug` at `INFO` | CloudWatch log group `/aws/elasticbeanstalk/<env>/var/app/current/boa.log`, one stream per instance ID; also in EB "bundle logs" (`02_logs.config`) |
| System logs | `/var/log/messages`, `/var/log/secure` | CloudWatch, `<instance-id>-messages` / `-secure` streams |
| EB platform logs | EB defaults | CloudWatch via `StreamLogs: true`; `DeleteOnTerminate: false` keeps them after an environment is terminated |
| Metrics | CPU, memory, disk, disk I/O, network | CloudWatch namespace `CWAgent`, by Auto Scaling group and instance |

Setting `LOGGING_LOCATION = 'STDOUT'` skips the file and uses Flask's handlers. Tests log to `boa-test.log` (`config/test.py`).

## CI (`.travis.yml`, `tox.ini`)

Travis (Ubuntu jammy, Python 3.11, PostgreSQL service): `nvm install 22`, `npm install`, `pip3 install tox`, create `boac_test` and `boac_loch_test` (same SQL as the root `CLAUDE.md`), `pip3 install -r requirements.txt`, then `tox --parallel`. That runs the whole `envlist`: `lint-py`, `lint-bea`, `lint-vue`, `build-vue`, `test`. `oxlint` and `lint-vue-fix` are tox envs but not in the list. Results go to Slack (encrypted token). CI does not deploy.

## Bumping versions: files that change together

| Bump | Files |
|---|---|
| Node | `.nvmrc` (exact version), `buildspec.yml` `runtime-versions.nodejs`, `.travis.yml` `nvm install`, root `CLAUDE.md` (mentions Node 22). `package.json` has no `engines` field |
| Python | `buildspec.yml` `runtime-versions.python`, `.travis.yml` `python`, `ruff.toml` `target-version`, `.python-version` (pyenv env name), `README.md`. The EB platform branch, which decides the server's Python, is chosen in AWS |
| PostgreSQL client | `.ebextensions/00_ami.config` `packages.yum` |
| Python packages | `requirements.txt` only (installed by EB on deploy and by Travis) |

## Gotchas

- **Build before start.** `INDEX_HTML` is read when routes are registered, so a missing `dist/static/index.html` breaks app startup, and a rebuilt frontend needs an app restart.
- **`/api/ping` returns 200 even when the DB is down** (see `data-refresh-and-terms.md`), so the EB health check only proves the process answers.
- **`gunicorn` is not in `requirements.txt`.** It comes from the EB Python platform.
- **Six worker processes.** In-process state isn't shared. A refresh-job thread runs inside whichever worker took the request.
- **Hooks must be executable.** EB runs `.platform/hooks/*` scripts directly, and CodeBuild only `chmod`s `scripts/*.sh`. The existing hooks are committed as mode 755; keep the execute bit when adding one (`git update-index --chmod=+x`).
- **Never put secrets in `.ebextensions` or `.platform`.** They ship in the public repo. Keys and per-environment config are pulled from S3 by the predeploy hooks.
- **`config/production-local.py` is mode 400, owned by `webapp`.** Read it with `sudo` on the instance; don't copy it off the box.
