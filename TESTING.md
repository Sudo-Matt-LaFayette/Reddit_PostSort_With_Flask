# Testing Documentation

This document provides comprehensive information about testing the Reddit Post Sorter application.

## Test Framework

- **Framework**: pytest
- **UI Testing**: Selenium WebDriver
- **Browser**: Chrome (headless in CI, visible for local debugging)
- **Driver Management**: webdriver-manager (automatic ChromeDriver installation)

## Setup

### Install Testing Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:
- `pytest` - Test framework
- `selenium` - Browser automation
- `webdriver-manager` - Automatic driver management
- `pytest-html` - HTML test reports
- `coverage` - Code coverage analysis

### ChromeDriver

ChromeDriver is automatically downloaded and managed by `webdriver-manager`. No manual installation needed!

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_ui_basic.py

# Run specific test class
pytest tests/test_ui_basic.py::TestBasicUI

# Run specific test
pytest tests/test_ui_basic.py::TestBasicUI::test_homepage_loads
```

### Using the Test Runner Script

```bash
# Basic run
python run_tests.py

# Verbose output
python run_tests.py -v

# Run with visible browser (for debugging)
python run_tests.py --visible

# Generate HTML report
python run_tests.py --html

# Generate coverage report
python run_tests.py --coverage

# Stop on first failure
python run_tests.py -x

# Run specific file
python run_tests.py -f test_ui_basic.py

# Combine options
python run_tests.py -v --coverage --html
```

## Test Organization

### Test Files

- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_ui_basic.py` - Basic UI functionality tests

### Test Classes

1. **TestBasicUI** - Tests for basic page loading and navigation
2. **TestCategoryManagement** - Tests for category CRUD operations
3. **TestToggleFunctionality** - Tests for hide categorized posts toggle
4. **TestResponsiveDesign** - Tests for mobile/tablet viewports
5. **TestAccessibility** - Tests for accessibility compliance

## Fixtures

### Available Fixtures

```python
# Flask app with test configuration
test_app

# Running Flask server on port 5555
flask_server

# Adaptive Chrome driver (recommended - responds to --visible flag)
driver

# Legacy: Headless Chrome driver (deprecated - use 'driver' instead)
chrome_driver

# Legacy: Visible Chrome driver (deprecated - use 'driver' with --visible)
chrome_driver_visible
```

### Using Fixtures

The `driver` fixture automatically adapts based on the `--visible` command-line flag:

```python
def test_example(driver, flask_server):
    """Use the adaptive driver fixture (recommended)"""
    driver.get(flask_server)
    # Your test code here
```

**Run with headless browser (default):**
```bash
pytest tests/test_ui_basic.py
python run_tests.py
```

**Run with visible browser (for debugging):**
```bash
pytest tests/test_ui_basic.py --visible
python run_tests.py --visible
```

## Writing New Tests

### Basic Test Template

```python
def test_my_feature(driver, flask_server):
    """Test description"""
    driver.get(f"{flask_server}/my-page")
    
    # Find element
    element = driver.find_element(By.ID, "my-element")
    
    # Perform action
    element.click()
    
    # Assert result
    assert "Expected Text" in driver.page_source
```

### Using Waits

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_with_wait(driver, flask_server):
    driver.get(flask_server)
    
    # Wait for element to be visible
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.ID, "my-element"))
    )
    
    assert element.is_displayed()
```

## GitHub Actions CI/CD

### Workflow File

`.github/workflows/ui-tests.yml` - Automated testing on push and PRs

### What Gets Tested

- ✅ Multiple Python versions (3.9, 3.10, 3.11)
- ✅ All UI tests run in headless Chrome
- ✅ Test results uploaded as artifacts
- ✅ PR comments with test status

### Manual Trigger

You can manually trigger tests from GitHub:
1. Go to "Actions" tab
2. Select "UI Tests" workflow
3. Click "Run workflow"

### Viewing Results

- **In GitHub**: Actions tab → Select workflow run → View logs
- **Artifacts**: Download test results and coverage reports
- **PR Comments**: Automatic comments on pull requests with test status

## Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=. --cov-report=term tests/

# HTML report (opens in browser)
pytest --cov=. --cov-report=html tests/
# Then open htmlcov/index.html
```

### Coverage Goals

- Aim for 80%+ code coverage
- Focus on critical user paths
- Test edge cases and error handling

## Common Selectors

### By ID
```python
element = driver.find_element(By.ID, "element-id")
```

### By Class
```python
elements = driver.find_elements(By.CLASS_NAME, "my-class")
```

### By XPath
```python
button = driver.find_element(By.XPATH, "//button[text()='Click Me']")
```

### By CSS Selector
```python
link = driver.find_element(By.CSS_SELECTOR, "a.nav-link")
```

## Debugging Tests

### Run with Visible Browser

```bash
pytest tests/test_ui_basic.py --capture=no
```

Or use the visible fixture:
```python
def test_debug(chrome_driver_visible, flask_server):
    driver = chrome_driver_visible
    # Browser will be visible
```

### Add Breakpoints

```python
def test_with_breakpoint(chrome_driver, flask_server):
    driver = chrome_driver
    driver.get(flask_server)
    
    import pdb; pdb.set_trace()  # Debugger will pause here
    
    # Continue testing
```

### Take Screenshots

```python
def test_with_screenshot(chrome_driver, flask_server):
    driver = chrome_driver
    driver.get(flask_server)
    
    # Take screenshot on failure
    try:
        assert False  # This will fail
    except AssertionError:
        driver.save_screenshot("failure.png")
        raise
```

## Best Practices

1. **Use Explicit Waits** - Don't use `time.sleep()`, use WebDriverWait
2. **Independent Tests** - Each test should be able to run standalone
3. **Descriptive Names** - Test names should clearly describe what's being tested
4. **Clean Up** - Fixtures handle cleanup automatically
5. **Page Objects** - For complex tests, consider using Page Object pattern
6. **Atomic Tests** - Test one thing per test function
7. **Avoid Hardcoded Waits** - Use implicit waits or explicit waits instead

## Troubleshooting

### ChromeDriver Issues

If you get ChromeDriver errors:
```bash
# Update webdriver-manager cache
pip install --upgrade webdriver-manager
```

### Port Already in Use

If port 5555 is in use:
- Change port in `conftest.py`
- Or kill the process using the port

### Tests Hang

- Check if Flask server started properly
- Increase implicit wait timeout
- Add explicit waits for slow elements

### Import Errors

Make sure your PYTHONPATH includes the project root:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Future Test Ideas

- [ ] Test file upload functionality
- [ ] Test error handling and validation
- [ ] Test performance (page load times)
- [ ] Test with mock Reddit API data
- [ ] Visual regression testing with screenshots
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Load testing with multiple concurrent users

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

