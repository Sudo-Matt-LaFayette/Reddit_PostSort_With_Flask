"""
Basic UI tests for Reddit Post Sorter
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestBasicUI:
    """Test basic UI functionality"""
    
    def test_homepage_loads(self, driver, flask_server):
        """Test that the homepage loads successfully"""
        driver.get(flask_server)
        
        # Check page title
        assert "Reddit Post Sorter" in driver.title
        
        # Check main heading exists
        heading = driver.find_element(By.TAG_NAME, "h2")
        assert "Recent Saved Posts" in heading.text
    
    def test_navbar_elements(self, driver, flask_server):
        """Test that navbar contains all required elements"""
        driver.get(flask_server)
        
        # Check navbar brand
        navbar_brand = driver.find_element(By.CLASS_NAME, "navbar-brand")
        assert "Reddit Post Sorter" in navbar_brand.text
        
        # Check navigation links
        nav_links = driver.find_elements(By.CLASS_NAME, "nav-link")
        nav_text = [link.text for link in nav_links]
        
        assert "Home" in nav_text
        assert "All Posts" in nav_text
        assert "Categories" in nav_text
        assert "Fetch Saved Posts" in nav_text
    
    def test_categories_page_loads(self, driver, flask_server):
        """Test that categories page loads"""
        driver.get(f"{flask_server}/categories")
        
        # Check heading
        heading = driver.find_element(By.TAG_NAME, "h2")
        assert "Categories" in heading.text
        
        # Check create button exists
        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create Category')]")
        assert create_button is not None
    
    def test_all_posts_page_loads(self, driver, flask_server):
        """Test that all posts page loads"""
        driver.get(f"{flask_server}/posts")
        
        # Check heading
        heading = driver.find_element(By.TAG_NAME, "h2")
        assert "All Posts" in heading.text
        
        # Check filter elements exist
        filter_label = driver.find_element(By.XPATH, "//label[@for='category_id']")
        assert "Category" in filter_label.text


class TestCategoryManagement:
    """Test category creation and management"""
    
    def test_create_category_modal_opens(self, driver, flask_server):
        """Test that create category modal can be opened"""
        driver.get(f"{flask_server}/categories")
        
        # Wait for and click create category button (using CSS selector for Bootstrap modal trigger)
        wait = WebDriverWait(driver, 10)
        create_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#createCategoryModal']"))
        )
        create_button.click()
        
        # Wait for modal to appear
        modal = wait.until(EC.visibility_of_element_located((By.ID, "createCategoryModal")))
        
        assert modal.is_displayed()
        
        # Check form fields exist
        name_input = driver.find_element(By.ID, "name")
        color_input = driver.find_element(By.ID, "color")
        
        assert name_input is not None
        assert color_input is not None
    
    def test_create_category_form_validation(self, driver, flask_server):
        """Test that category form validates input"""
        driver.get(f"{flask_server}/categories")
        
        # Wait for and click create category button (using CSS selector for Bootstrap modal trigger)
        wait = WebDriverWait(driver, 10)
        create_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#createCategoryModal']"))
        )
        create_button.click()
        
        # Wait for modal to appear
        wait.until(EC.visibility_of_element_located((By.ID, "createCategoryModal")))
        
        # Try to submit empty form
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create Category') and @type='submit']")
        
        name_input = driver.find_element(By.ID, "name")
        
        # HTML5 validation should prevent submission
        assert name_input.get_attribute("required") is not None


class TestToggleFunctionality:
    """Test hide categorized posts toggle"""
    
    def test_hide_categorized_toggle_exists(self, driver, flask_server):
        """Test that hide categorized toggle exists on homepage"""
        driver.get(flask_server)
        
        # Check toggle exists
        toggle = driver.find_element(By.ID, "hideCategorizedToggle")
        assert toggle is not None
        
        # Check label exists
        label = driver.find_element(By.XPATH, "//label[@for='hideCategorizedToggle']")
        assert "Hide Categorized" in label.text
    
    def test_toggle_state_changes(self, driver, flask_server):
        """Test that toggle can be checked and unchecked"""
        driver.get(flask_server)
        
        toggle = driver.find_element(By.ID, "hideCategorizedToggle")
        
        # Initial state should be unchecked
        assert not toggle.is_selected()
        
        # Click to check
        toggle.click()
        time.sleep(0.5)  # Wait for animation
        
        assert toggle.is_selected()
        
        # Click to uncheck
        toggle.click()
        time.sleep(0.5)
        
        assert not toggle.is_selected()


class TestResponsiveDesign:
    """Test responsive design elements"""
    
    def test_mobile_viewport(self, driver, flask_server):
        """Test that site works on mobile viewport"""
        # Set mobile viewport
        driver.set_window_size(375, 667)  # iPhone size
        driver.get(flask_server)
        
        # Page should still load
        assert "Reddit Post Sorter" in driver.title
        
        # Navbar should exist
        navbar = driver.find_element(By.CLASS_NAME, "navbar")
        assert navbar is not None
    
    def test_tablet_viewport(self, driver, flask_server):
        """Test that site works on tablet viewport"""
        # Set tablet viewport
        driver.set_window_size(768, 1024)  # iPad size
        driver.get(flask_server)
        
        # Page should still load
        assert "Reddit Post Sorter" in driver.title


class TestAccessibility:
    """Test basic accessibility features"""
    
    def test_page_has_title(self, driver, flask_server):
        """Test that page has a title"""
        driver.get(flask_server)
        
        assert driver.title != ""
        assert len(driver.title) > 0
    
    def test_images_have_alt_text(self, driver, flask_server):
        """Test that images have alt text"""
        driver.get(flask_server)
        
        images = driver.find_elements(By.TAG_NAME, "img")
        
        for img in images:
            # Each image should have alt attribute
            alt = img.get_attribute("alt")
            assert alt is not None
    
    def test_forms_have_labels(self, driver, flask_server):
        """Test that form inputs have associated labels"""
        driver.get(f"{flask_server}/posts")
        
        # Check filter form
        category_select = driver.find_element(By.ID, "category_id")
        category_label = driver.find_element(By.XPATH, "//label[@for='category_id']")
        
        assert category_label is not None
        assert "Category" in category_label.text

