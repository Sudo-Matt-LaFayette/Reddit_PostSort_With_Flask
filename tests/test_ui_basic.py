"""
Basic UI tests for Flask Weather Station
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBasicUI:
    """Test basic UI functionality"""

    def test_homepage_loads(self, driver, flask_server):
        """Test that the homepage loads successfully"""
        driver.get(flask_server)

        assert "Weather Station" in driver.title

        map_panel = driver.find_element(By.ID, "map")
        info_panel = driver.find_element(By.ID, "info-panel")

        assert map_panel is not None
        assert info_panel is not None

    def test_clock_and_location_present(self, driver, flask_server):
        """Test that clock and location elements render"""
        driver.get(flask_server)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-role='clock-time']")))

        clock_time = driver.find_element(By.CSS_SELECTOR, "[data-role='clock-time']")
        location_name = driver.find_element(By.CSS_SELECTOR, "[data-role='location-name']")

        assert clock_time is not None
        assert location_name is not None

    def test_current_weather_section(self, driver, flask_server):
        """Test that current weather section includes key stats"""
        driver.get(flask_server)

        current_temp = driver.find_element(By.CSS_SELECTOR, "[data-role='current-temp']")
        current_condition = driver.find_element(By.CSS_SELECTOR, "[data-role='current-condition']")
        current_wind = driver.find_element(By.CSS_SELECTOR, "[data-role='current-wind']")

        assert current_temp is not None
        assert current_condition is not None
        assert current_wind is not None


class TestForecastBlocks:
    """Test daily forecast blocks"""

    def test_daily_forecast_blocks_exist(self, driver, flask_server):
        """Ensure daily forecast blocks render"""
        driver.get(flask_server)

        blocks = driver.find_elements(By.CLASS_NAME, "forecast-card")
        assert len(blocks) >= 7

    def test_daily_forecast_block_contents(self, driver, flask_server):
        """Each forecast block should include day, temps, and sun times"""
        driver.get(flask_server)

        blocks = driver.find_elements(By.CLASS_NAME, "forecast-card")
        assert blocks

        sample_block = blocks[0]
        day = sample_block.find_element(By.CLASS_NAME, "forecast-day")
        temps = sample_block.find_elements(By.CSS_SELECTOR, ".forecast-temp span")
        sun = sample_block.find_element(By.CLASS_NAME, "forecast-sun")

        assert day.text != ""
        assert len(temps) >= 2
        assert sun.text != ""


class TestControlsAndHints:
    """Test control buttons and map hints"""

    def test_control_buttons_exist(self, driver, flask_server):
        """Control buttons should render with aria-labels"""
        driver.get(flask_server)

        buttons = driver.find_elements(By.CLASS_NAME, "control-button")
        assert len(buttons) >= 3

        for button in buttons:
            assert button.get_attribute("aria-label")

    def test_map_hint_exists(self, driver, flask_server):
        """Map hint text should be visible"""
        driver.get(flask_server)

        hint = driver.find_element(By.CLASS_NAME, "map-hint")
        assert "Click the map" in hint.text


class TestResponsiveDesign:
    """Test responsive design elements"""

    def test_mobile_viewport(self, driver, flask_server):
        """Test that site works on mobile viewport"""
        driver.set_window_size(375, 667)
        driver.get(flask_server)

        assert "Weather Station" in driver.title

        map_panel = driver.find_element(By.ID, "map")
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

        assert driver.title != ""

    def test_buttons_have_labels(self, driver, flask_server):
        """Ensure control buttons have aria-labels"""
        driver.get(flask_server)

        buttons = driver.find_elements(By.CLASS_NAME, "control-button")
        for button in buttons:
            assert button.get_attribute("aria-label")
