# GitHub Actions Setup - Complete Guide

This document provides **comprehensive, step-by-step instructions** for setting up GitHub Actions CI/CD with Selenium UI testing. Use this as a reference for future projects.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Workflow File Explained](#workflow-file-explained)
6. [Testing Configuration](#testing-configuration)
7. [Local vs CI Environment](#local-vs-ci-environment)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)
10. [Replication Steps](#replication-steps)

---

## Overview

### What We're Building

A complete CI/CD pipeline that:
- ✅ Automatically runs UI tests on every push
- ✅ Tests across multiple Python versions
- ✅ Uses headless Chrome in CI environment
- ✅ Generates test reports and artifacts
- ✅ Comments on pull requests with results
- ✅ Can be manually triggered

### Technologies Used

- **GitHub Actions** - CI/CD platform
- **pytest** - Python testing framework
- **Selenium** - Browser automation
- **Chrome/ChromeDriver** - Browser for testing
- **webdriver-manager** - Automatic driver management

---

## Prerequisites

### Required Knowledge

- Basic Git/GitHub understanding
- Python virtual environments
- Command line basics
- Basic pytest knowledge (helpful but not required)

### Required Files in Your Project

```
your-project/
├── requirements.txt          # Main dependencies
├── requirements-dev.txt      # Testing dependencies
├── pytest.ini               # Pytest configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_*.py            # Test files
└── .github/
    └── workflows/
        └── ui-tests.yml     # GitHub Actions workflow
```

---

## Project Structure

### Directory Layout

```
Reddit Sort Python Flask/
│
├── .github/                          # GitHub-specific files
│   └── workflows/                    # GitHub Actions workflows
│       └── ui-tests.yml             # UI testing workflow ⭐
│
├── tests/                            # Test directory
│   ├── __init__.py                  # Makes tests a package
│   ├── conftest.py                  # Pytest configuration & fixtures ⭐
│   └── test_ui_basic.py             # Test files ⭐
│
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development/testing dependencies ⭐
├── pytest.ini                       # Pytest configuration ⭐
├── run_tests.py                     # Local test runner script
├── .gitignore                       # Git ignore patterns
│
├── app.py                           # Your Flask app
└── templates/                       # Your templates
```

**⭐ = Critical files for GitHub Actions**

---

## Step-by-Step Setup

### Step 1: Create Testing Dependencies File

**File:** `requirements-dev.txt`

```txt
# Testing Framework
pytest==7.4.3
pytest-flask==1.3.0

# Selenium & Browser Automation
selenium==4.15.2
webdriver-manager==4.0.1
pytest-selenium==4.0.1

# Test Reporting
pytest-html==4.1.1
coverage==7.3.2
pytest-cov==4.1.0

# Code Quality (optional)
black==23.11.0
flake8==6.1.0
```

**Why these packages?**
- `pytest` - Testing framework
- `selenium` - Browser automation
- `webdriver-manager` - Auto-downloads correct ChromeDriver version
- `pytest-html` - Generates HTML test reports
- `coverage`/`pytest-cov` - Code coverage analysis

---

### Step 2: Create Pytest Configuration

**File:** `pytest.ini`

```ini
[pytest]
# Test Discovery
testpaths = tests                    # Where to look for tests
python_files = test_*.py             # Test file naming pattern
python_classes = Test*               # Test class naming pattern
python_functions = test_*            # Test function naming pattern

# Output Configuration
addopts = 
    -v                               # Verbose output
    --tb=short                       # Short traceback format
    --strict-markers                 # Error on unknown markers
    --disable-warnings               # Cleaner output
    
# Custom Test Markers (optional)
markers =
    ui: UI tests using Selenium
    smoke: Quick smoke tests
    slow: Slower running tests
    integration: Integration tests
```

**Key Settings Explained:**
- `testpaths` - Tells pytest where to find tests
- `python_files` - Only files matching this pattern are considered tests
- `-v` - Verbose mode (shows each test name)
- `--tb=short` - Shorter error tracebacks (easier to read)
- `markers` - Custom tags for organizing tests

---

### Step 3: Create Pytest Fixtures

**File:** `tests/conftest.py`

This file contains **reusable test components** (fixtures):

```python
import pytest
import os
import sys
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

# ============================================
# FLASK APP FIXTURE
# ============================================
@pytest.fixture(scope="session")
def test_app():
    """
    Creates a test Flask application
    
    Scope: session (created once, shared across all tests)
    """
    # Configure for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_reddit_sorter.db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create test database
    with app.app_context():
        db.create_all()
        yield app
        
        # Cleanup after all tests
        db.session.remove()
        db.drop_all()
        
        if os.path.exists('test_reddit_sorter.db'):
            os.remove('test_reddit_sorter.db')

# ============================================
# FLASK SERVER FIXTURE
# ============================================
@pytest.fixture(scope="session")
def flask_server(test_app):
    """
    Starts Flask server in background thread
    
    Returns: Base URL (http://127.0.0.1:5555)
    """
    def run_server():
        test_app.run(
            host='127.0.0.1',
            port=5555,                    # Different port than dev (5000)
            debug=False,
            use_reloader=False            # CRITICAL: Must be False for threading
        )
    
    # Start server in daemon thread (dies when main thread exits)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield 'http://127.0.0.1:5555'

# ============================================
# CHROME DRIVER FIXTURE (HEADLESS)
# ============================================
@pytest.fixture(scope="function")
def chrome_driver():
    """
    Chrome WebDriver for CI/automated testing
    
    Scope: function (new driver for each test)
    Mode: Headless (no visible browser)
    """
    chrome_options = Options()
    
    # Headless mode (no GUI)
    chrome_options.add_argument("--headless")
    
    # Required for CI environments
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Set window size (important for responsive tests)
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Auto-download correct ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Implicit wait (waits up to 10s for elements)
    driver.implicitly_wait(10)
    
    yield driver
    
    # Cleanup
    driver.quit()

# ============================================
# CHROME DRIVER FIXTURE (VISIBLE)
# ============================================
@pytest.fixture(scope="function")
def chrome_driver_visible():
    """
    Chrome WebDriver for local debugging
    
    Mode: Visible (you can see the browser)
    """
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    driver.quit()
```

**Critical Concepts:**

1. **Fixture Scopes:**
   - `session` - Created once, shared by all tests
   - `function` - Created fresh for each test

2. **Why Threading?**
   - Flask server runs in background
   - Tests run in main thread
   - Server must be daemon thread (dies automatically)

3. **Why `use_reloader=False`?**
   - Flask's reloader conflicts with threading
   - Must be disabled in test environment

4. **Why webdriver-manager?**
   - Automatically downloads correct ChromeDriver version
   - No manual driver management needed
   - Works across different environments

---

### Step 4: Write Test Files

**File:** `tests/test_ui_basic.py`

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestBasicUI:
    """Basic UI tests"""
    
    def test_homepage_loads(self, chrome_driver, flask_server):
        """Test homepage loads successfully"""
        driver = chrome_driver
        driver.get(flask_server)  # flask_server = "http://127.0.0.1:5555"
        
        # Check title
        assert "Reddit Post Sorter" in driver.title
        
        # Check heading exists
        heading = driver.find_element(By.TAG_NAME, "h2")
        assert "Recent Saved Posts" in heading.text
```

**Test Function Requirements:**
- Must start with `test_`
- Takes fixtures as parameters
- Uses `assert` for verification

---

### Step 5: Create GitHub Actions Workflow

**File:** `.github/workflows/ui-tests.yml`

**CRITICAL: This is the main CI/CD configuration**

```yaml
name: UI Tests                              # Workflow name (shows in GitHub UI)

# ============================================
# TRIGGERS - When to run this workflow
# ============================================
on:
  push:
    branches: [ main, develop ]             # Run on pushes to these branches
  pull_request:
    branches: [ main ]                      # Run on PRs to main
  workflow_dispatch:                        # Allow manual trigger from UI

# ============================================
# JOBS - What to run
# ============================================
jobs:
  ui-tests:                                 # Job ID
    runs-on: ubuntu-latest                  # Run on Ubuntu (Linux)
    
    # ========================================
    # MATRIX STRATEGY - Test multiple versions
    # ========================================
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']  # Test on 3 Python versions
    
    # ========================================
    # STEPS - Individual tasks
    # ========================================
    steps:
    
    # STEP 1: Get the code
    - name: Checkout code
      uses: actions/checkout@v3             # Official GitHub action
    
    # STEP 2: Install Python
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4         # Official Python setup action
      with:
        python-version: ${{ matrix.python-version }}
    
    # STEP 3: Cache dependencies (speeds up builds)
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip                  # Where pip caches packages
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt', '**/requirements-dev.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    # STEP 4: Install Python dependencies
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    # STEP 5: Install Chrome browser
    - name: Install Chrome
      uses: browser-actions/setup-chrome@latest
      with:
        chrome-version: stable              # Use latest stable Chrome
    
    # STEP 6: Install ChromeDriver
    - name: Install ChromeDriver
      uses: nanasess/setup-chromedriver@master
    
    # STEP 7: Verify installations
    - name: Display Chrome version
      run: |
        google-chrome --version
        chromedriver --version
    
    # STEP 8: Run the tests
    - name: Run UI Tests
      run: |
        pytest tests/test_ui_basic.py -v --tb=short
      env:
        PYTHONPATH: ${{ github.workspace }}  # Set Python path to project root
    
    # STEP 9: Upload test results (runs even if tests fail)
    - name: Upload test results
      if: always()                          # CRITICAL: Run even on failure
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          pytest-results.xml
          htmlcov/
        retention-days: 30                  # Keep for 30 days
    
    # STEP 10: Comment on PR with results
    - name: Comment PR with test results
      if: github.event_name == 'pull_request' && always()
      uses: actions/github-script@v6
      with:
        script: |
          const output = `#### UI Tests 🧪
          - Python Version: \`${{ matrix.python-version }}\`
          - Status: \`${{ job.status }}\`
          
          *Automated by GitHub Actions*`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: output
          });
```

---

## Workflow File Explained

### Section 1: Triggers (`on`)

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
```

**What each trigger does:**
- `push` - Runs when code is pushed to specified branches
- `pull_request` - Runs when PR is created/updated
- `workflow_dispatch` - Adds "Run workflow" button in GitHub UI

### Section 2: Job Configuration

```yaml
runs-on: ubuntu-latest
```

**Runner options:**
- `ubuntu-latest` - Linux (most common, fastest)
- `windows-latest` - Windows
- `macos-latest` - macOS

**Why Ubuntu?**
- Fastest startup time
- Most GitHub Actions examples use it
- Best support for headless Chrome

### Section 3: Matrix Strategy

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

**What this does:**
- Creates 3 separate jobs
- Each runs with different Python version
- Ensures compatibility across versions

**Accessing matrix variables:**
```yaml
${{ matrix.python-version }}
```

### Section 4: Caching

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt', '**/requirements-dev.txt') }}
```

**Why cache?**
- Speeds up builds significantly
- Reuses downloaded packages if requirements unchanged
- `hashFiles()` creates unique key based on file contents

**Cache invalidation:**
- Automatically invalidates when requirements change
- Can manually clear from GitHub UI (Settings → Actions → Caches)

### Section 5: Critical Chrome Setup

```yaml
# Install Chrome
- name: Install Chrome
  uses: browser-actions/setup-chrome@latest

# Install ChromeDriver
- name: Install ChromeDriver
  uses: nanasess/setup-chromedriver@master
```

**Why both?**
- Chrome = Browser application
- ChromeDriver = WebDriver for Selenium to control Chrome

**Important:**
- Order matters: Install Chrome before ChromeDriver
- webdriver-manager can also handle ChromeDriver, but explicit installation is more reliable in CI

### Section 6: Environment Variables

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
```

**What is `github.workspace`?**
- Path to your repository on the runner
- Example: `/home/runner/work/reddit-post-sorter/reddit-post-sorter`

**Why set PYTHONPATH?**
- Ensures Python can import your modules
- Critical for `from app import ...` to work

### Section 7: Conditional Steps

```yaml
if: always()
```

**Conditions available:**
- `always()` - Run even if previous steps failed
- `success()` - Only run if all previous steps succeeded (default)
- `failure()` - Only run if any previous step failed
- `cancelled()` - Only run if workflow was cancelled

**Use case:**
- Upload test artifacts even if tests fail
- Send notifications on failure

---

## Testing Configuration

### Local Testing Setup

**Install dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Run tests:**
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_ui_basic.py

# Verbose output
pytest tests/ -v

# With HTML report
pytest tests/ --html=report.html
```

### CI Testing Setup

**Differences from local:**
1. Uses headless Chrome (`--headless` flag)
2. Runs in clean Ubuntu environment
3. No `.env` file (uses environment variables or mocks)
4. Different port for Flask (5555 vs 5000)

---

## Local vs CI Environment

### Key Differences

| Aspect | Local | CI (GitHub Actions) |
|--------|-------|---------------------|
| **OS** | Windows/Mac/Linux | Ubuntu Linux |
| **Browser** | Can be visible | Always headless |
| **Chrome** | System Chrome | Fresh install |
| **ChromeDriver** | System or cached | Fresh install |
| **Dependencies** | Virtual env | Fresh install |
| **Database** | May persist | Always fresh |
| **Environment** | `.env` file | GitHub Secrets |

### Making Tests Work in Both

**Use environment detection:**

```python
import os

# Check if running in CI
IS_CI = os.getenv('CI', 'false').lower() == 'true'

# Adjust timeouts
TIMEOUT = 5 if IS_CI else 10

# Adjust waits
driver.implicitly_wait(TIMEOUT)
```

**Handling environment variables:**

```python
# In CI, use GitHub Secrets
# Locally, use .env file

from dotenv import load_dotenv
load_dotenv()  # Only loads if .env exists

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'test_id')
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: ChromeDriver version mismatch

**Error:**
```
SessionNotCreatedException: Message: session not created: 
This version of ChromeDriver only supports Chrome version 119
```

**Solution:**
Use webdriver-manager (automatic):
```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

#### Issue 2: Tests pass locally but fail in CI

**Causes:**
1. Timing issues (CI is slower)
2. Different screen sizes
3. Missing dependencies

**Solutions:**
```python
# Increase waits in CI
from selenium.webdriver.support.ui import WebDriverWait
wait = WebDriverWait(driver, 20)  # Longer timeout

# Set consistent window size
chrome_options.add_argument("--window-size=1920,1080")

# Use explicit waits
wait.until(EC.element_to_be_clickable((By.ID, "button")))
```

#### Issue 3: Flask server doesn't start

**Error:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Solution:**
```python
# Increase sleep time
time.sleep(3)  # Wait longer for server

# Or use healthcheck
import requests
for _ in range(30):  # Try for 30 seconds
    try:
        requests.get('http://127.0.0.1:5555')
        break
    except:
        time.sleep(1)
```

#### Issue 4: Permission denied errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'chromedriver'
```

**Solution:**
```yaml
# In GitHub Actions, add:
- name: Set ChromeDriver permissions
  run: chmod +x $(which chromedriver)
```

#### Issue 5: Database locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```python
# Use separate test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.db'

# Cleanup after each test
@pytest.fixture(scope="function")
def clean_db(test_app):
    with test_app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with test_app.app_context():
        db.session.remove()
```

---

## Advanced Configuration

### Running Tests in Parallel

**Install:**
```bash
pip install pytest-xdist
```

**Run:**
```bash
pytest -n auto tests/  # Auto-detect CPU cores
```

**In GitHub Actions:**
```yaml
- name: Run UI Tests (Parallel)
  run: pytest -n 2 tests/  # Run with 2 workers
```

### Adding Test Coverage Requirements

**In pytest.ini:**
```ini
addopts = --cov=. --cov-fail-under=80
```

**In GitHub Actions:**
```yaml
- name: Check coverage
  run: |
    pytest --cov=. --cov-report=xml
    coverage report --fail-under=80
```

### Multiple Browser Testing

**Add Firefox:**
```yaml
matrix:
  browser: [chrome, firefox]
  python-version: ['3.9', '3.10', '3.11']

steps:
  - name: Setup Firefox
    if: matrix.browser == 'firefox'
    uses: browser-actions/setup-firefox@latest
```

### Scheduled Tests

**Run tests daily:**
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Every day at midnight UTC
```

---

## Replication Steps

### To Set This Up in a New Project

**Step 1: Create directory structure**
```bash
mkdir -p .github/workflows tests
touch .github/workflows/ui-tests.yml
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_ui_basic.py
touch pytest.ini
touch requirements-dev.txt
```

**Step 2: Copy files from this project**
1. Copy `.github/workflows/ui-tests.yml`
2. Copy `tests/conftest.py` (modify app import)
3. Copy `pytest.ini`
4. Copy `requirements-dev.txt`

**Step 3: Modify for your project**
```python
# In conftest.py, change:
from app import app, db
# To your app's import path

# Adjust ports if needed:
test_app.run(host='127.0.0.1', port=YOUR_PORT)
```

**Step 4: Write your first test**
```python
def test_homepage(chrome_driver, flask_server):
    driver = chrome_driver
    driver.get(flask_server)
    assert "Your App Name" in driver.title
```

**Step 5: Test locally**
```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

**Step 6: Push to GitHub**
```bash
git add .
git commit -m "Add GitHub Actions CI/CD"
git push
```

**Step 7: Watch it run**
- Go to GitHub repository
- Click "Actions" tab
- Watch your tests run!

---

## GitHub Secrets (For Sensitive Data)

### When to Use Secrets

- API keys
- Passwords
- Tokens
- Database URLs

### Adding Secrets

1. Go to repository Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `REDDIT_CLIENT_ID`
5. Value: Your actual client ID
6. Click "Add secret"

### Using Secrets in Workflow

```yaml
- name: Run tests
  env:
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_SECRET: ${{ secrets.REDDIT_SECRET }}
  run: pytest tests/
```

### Accessing in Python

```python
import os
client_id = os.getenv('REDDIT_CLIENT_ID')
```

---

## Monitoring and Notifications

### Email Notifications

GitHub automatically emails on:
- First failure of a workflow
- Failure of a workflow that previously succeeded

### Slack Notifications

```yaml
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Status Badges

Add to README.md:
```markdown
![UI Tests](https://github.com/username/repo/workflows/UI%20Tests/badge.svg)
```

---

## Best Practices Summary

✅ **DO:**
- Use matrix strategy for multiple Python versions
- Cache dependencies for faster builds
- Use `if: always()` for artifact uploads
- Set explicit Python path
- Use webdriver-manager for drivers
- Write clear test names
- Add comments to workflow file
- Test locally before pushing

❌ **DON'T:**
- Commit secrets to repository
- Use hardcoded passwords
- Skip cleanup steps
- Ignore test failures
- Use `time.sleep()` instead of explicit waits
- Test with only one Python version
- Forget to set PYTHONPATH

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [webdriver-manager Documentation](https://github.com/SergeyPirogov/webdriver_manager)

---

## Summary Checklist

Before committing your CI/CD setup:

- [ ] Created `.github/workflows/ui-tests.yml`
- [ ] Created `tests/conftest.py` with fixtures
- [ ] Created `tests/test_*.py` with actual tests
- [ ] Created `pytest.ini` configuration
- [ ] Created `requirements-dev.txt`
- [ ] Updated `.gitignore` for test artifacts
- [ ] Tested locally with `pytest`
- [ ] Verified Chrome/ChromeDriver setup
- [ ] Checked Python imports work
- [ ] Reviewed workflow triggers
- [ ] Added GitHub Secrets if needed
- [ ] Documented any project-specific configuration

---

**Last Updated:** October 14, 2025
**Author:** Development Team
**Project:** Reddit Post Sorter

*This document can be copied and adapted for any Python web application project requiring UI testing with GitHub Actions.*

