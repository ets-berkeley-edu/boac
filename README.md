# BOA

Berkeley Online Advising

![Airplane flying above the clouds](src/assets/boa-stratocruiser.jpg)

## Installation

* Install Python 3.8
* Create your virtual environment (venv)
* Install dependencies

```
pip3 install -r requirements.txt [--upgrade]
```

### Front-end dependencies

```
nvm use
npm install
```

### Create Postgres user and databases

```
createuser boac --no-createdb --no-superuser --no-createrole --pwprompt
createdb boac --owner=boac
createdb boac_test --owner=boac
createdb boac_loch_test --owner=boac

# Load schema
export FLASK_APP=application.py
flask initdb
```

### Create local configurations

If you plan to use any resources outside localhost, put your configurations in a separately encrypted area:

```
mkdir /Volumes/XYZ/boac_config
export BOAC_LOCAL_CONFIGS=/Volumes/XYZ/boac_config
```

## Run tests, lint the code

We use [Tox](https://tox.readthedocs.io) for continuous integration. Under the hood, you'll find [PyTest](https://docs.pytest.org), [Flake8](http://flake8.pycqa.org) and [ESLint](https://eslint.org/).
```
# Run all tests and linters with Tox's parallel mode:
tox -p

# Pytest
tox -e test

# Run specific test(s)
tox -e test -- tests/test_models/test_authorized_user.py

# Linters, à la carte
tox -e lint-py
tox -e lint-vue

# Auto-fix linting errors in Vue code
tox -e lint-vue-fix

# Lint specific file(s)
tox -e lint-py -- scripts/cohort_fixtures.py
```
