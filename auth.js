// ========================================
// EasyVents - User Authentication System
// Updated to work with Flask Backend API
// ========================================

const API_URL = 'http://localhost:5000/api';

// API Helper Functions
const API = {
    // Make POST request to API
    post: async function(endpoint, data) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            return { ...result, status: response.status };
        } catch (error) {
            console.error('API Error:', error);
            return {
                success: false,
                message: 'שגיאה בתקשורת עם השרת. אנא נסה שוב.',
                error: error.message
            };
        }
    },

    // Make GET request to API
    get: async function(endpoint) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            const result = await response.json();
            return { ...result, status: response.status };
        } catch (error) {
            console.error('API Error:', error);
            return {
                success: false,
                message: 'שגיאה בתקשורת עם השרת',
                error: error.message
            };
        }
    }
};

// Validation Functions
const Validation = {
    // Validate email format
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Validate password strength (at least 8 chars, contains letters and numbers)
    isValidPassword: function(password) {
        if (password.length < 8) {
            return { valid: false, message: 'הסיסמה חייבת להכיל לפחות 8 תווים' };
        }
        
        const hasLetter = /[a-zA-Z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        
        if (!hasLetter || !hasNumber) {
            return { valid: false, message: 'הסיסמה חייבת להכיל גם אותיות וגם מספרים' };
        }
        
        return { valid: true, message: '' };
    },

    // Validate phone number (Israeli format)
    isValidPhone: function(phone) {
        if (!phone) return true; // Phone is optional
        const phoneRegex = /^0[2-9]\d{7,8}$/;
        return phoneRegex.test(phone.replace(/[-\s]/g, ''));
    },

    // Validate required fields
    validateRequiredFields: function(fields) {
        for (let [key, value] of Object.entries(fields)) {
            if (!value || value.trim() === '') {
                return { valid: false, field: key };
            }
        }
        return { valid: true };
    }
};

// UI Helper Functions
const UI = {
    // Show error message
    showError: function(formId, message) {
        const form = document.getElementById(formId);
        let errorDiv = form.querySelector('.form-message.error');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'form-message error';
            form.insertBefore(errorDiv, form.firstChild);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    },

    // Show success message
    showSuccess: function(formId, message) {
        const form = document.getElementById(formId);
        let successDiv = form.querySelector('.form-message.success');
        
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.className = 'form-message success';
            form.insertBefore(successDiv, form.firstChild);
        }
        
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    },

    // Clear all messages
    clearMessages: function(formId) {
        const form = document.getElementById(formId);
        const messages = form.querySelectorAll('.form-message');
        messages.forEach(msg => msg.style.display = 'none');
    }
};

// Registration Handler
async function handleRegistration(event) {
    event.preventDefault();
    UI.clearMessages('registerForm');

    // Get form data
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const termsAccepted = document.getElementById('terms').checked;
    const newsletter = document.getElementById('newsletter').checked;

    // Validate required fields
    const requiredValidation = Validation.validateRequiredFields({
        'שם פרטי': firstName,
        'שם משפחה': lastName,
        'אימייל': email,
        'סיסמה': password,
        'אימות סיסמה': confirmPassword
    });

    if (!requiredValidation.valid) {
        UI.showError('registerForm', `השדה "${requiredValidation.field}" הוא חובה`);
        return;
    }

    // Validate email
    if (!Validation.isValidEmail(email)) {
        UI.showError('registerForm', 'כתובת האימייל אינה תקינה');
        return;
    }

    // Validate phone (if provided)
    if (phone && !Validation.isValidPhone(phone)) {
        UI.showError('registerForm', 'מספר הטלפון אינו תקין');
        return;
    }

    // Validate password strength
    const passwordValidation = Validation.isValidPassword(password);
    if (!passwordValidation.valid) {
        UI.showError('registerForm', passwordValidation.message);
        return;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        UI.showError('registerForm', 'הסיסמאות אינן תואמות');
        return;
    }

    // Check terms acceptance
    if (!termsAccepted) {
        UI.showError('registerForm', 'יש לאשר את תנאי השימוש');
        return;
    }

    // Send registration request to API
    const result = await API.post('/register', {
        firstName,
        lastName,
        email,
        phone,
        password,
        newsletter
    });

    if (result.success) {
        // Save user session
        sessionStorage.setItem('easyVentsCurrentUser', JSON.stringify(result.user));
        
        // Show success message
        UI.showSuccess('registerForm', '✅ ' + result.message);

        // Redirect to home page after 2 seconds
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    } else {
        UI.showError('registerForm', result.message);
        
        // Redirect to login if user exists
        if (result.redirect) {
            setTimeout(() => {
                window.location.href = result.redirect;
            }, 2000);
        }
    }
}

// Login Handler
async function handleLogin(event) {
    event.preventDefault();
    UI.clearMessages('loginForm');

    // Get form data
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;

    // Validate required fields
    if (!email || !password) {
        UI.showError('loginForm', 'נא למלא את כל השדות');
        return;
    }

    // Validate email format
    if (!Validation.isValidEmail(email)) {
        UI.showError('loginForm', 'כתובת האימייל אינה תקינה');
        return;
    }

    // Send login request to API
    const result = await API.post('/login', {
        email,
        password
    });

    if (result.success) {
        // Save user session
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem('easyVentsCurrentUser', JSON.stringify(result.user));
        
        // Show success message
        UI.showSuccess('loginForm', '✅ ' + result.message);

        // Redirect to home page after 1.5 seconds
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    } else {
        UI.showError('loginForm', result.message);
        
        // Redirect to register if user doesn't exist
        if (result.redirect) {
            setTimeout(() => {
                window.location.href = result.redirect;
            }, 2000);
        }
    }
}

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
        
        // Real-time password validation
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                const validation = Validation.isValidPassword(this.value);
                if (!validation.valid && this.value.length > 0) {
                    this.setCustomValidity(validation.message);
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', function() {
                if (this.value !== passwordInput.value && this.value.length > 0) {
                    this.setCustomValidity('הסיסמאות אינן תואמות');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    }

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

// Utility function to check if user is logged in
function isUserLoggedIn() {
    return localStorage.getItem('easyVentsCurrentUser') || sessionStorage.getItem('easyVentsCurrentUser');
}

// Utility function to get current user
function getCurrentUser() {
    const user = localStorage.getItem('easyVentsCurrentUser') || sessionStorage.getItem('easyVentsCurrentUser');
    return user ? JSON.parse(user) : null;
}

// Utility function to logout
function logout() {
    localStorage.removeItem('easyVentsCurrentUser');
    sessionStorage.removeItem('easyVentsCurrentUser');
    window.location.href = 'index.html';
}
