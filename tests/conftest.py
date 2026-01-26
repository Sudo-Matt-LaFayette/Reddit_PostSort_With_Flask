"""
Pytest configuration and fixtures for UI testing.
"""
import os
import sys
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Force sample data to keep tests offline and stable.
os.environ.setdefault("WEATHER_USE_SAMPLE", "1")
os.environ.setdefault("DEFAULT_LOCATION", "Dallas, Texas")
os.environ.setdefault("DEFAULT_UNITS", "imperial")

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--visible",
        action="store_true",
        default=False,
        help="Run tests with visible browser (non-headless mode)",
    )


@pytest.fixture(scope="session")
def test_app():
    """Create and configure a test Flask app."""
    app.config["TESTING"] = True
    yield app


@pytest.fixture(scope="session")
def flask_server(test_app):
    """Start Flask server in a separate thread for UI testing."""

    def run_server():
        test_app.run(host="127.0.0.1", port=5555, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)

    yield "http://127.0.0.1:5555"


@pytest.fixture(scope="function")
def driver(request):
    """Setup Chrome WebDriver - adapts based on --visible flag."""
    visible = request.config.getoption("--visible")

    chrome_options = Options()
    if not visible:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


# Legacy fixtures for backward compatibility
@pytest.fixture(scope="function")
def chrome_driver(driver):
    """Legacy headless driver fixture (use 'driver' instead)."""
    return driver


@pytest.fixture(scope="function")
def chrome_driver_visible(request):
    """Legacy visible driver fixture (use 'driver' with --visible instead)."""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()
