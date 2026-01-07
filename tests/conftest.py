"""
EasyEvents Selenium Test Configuration
Base setup for all Selenium tests
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Base URL for the application
BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="function")
def driver():
    """
    Create a Chrome WebDriver instance for each test function.
    Automatically handles driver setup and teardown.
    """
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    # Uncomment for headless mode:
    # chrome_options.add_argument("--headless")
    
    # Hebrew support
    chrome_options.add_argument("--lang=he")
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements
    
    yield driver
    
    # Cleanup
    driver.quit()


@pytest.fixture(scope="module")
def driver_module():
    """
    Create a Chrome WebDriver instance shared across test module.
    More efficient for related tests.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--lang=he")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


class BasePage:
    """Base class for Page Object Model"""
    
    def __init__(self, driver):
        self.driver = driver
        self.base_url = BASE_URL
    
    def navigate_to(self, path=""):
        """Navigate to a specific path"""
        self.driver.get(f"{self.base_url}{path}")
        time.sleep(0.5)  # Small delay for page load
    
    def get_title(self):
        """Get page title"""
        return self.driver.title
    
    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.3)
    
    def take_screenshot(self, name):
        """Take a screenshot"""
        self.driver.save_screenshot(f"tests/screenshots/{name}.png")
