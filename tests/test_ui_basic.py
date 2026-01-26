"""
Basic UI tests for the Flask Weather Station.
"""
from selenium.webdriver.common.by import By


class TestBasicUI:
    """Test basic UI functionality."""

    def test_homepage_loads(self, driver, flask_server):
        """Test that the homepage loads successfully."""
        driver.get(flask_server)

        assert "Weather" in driver.title
        dashboard = driver.find_element(By.CLASS_NAME, "dashboard")
        assert dashboard is not None

    def test_map_panel_present(self, driver, flask_server):
        """Test that the map panel and controls exist."""
        driver.get(flask_server)

        map_panel = driver.find_element(By.CLASS_NAME, "map-panel")
        assert map_panel is not None

        controls = driver.find_elements(By.CLASS_NAME, "map-control-button")
        assert len(controls) >= 2

    def test_location_form_fields(self, driver, flask_server):
        """Test that location form fields are present."""
        driver.get(flask_server)

        location_label = driver.find_element(By.XPATH, "//label[@for='location']")
        units_label = driver.find_element(By.XPATH, "//label[@for='units']")
        location_input = driver.find_element(By.ID, "location")
        units_select = driver.find_element(By.ID, "units")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        assert "Location" in location_label.text
        assert "Units" in units_label.text
        assert location_input is not None
        assert units_select is not None
        assert submit_button is not None

    def test_current_conditions_block(self, driver, flask_server):
        """Test that current conditions block renders."""
        driver.get(flask_server)

        current_block = driver.find_element(By.CLASS_NAME, "current-block")
        assert current_block is not None

        temp = driver.find_element(By.CLASS_NAME, "current-temp")
        condition = driver.find_element(By.CLASS_NAME, "current-condition")
        assert temp.text != ""
        assert condition.text != ""

    def test_daily_cards_present(self, driver, flask_server):
        """Test that daily forecast cards are rendered."""
        driver.get(flask_server)

        day_cards = driver.find_elements(By.CLASS_NAME, "day-card")
        assert len(day_cards) >= 7


class TestStatusAndAccessibility:
    """Test status banner and accessibility helpers."""

    def test_status_banner_present_in_sample_mode(self, driver, flask_server):
        """Sample mode should show a status banner."""
        driver.get(flask_server)

        banner = driver.find_element(By.CLASS_NAME, "status-banner")
        assert "sample" in banner.text.lower()

    def test_images_have_alt_text(self, driver, flask_server):
        """All images should have alt text."""
        driver.get(flask_server)

        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt = img.get_attribute("alt")
            assert alt is not None


class TestResponsiveDesign:
    """Test responsive design elements."""

    def test_mobile_viewport(self, driver, flask_server):
        """Test that site works on mobile viewport."""
        driver.set_window_size(375, 667)
        driver.get(flask_server)

        assert "Weather" in driver.title
        map_panel = driver.find_element(By.CLASS_NAME, "map-panel")
        assert map_panel is not None

    def test_tablet_viewport(self, driver, flask_server):
        """Test that site works on tablet viewport."""
        driver.set_window_size(768, 1024)
        driver.get(flask_server)

        assert "Weather" in driver.title
