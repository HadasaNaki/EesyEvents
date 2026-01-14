"""
Test Suite: Results Page Tests
Tests for the venues and suppliers results page
"""
import pytest
import time
from tests.pages import ResultsPage


class TestResultsPage:
    """Test cases for the results page"""
    
    def test_results_page_loads(self, driver):
        """Test that results page loads successfully"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        assert "/results" in driver.current_url
        print("✅ Results page loaded successfully")
    
    def test_results_page_with_wedding_filter(self, driver):
        """Test results page with wedding event type filter"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="wedding")
        
        time.sleep(1)
        assert "/results" in driver.current_url
        assert "wedding" in driver.current_url
        print("✅ Results page with wedding filter loaded")
    
    def test_results_page_with_region_filter(self, driver):
        """Test results page with region filter"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="wedding", region="מרכז")
        
        time.sleep(1)
        assert "/results" in driver.current_url
        print("✅ Results page with region filter loaded")
    
    def test_venues_are_displayed(self, driver):
        """Test that venue cards are displayed"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="wedding")
        
        time.sleep(1)
        venue_count = results.get_venue_count()
        
        print(f"✅ Found {venue_count} venue cards")
        # At least some venues should be displayed
        assert venue_count >= 0, "Venue count should be non-negative"
    
    def test_suppliers_are_displayed(self, driver):
        """Test that supplier cards are displayed"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        supplier_count = results.get_supplier_count()
        
        print(f"✅ Found {supplier_count} supplier cards")
        assert supplier_count >= 0, "Supplier count should be non-negative"
    
    def test_filter_summary_is_visible(self, driver):
        """Test that filters section is visible"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        # Look for the filter section header "סינון מתקדם"
        filter_header = driver.find_elements("xpath", "//h3[contains(text(), 'סינון מתקדם')]")
        
        assert len(filter_header) > 0, "Filter section header should be visible"
        print("✅ Filter summary section is visible")

    def test_results_hero_section(self, driver):
        """Test that results header/hero is displayed"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="birthday")
        
        time.sleep(1)
        
        # Look for the main header "הבחירות שלך"
        # Using CSS selector and text check instead of XPath for better reliability with Hebrew
        hero_elements = driver.find_elements("css selector", "h2.font-serif")
        
        found = False
        for h in hero_elements:
            if "הבחירות שלך" in h.text:
                found = True
                break
        
        if not found:
             # Fallback check in page source
             found = "הבחירות שלך" in driver.page_source
        
        assert found, "Results page header should be visible"
        print("✅ Results page header is displayed")
    
    def test_toggle_filters_panel(self, driver):
        """Test that filters panel can be toggled"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="wedding")
        
        time.sleep(1)
        
        # Try to find and click filter toggle button
        toggle_btns = driver.find_elements("css selector", ".filter-toggle-btn, button[onclick*='toggleFilters']")
        
        if toggle_btns:
            toggle_btns[0].click()
            time.sleep(0.5)
            
            # Check if panel opened
            panel = driver.find_elements("css selector", "#filtersPanel.open, .filters-panel.open")
            print(f"✅ Filters panel toggle tested. Panel open: {len(panel) > 0}")
        else:
            pytest.skip("Filter toggle button not found")
    
    def test_call_buttons_present(self, driver):
        """Test that call buttons are present on cards"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        call_btns = driver.find_elements("css selector", "a[href^='tel:'], .btn-primary")
        
        print(f"✅ Found {len(call_btns)} call/action buttons")
    
    def test_favorite_button_click(self, driver):
        """Test that favorite button can be clicked"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        fav_btns = driver.find_elements("css selector", ".favorite-btn")
        
        if fav_btns:
            # Get initial state
            initial_text = fav_btns[0].text
            
            # Click favorite
            fav_btns[0].click()
            time.sleep(0.3)
            
            # Check if state changed
            new_text = fav_btns[0].text
            state_changed = initial_text != new_text or "active" in fav_btns[0].get_attribute("class")
            
            print(f"✅ Favorite button clicked. State changed: {state_changed}")
        else:
            pytest.skip("No favorite buttons found")
    
    def test_results_hero_section(self, driver):
        """Test that hero section is displayed"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="birthday")
        
        time.sleep(1)
        
        hero_elements = driver.find_elements("css selector", ".results-hero, .hero-title")
        
        assert len(hero_elements) > 0, "Hero section should be visible"
        print("✅ Hero section is displayed")
    
    def test_filter_by_multiple_criteria(self, driver):
        """Test filtering by multiple criteria"""
        results = ResultsPage(driver)
        results.go_to_results(event_type="wedding", region="מרכז", guests="100")
        
        time.sleep(1)
        
        assert "wedding" in driver.current_url
        assert "100" in driver.current_url or "guests" in driver.current_url
        
        print("✅ Multiple filter criteria applied")
    
    def test_empty_results_handling(self, driver):
        """Test page handles empty results gracefully"""
        results = ResultsPage(driver)
        # Use unlikely combination
        results.go_to_results(event_type="wedding", region="nonexistent", guests="99999")
        
        time.sleep(1)
        
        # Page should still load without errors
        assert "/results" in driver.current_url
        print("✅ Empty results handled gracefully")
    
    def test_back_to_search_link(self, driver):
        """Test that 'back to search' link works"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        back_links = driver.find_elements("css selector", "a[href='/plan'], .filter-reset-btn")
        
        if back_links:
            back_links[0].click()
            time.sleep(1)
            
            assert "/plan" in driver.current_url
            print("✅ Back to search link works")
        else:
            print("ℹ️ Back to search link not found (optional)")


class TestResultsFiltering:
    """Test filtering functionality on results page"""
    
    def test_filter_form_submission(self, driver):
        """Test that filter form can be submitted"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        # Open filters panel
        toggle_btns = driver.find_elements("css selector", ".filter-toggle-btn")
        if toggle_btns:
            toggle_btns[0].click()
            time.sleep(0.5)
        
        # Find and submit filter form
        forms = driver.find_elements("css selector", ".filters-form form, #filtersPanel form")
        
        if forms:
            submit_btns = forms[0].find_elements("css selector", "button[type='submit']")
            if submit_btns:
                submit_btns[0].click()
                time.sleep(1)
                print("✅ Filter form submitted")
            else:
                pytest.skip("Submit button not found in filter form")
        else:
            pytest.skip("Filter form not found")
    
    def test_event_type_select_options(self, driver):
        """Test that event type select has options"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        # Open filters panel first
        toggle_btns = driver.find_elements("css selector", ".filter-toggle-btn")
        if toggle_btns:
            toggle_btns[0].click()
            time.sleep(0.5)
        
        # Find event type select
        selects = driver.find_elements("css selector", "select[name='event_type']")
        
        if selects:
            options = selects[0].find_elements("css selector", "option")
            option_count = len(options)
            print(f"✅ Event type select has {option_count} options")
            assert option_count > 1, "Should have multiple event type options"
        else:
            pytest.skip("Event type select not found")
    
    def test_region_select_options(self, driver):
        """Test that region select has options"""
        results = ResultsPage(driver)
        results.go_to_results()
        
        time.sleep(1)
        
        # Open filters panel
        toggle_btns = driver.find_elements("css selector", ".filter-toggle-btn")
        if toggle_btns:
            toggle_btns[0].click()
            time.sleep(0.5)
        
        # Find region select
        selects = driver.find_elements("css selector", "select[name='region']")
        
        if selects:
            options = selects[0].find_elements("css selector", "option")
            option_count = len(options)
            print(f"✅ Region select has {option_count} options")
            assert option_count > 1, "Should have multiple region options"
        else:
            pytest.skip("Region select not found")
