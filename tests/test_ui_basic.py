"""
Basic UI tests for Weather Station
"""
from selenium.webdriver.common.by import By


class TestDashboardUI:
    """Test dashboard rendering and core widgets"""

    def test_homepage_loads(self, driver, flask_server):
        """Test that the homepage loads successfully"""
        driver.get(flask_server)

        assert "Weather Station" in driver.title
        app_shell = driver.find_element(By.CLASS_NAME, "app-shell")
        assert app_shell is not None

    def test_current_conditions_present(self, driver, flask_server):
        """Test that current conditions block is visible"""
        driver.get(flask_server)

        current_card = driver.find_element(By.CLASS_NAME, "current-card")
        assert "Feels like" in current_card.text

        temp = driver.find_element(By.CLASS_NAME, "current-temp")
        assert temp.text.strip() != ""

    def test_daily_blocks_render(self, driver, flask_server):
        """Test that daily forecast blocks render"""
        driver.get(flask_server)

        daily_cards = driver.find_elements(By.CLASS_NAME, "daily-card")
        assert len(daily_cards) >= 5
        assert any("High" in card.text for card in daily_cards)

    def test_map_status_chip(self, driver, flask_server):
        """Test that Mapbox status chip renders"""
        driver.get(flask_server)

        chips = driver.find_elements(By.CLASS_NAME, "status-chip")
        assert any("Mapbox" in chip.text for chip in chips)


class TestResponsiveDesign:
    """Test responsive design elements"""

    def test_mobile_viewport(self, driver, flask_server):
        """Test that site works on mobile viewport"""
        driver.set_window_size(375, 667)
        driver.get(flask_server)

        assert "Weather Station" in driver.title
        map_panel = driver.find_element(By.CLASS_NAME, "map-panel")
        assert map_panel is not None

    def test_tablet_viewport(self, driver, flask_server):
        """Test that site works on tablet viewport"""
        driver.set_window_size(768, 1024)
        driver.get(flask_server)

        assert "Weather Station" in driver.title


class TestAccessibility:
    """Test basic accessibility features"""

    def test_page_has_title(self, driver, flask_server):
        """Test that page has a title"""
        driver.get(flask_server)

        assert driver.title
        assert len(driver.title) > 0

    def test_images_have_alt_text(self, driver, flask_server):
        """Test that images have alt text"""
        driver.get(flask_server)

        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt = img.get_attribute("alt")
            assert alt is not None

