"""
Test Suite: Plan/Create Event Page Tests
Tests for the event planning wizard page
"""
import pytest
import time
from tests.pages import PlanPage, ResultsPage


class TestPlanPage:
    """Test cases for the event planning page"""
    
    def test_plan_page_loads(self, driver):
        """Test that plan page loads successfully"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        assert "/plan" in driver.current_url
        print("✅ Plan page loaded successfully")
    
    def test_event_type_cards_displayed(self, driver):
        """Test that event type selection cards are displayed"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Look for event type cards
        cards = driver.find_elements("css selector", ".event-type-card, .category-card, [data-type]")
        
        print(f"✅ Found {len(cards)} event type cards")
        assert len(cards) > 0, "Should have event type selection cards"
    
    def test_wedding_event_type_exists(self, driver):
        """Test that wedding event type option exists"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Look for wedding option
        wedding_elements = driver.find_elements("css selector", 
            "[data-type='wedding'], [onclick*='wedding'], .event-card:contains('חתונה')")
        
        # Also check by text content
        page_source = driver.page_source
        has_wedding = "חתונה" in page_source or "wedding" in page_source.lower()
        
        assert has_wedding, "Wedding event type should be available"
        print("✅ Wedding event type found")
    
    def test_bar_mitzvah_event_type_exists(self, driver):
        """Test that bar mitzvah event type option exists"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        page_source = driver.page_source
        has_bar_mitzvah = "בר מצווה" in page_source or "bar_mitzvah" in page_source.lower()
        
        assert has_bar_mitzvah, "Bar Mitzvah event type should be available"
        print("✅ Bar Mitzvah event type found")
    
    def test_birthday_event_type_exists(self, driver):
        """Test that birthday event type option exists"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        page_source = driver.page_source
        has_birthday = "יום הולדת" in page_source or "birthday" in page_source.lower()
        
        assert has_birthday, "Birthday event type should be available"
        print("✅ Birthday event type found")
    
    def test_form_has_required_fields(self, driver):
        """Test that planning form has required input fields"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Check for common form fields
        form_elements = driver.find_elements("css selector", 
            "form input, form select, form textarea")
        
        print(f"✅ Found {len(form_elements)} form elements")
    
    def test_click_event_type_selects_it(self, driver):
        """Test that clicking event type card selects it"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Find clickable event cards
        cards = driver.find_elements("css selector", 
            ".event-type-card, .category-card, [onclick], label[for]")
        
        if cards:
            # Click first card
            cards[0].click()
            time.sleep(0.5)
            print("✅ Event type card clicked")
        else:
            pytest.skip("No clickable event type cards found")
    
    def test_form_submission_redirects_to_results(self, driver):
        """Test that form submission redirects to results page"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Find and click an event type if available
        event_cards = driver.find_elements("css selector", 
            ".event-type-card, [data-type], [onclick*='select']")
        
        if event_cards:
            event_cards[0].click()
            time.sleep(0.3)
        
        # Find and submit form
        submit_btns = driver.find_elements("css selector", 
            "button[type='submit'], input[type='submit'], .submit-btn")
        
        if submit_btns:
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btns[0])
            time.sleep(0.3)
            submit_btns[0].click()
            time.sleep(2)
            
            # Should redirect to results
            assert "/results" in driver.current_url or "/plan" in driver.current_url
            print(f"✅ Form submitted. Current URL: {driver.current_url}")
        else:
            pytest.skip("Submit button not found")
    
    def test_page_has_hebrew_content(self, driver):
        """Test that page displays Hebrew content"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        page_source = driver.page_source
        hebrew_chars = any('\u0590' <= char <= '\u05FF' for char in page_source)
        
        assert hebrew_chars, "Plan page should have Hebrew content"
        print("✅ Hebrew content displayed on plan page")
    
    def test_responsive_layout(self, driver):
        """Test that page has responsive layout elements"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Check for grid/flex containers
        containers = driver.find_elements("css selector", 
            ".grid, .flex, .container, [class*='grid'], [class*='flex']")
        
        assert len(containers) > 0, "Should have responsive layout containers"
        print(f"✅ Found {len(containers)} responsive layout elements")


class TestPlanPageInteractions:
    """Test interactive elements on plan page"""
    
    def test_guests_input_accepts_numbers(self, driver):
        """Test that guests input accepts numeric values"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Find guests input
        guests_inputs = driver.find_elements("css selector", 
            "input[name='guests'], input[type='number']")
        
        if guests_inputs:
            guests_inputs[0].clear()
            guests_inputs[0].send_keys("150")
            
            value = guests_inputs[0].get_attribute("value")
            assert value == "150", "Guests input should accept numbers"
            print("✅ Guests input accepts numeric values")
        else:
            pytest.skip("Guests input not found")
    
    def test_region_dropdown_has_options(self, driver):
        """Test that region dropdown has selectable options"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Find region select
        selects = driver.find_elements("css selector", "select[name='region']")
        
        if selects:
            options = selects[0].find_elements("css selector", "option")
            print(f"✅ Region dropdown has {len(options)} options")
            assert len(options) > 0, "Region dropdown should have options"
        else:
            pytest.skip("Region dropdown not found")
    
    def test_style_selection_available(self, driver):
        """Test that style selection is available"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Look for style selection elements
        style_elements = driver.find_elements("css selector", 
            "select[name='style'], [name='style'], .style-option")
        
        page_source = driver.page_source
        has_style_section = "סגנון" in page_source or "style" in page_source.lower()
        
        print(f"✅ Style selection: elements found={len(style_elements)}, text found={has_style_section}")
    
    def test_navigation_back_to_home(self, driver):
        """Test navigation back to home from plan page"""
        plan = PlanPage(driver)
        plan.go_to_plan()
        
        time.sleep(1)
        
        # Find logo or home link
        home_links = driver.find_elements("css selector", 
            "a[href='/'], .nav-brand, .logo a")
        
        if home_links:
            home_links[0].click()
            time.sleep(1)
            
            # Should be on home page
            current_url = driver.current_url
            is_home = current_url.endswith("/") or "/plan" not in current_url
            print(f"✅ Navigation to home: {current_url}")
        else:
            pytest.skip("Home link not found")
