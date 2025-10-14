"""
Pytest configuration and fixtures for UI testing
"""
import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

@pytest.fixture(scope="session")
def test_app():
    """Create and configure a test Flask app"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_reddit_sorter.db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        
        # Clean up test database
        if os.path.exists('test_reddit_sorter.db'):
            os.remove('test_reddit_sorter.db')

@pytest.fixture(scope="session")
def flask_server(test_app):
    """Start Flask server in a separate thread for UI testing"""
    def run_server():
        test_app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield 'http://127.0.0.1:5555'
    
    # Server will stop when main thread exits (daemon=True)

@pytest.fixture(scope="function")
def chrome_driver():
    """Setup Chrome WebDriver for UI testing"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for CI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Use webdriver-manager to automatically download correct chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def chrome_driver_visible():
    """Setup visible Chrome WebDriver for local testing/debugging"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

