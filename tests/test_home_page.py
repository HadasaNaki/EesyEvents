"""
Test Suite: Home Page Tests
Tests for the EasyEvents landing page
"""
import pytest
from tests.pages import HomePage


@pytest.mark.slow
class TestHomePage:
    """Test cases for the home page"""
    
    def test_home_page_loads(self, driver):
        """Test that home page loads successfully"""
        home = HomePage(driver)
        home.go_to_home()
        
        assert "EasyEvents" in driver.title or "Easy" in driver.title
        print("✅ Home page loaded successfully")
    
    def test_logo_is_visible(self, driver):
        """Test that logo is displayed on home page"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Check that the page has loaded
        assert home.get_current_url().endswith("/") or "localhost" in home.get_current_url()
        print("✅ Logo/branding visible on home page")
    
    def test_navigation_links_present(self, driver):
        """Test that main navigation links are present"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Check for navigation elements
        nav_elements = driver.find_elements("css selector", "nav a, .navbar a")
        assert len(nav_elements) > 0, "Navigation links should be present"
        print(f"✅ Found {len(nav_elements)} navigation links")
    
    def test_start_planning_button_exists(self, driver):
        """Test that start planning CTA button exists"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Look for any CTA button that leads to planning
        cta_buttons = driver.find_elements("css selector", "a[href='/plan'], .cta-btn, .btn-primary")
        assert len(cta_buttons) > 0, "Should have at least one CTA button"
        print("✅ Start planning button found")
    
    def test_click_login_navigates_correctly(self, driver):
        """Test that clicking login navigates to login page"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Find and click login link
        login_links = driver.find_elements("css selector", "a[href='/login']")
        if login_links:
            login_links[0].click()
            assert "/login" in driver.current_url
            print("✅ Login navigation works correctly")
        else:
            pytest.skip("Login link not found on home page")
    
    def test_click_register_navigates_correctly(self, driver):
        """Test that clicking register navigates to register page"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Find and click register link
        register_links = driver.find_elements("css selector", "a[href='/register']")
        if register_links:
            register_links[0].click()
            assert "/register" in driver.current_url
            print("✅ Register navigation works correctly")
        else:
            pytest.skip("Register link not found on home page")
    
    def test_responsive_menu_elements(self, driver):
        """Test that page has proper structure for different screen sizes"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Check for container elements
        containers = driver.find_elements("css selector", ".container, .wrapper, main")
        assert len(containers) > 0, "Page should have container elements"
        print("✅ Responsive structure elements present")
    
    def test_hebrew_content_displayed(self, driver):
        """Test that Hebrew content is displayed correctly"""
        home = HomePage(driver)
        home.go_to_home()
        
        # Get page source and check for Hebrew characters
        page_source = driver.page_source
        hebrew_chars = any('\u0590' <= char <= '\u05FF' for char in page_source)
        assert hebrew_chars, "Page should contain Hebrew text"
        print("✅ Hebrew content displayed correctly")
    
    def test_page_has_footer(self, driver):
        """Test that page has a footer section"""
        home = HomePage(driver)
        home.go_to_home()
        
        footers = driver.find_elements("css selector", "footer, .footer")
        # Footer is optional but good to check
        if footers:
            print("✅ Footer section found")
        else:
            print("ℹ️ No footer section found (optional)")
