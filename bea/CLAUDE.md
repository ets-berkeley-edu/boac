# bea/CLAUDE.md

BEA ("BOA's best friend") is BOA's browser automation test suite. Tests run locally against a live BOA instance using Selenium's Python API and Chromedriver (or Firefox/Safari).

## Running tests

```bash
# Interactive launcher (prompts for browser, headless mode, and test suite)
cd bea && ./bea.sh

# Direct pytest (from the bea/ directory)
USERNAME=<uid> PASSWORD=<password> pytest -vvv tests/test_note_mgmt.py --browser chrome --headless false

# Run a single test class
USERNAME=<uid> PASSWORD=<password> pytest -vvv tests/test_note_mgmt.py::TestNoteMgmt --browser chrome --headless false

# Headless
USERNAME=<uid> PASSWORD=<password> pytest -vvv tests/test_note_mgmt.py --browser chrome --headless true
```

Supported `--browser` values: `chrome`, `firefox`, `safari` (Safari is headless-incompatible).

## Configuration

`BOAC_ENV=bea` is set automatically by `conftest.py`. The active config file is `config/bea.py`. Local overrides go in a file pointed to by `BOAC_LOCAL_CONFIGS` (same pattern as the main app). Key settings:

| Setting | Purpose |
|---|---|
| `BASE_URL` | BOA instance under test (default: `https://boa-qa.berkeley.edu`) |
| `BROWSER` / `BROWSER_BINARY_PATH` | Browser selection and Chrome binary location |
| `BROWSER_HEADLESS` | Default headless flag (overridden by `--headless` CLI arg) |
| `TIMEOUT_SHORT/MEDIUM/LONG` | Selenium `WebDriverWait` timeouts (seconds) |
| `CLICK_SLEEP` | Sleep injected after clicks (seconds) |
| `TEST_DATA` | Path to `bea/fixtures/bea-test-data.json` |

## Architecture

### Layer overview

```
tests/          — pytest test files (one per feature area)
config/         — BEATestConfig / BEATestBaseConfigs: test data setup helpers
pages/          — Page Object Model: one class per page or page fragment
models/         — Plain data classes mirroring BOA domain objects
test_utils/     — Shared helpers (DB queries, Nessie data fetching, WebDriver setup)
fixtures/       — Static test data (JSON)
assets/         — Sample files used in attachment upload tests
```

### Page Object Model (`pages/`)

- `page.py` — `Page` base class: wraps Selenium `find_element`, `WebDriverWait`, `ActionChains`, etc.
- All page classes inherit from `Page` (and mix in domain-specific base classes like `BоaPages`, `StudentPageTimeline`).
- Locators are defined as class-level tuples: `FOO_BUTTON = (By.ID, 'foo-btn')`.
- Page classes never contain assertions; they expose action and query methods that tests call.

### Test structure (`tests/`)

- Each test file contains one pytest class.
- All page objects and the Selenium driver are injected via the session-scoped `page_objects` fixture defined in `conftest.py`. Tests access them as instance attributes (e.g., `self.student_page`, `self.driver`).
- Tests that iterate over many students/notes/etc. use parameterization built by `BEATestConfig` methods in `config/bea_test_config.py`.

### Test data setup (`config/`)

- `BEATestBaseConfigs` — base class with helpers like `set_base_configs()`, `set_test_students()`, `set_note_attachments()`.
- `BEATestConfig` — extends base with one method per test file (e.g., `note_mgmt()`, `filtered_cohorts()`). Each method populates `self.advisor`, `self.test_students`, `self.test_cases`, etc.
- `BEATestCase` — a single parameterized test case (student + optional note/appt/course).

### Utilities (`test_utils/`)

- `webdriver_manager.py` — `WebDriverManager.launch_browser()` / `quit_browser()`: creates the Chrome/Firefox/Safari driver with the right options.
- `boa_utils.py` — Queries the BOA PostgreSQL database directly (bypassing HTTP) to set up and verify state.
- `nessie_utils.py` / `nessie_timeline_utils.py` — Fetch student/enrollment/note/appointment data from the data loch (external data warehouse) for test verification.
- `utils.py` — Misc helpers: timeouts, download directory, term arithmetic, CSV parsing.

## Logging

Test output goes to `bea/bea.log` (`LOGGING_LOCATION` in `config/bea.py`).
