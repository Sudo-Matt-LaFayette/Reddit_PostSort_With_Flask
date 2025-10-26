# 🚀 Quick Start: UI Testing

Get up and running with UI tests in 5 minutes!

## Step 1: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Activate the virtual environment:**

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
venv\Scripts\activate.bat
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

This installs pytest, Selenium, and other testing tools.

## Step 3: Run Your First Test

```bash
pytest tests/test_ui_basic.py -v
```

You should see tests running and passing! ✅

## Step 4: Run Tests with HTML Report

```bash
python run_tests.py --html
```

Open `test-report.html` in your browser to see a beautiful test report!

## Step 5: Debug with Visible Browser

Want to see what's happening?

```bash
python run_tests.py --visible
```

Chrome will open and you can watch the tests run!

## Step 6: Check Coverage

```bash
python run_tests.py --coverage
```

See which parts of your code are tested!

---

## Common Commands

```bash
# Run all tests
pytest tests/

# Run with visible browser (for debugging)
pytest tests/ --visible

# Run specific test
pytest tests/test_ui_basic.py::TestBasicUI::test_homepage_loads

# Run with coverage
pytest --cov=. tests/

# Stop on first failure
pytest -x tests/

# Show print statements
pytest -s tests/
```

---

## GitHub Actions Setup

Your tests will run automatically on every push! 🎉

1. Push your code to GitHub
2. Go to "Actions" tab
3. Watch tests run automatically
4. Get test results in PR comments

---

## Need Help?

Check out `TESTING.md` for comprehensive documentation!

---

## Quick Test Template

```python
def test_my_feature(driver, flask_server):
    """Test my awesome feature"""
    driver.get(flask_server)
    
    # Find element
    button = driver.find_element(By.ID, "my-button")
    
    # Click it
    button.click()
    
    # Check result
    assert "Success" in driver.page_source
```

**Tip:** Use `--visible` flag to see the browser in action while debugging!

Happy Testing! 🎉

