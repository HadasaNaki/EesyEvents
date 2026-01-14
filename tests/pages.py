"""
Page Object Model for EasyEvents pages
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from tests.conftest import BasePage
import time


class HomePage(BasePage):
    """Home page (landing page) object"""
    
    # Locators
    NAV_LOGO = (By.CSS_SELECTOR, ".nav-brand")
    LOGIN_BTN = (By.CSS_SELECTOR, "a[href='/login']")
    REGISTER_BTN = (By.CSS_SELECTOR, "a[href='/register']")
    START_PLANNING_BTN = (By.CSS_SELECTOR, "a[href='/plan']")
    HERO_TITLE = (By.CSS_SELECTOR, ".hero-title, h1")
    
    def go_to_home(self):
        """Navigate to home page"""
        self.navigate_to("/")
    
    def click_login(self):
        """Click login button"""
        self.wait_for_clickable(*self.LOGIN_BTN).click()
    
    def click_register(self):
        """Click register button"""
        self.wait_for_clickable(*self.REGISTER_BTN).click()
    
    def click_start_planning(self):
        """Click start planning button"""
        btn = self.wait_for_clickable(*self.START_PLANNING_BTN)
        self.scroll_to_element(btn)
        btn.click()
    
    def get_hero_title(self):
        """Get hero section title text"""
        return self.wait_for_element(*self.HERO_TITLE).text
    
    def is_logo_visible(self):
        """Check if logo is visible"""
        try:
            return self.wait_for_element(*self.NAV_LOGO).is_displayed()
        except:
            return False


class LoginPage(BasePage):
    """Login page object"""
    
    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message, .alert-error, .text-red-500")
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href='/register']")
    
    def go_to_login(self):
        """Navigate to login page"""
        self.navigate_to("/login")
    
    def enter_email(self, email):
        """Enter email"""
        self.wait_for_element(*self.EMAIL_INPUT).clear()
        self.driver.find_element(*self.EMAIL_INPUT).send_keys(email)
    
    def enter_password(self, password):
        """Enter password"""
        self.wait_for_element(*self.PASSWORD_INPUT).clear()
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
    
    def click_submit(self):
        """Click submit/login button"""
        self.wait_for_clickable(*self.SUBMIT_BTN).click()
    
    def login(self, email, password):
        """Complete login flow"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()
        time.sleep(1)
    
    def get_error_message(self):
        """Get error message if displayed"""
        try:
            return self.wait_for_element(*self.ERROR_MESSAGE, timeout=3).text
        except:
            return None
    
    def is_on_login_page(self):
        """Check if currently on login page"""
        return "/login" in self.get_current_url()


class RegisterPage(BasePage):
    """Registration page object"""
    
    # Locators
    FIRST_NAME_INPUT = (By.ID, "firstName")
    LAST_NAME_INPUT = (By.ID, "lastName")
    EMAIL_INPUT = (By.ID, "email")
    PHONE_INPUT = (By.ID, "phone")
    PASSWORD_INPUT = (By.ID, "password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "confirmPassword")
    NEWSLETTER_CHECKBOX = (By.NAME, "newsletter")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message, .alert-error, #error-message")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".success-message, .alert-success")
    
    def go_to_register(self):
        """Navigate to registration page"""
        self.navigate_to("/register")
    
    def fill_registration_form(self, first_name, last_name, email, phone, password, confirm_password, newsletter=False):
        """Fill all registration fields"""
        self.wait_for_element(*self.FIRST_NAME_INPUT).send_keys(first_name)
        self.driver.find_element(*self.LAST_NAME_INPUT).send_keys(last_name)
        self.driver.find_element(*self.EMAIL_INPUT).send_keys(email)
        self.driver.find_element(*self.PHONE_INPUT).send_keys(phone)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.CONFIRM_PASSWORD_INPUT).send_keys(confirm_password)
        
        if newsletter:
            checkbox = self.driver.find_element(*self.NEWSLETTER_CHECKBOX)
            if not checkbox.is_selected():
                checkbox.click()
    
    def click_submit(self):
        """Click submit button"""
        self.wait_for_clickable(*self.SUBMIT_BTN).click()
        time.sleep(1)
    
    def register(self, first_name, last_name, email, phone, password, confirm_password, newsletter=False):
        """Complete registration flow"""
        self.fill_registration_form(first_name, last_name, email, phone, password, confirm_password, newsletter)
        self.click_submit()


class PlanPage(BasePage):
    """Event planning page object"""
    
    # Locators
    EVENT_TYPE_CARDS = (By.CSS_SELECTOR, ".event-type-card, .category-card")
    WEDDING_CARD = (By.CSS_SELECTOR, "[data-type='wedding'], [onclick*='wedding']")
    BAR_MITZVAH_CARD = (By.CSS_SELECTOR, "[data-type='bar_mitzvah'], [onclick*='bar_mitzvah']")
    REGION_SELECT = (By.NAME, "region")
    GUESTS_INPUT = (By.NAME, "guests")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    
    def go_to_plan(self):
        """Navigate to planning page"""
        self.navigate_to("/plan")
    
    def select_event_type(self, event_type):
        """Select event type by clicking card"""
        card = self.wait_for_clickable(By.CSS_SELECTOR, f"[data-type='{event_type}'], [onclick*='{event_type}']")
        self.scroll_to_element(card)
        card.click()
    
    def get_event_type_cards_count(self):
        """Get number of event type cards"""
        cards = self.driver.find_elements(*self.EVENT_TYPE_CARDS)
        return len(cards)
    
    def enter_guests_count(self, count):
        """Enter number of guests"""
        input_field = self.wait_for_element(*self.GUESTS_INPUT)
        input_field.clear()
        input_field.send_keys(str(count))
    
    def select_region(self, region):
        """Select region from dropdown"""
        select = Select(self.wait_for_element(*self.REGION_SELECT))
        select.select_by_value(region)
    
    def submit_form(self):
        """Submit the planning form"""
        self.wait_for_clickable(*self.SUBMIT_BTN).click()
        time.sleep(1)


class ResultsPage(BasePage):
    """Results page object"""
    
    # Locators
    VENUE_CARDS = (By.CSS_SELECTOR, ".venue-card, .elegant-card.venue-card")
    SUPPLIER_CARDS = (By.CSS_SELECTOR, ".supplier-card, .elegant-card.supplier-card")
    FILTER_SUMMARY = (By.CSS_SELECTOR, ".filters-card, .results-summary")
    FILTER_TOGGLE_BTN = (By.CSS_SELECTOR, ".filter-toggle-btn")
    FILTERS_PANEL = (By.ID, "filtersPanel")
    HERO_TITLE = (By.CSS_SELECTOR, ".hero-title")
    CALL_BTN = (By.CSS_SELECTOR, "a[href^='tel:']")
    FAVORITE_BTN = (By.CSS_SELECTOR, ".favorite-btn")
    
    def go_to_results(self, event_type="", region="", guests=""):
        """Navigate to results page with filters"""
        params = []
        if event_type:
            params.append(f"event_type={event_type}")
        if region:
            params.append(f"region={region}")
        if guests:
            params.append(f"guests={guests}")
        
        query = "&".join(params)
        self.navigate_to(f"/results?{query}")
    
    def get_venue_count(self):
        """Get number of venue cards displayed"""
        time.sleep(0.5)
        venues = self.driver.find_elements(*self.VENUE_CARDS)
        return len(venues)
    
    def get_supplier_count(self):
        """Get number of supplier cards displayed"""
        suppliers = self.driver.find_elements(*self.SUPPLIER_CARDS)
        return len(suppliers)
    
    def is_filter_summary_visible(self):
        """Check if filter summary is visible"""
        try:
            return self.wait_for_element(*self.FILTER_SUMMARY).is_displayed()
        except:
            return False
    
    def toggle_filters(self):
        """Open/close filters panel"""
        btn = self.wait_for_clickable(*self.FILTER_TOGGLE_BTN)
        btn.click()
        time.sleep(0.5)
    
    def is_filters_panel_open(self):
        """Check if filters panel is open"""
        panel = self.driver.find_element(*self.FILTERS_PANEL)
        return "open" in panel.get_attribute("class")
    
    def click_first_favorite(self):
        """Click first favorite button"""
        btns = self.driver.find_elements(*self.FAVORITE_BTN)
        if btns:
            btns[0].click()
            return True
        return False
    
    def get_hero_title(self):
        """Get results page title"""
        return self.wait_for_element(*self.HERO_TITLE).text


class DashboardPage(BasePage):
    """User dashboard page object"""
    
    # Locators
    EVENT_CARDS = (By.CSS_SELECTOR, ".event-card")
    NEW_EVENT_BTN = (By.CSS_SELECTOR, "a[href='/plan']")
    USER_NAME = (By.CSS_SELECTOR, ".user-name, .welcome-message")
    LOGOUT_BTN = (By.CSS_SELECTOR, "a[href='/logout'], .logout-btn")
    
    def go_to_dashboard(self):
        """Navigate to dashboard"""
        self.navigate_to("/dashboard")
    
    def get_event_count(self):
        """Get number of events displayed"""
        events = self.driver.find_elements(*self.EVENT_CARDS)
        return len(events)
    
    def click_new_event(self):
        """Click to create new event"""
        self.wait_for_clickable(*self.NEW_EVENT_BTN).click()
    
    def is_logged_in(self):
        """Check if user appears to be logged in"""
        return "/dashboard" in self.get_current_url()
