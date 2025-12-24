"""
EasyVents - Backend API Server
Flask server for user authentication and management
"""

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'super_secret_key_for_easyevents_session'  # Required for Flask-Login
CORS(app)  # Enable CORS for all routes

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, '..', 'database', 'easyevents.db')

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, id, first_name, last_name, email, phone):
        self.id = str(id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
    
    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if not user:
            return None
        return User(user['id'], user['first_name'], user['last_name'], user['email'], user['phone'])

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def init_db():
    """Initialize the database with users table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            newsletter BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Initialize database on startup
init_db()

# Validation functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength (min 8 chars, contains letters and numbers)"""
    if len(password) < 8:
        return False, "הסיסמה חייבת להכיל לפחות 8 תווים"
    
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_number = bool(re.search(r'[0-9]', password))
    
    if not has_letter or not has_number:
        return False, "הסיסמה חייבת להכיל גם אותיות וגם מספרים"
    
    return True, ""

def validate_phone(phone):
    """Validate Israeli phone number"""
    if not phone:
        return True
    pattern = r'^0[2-9]\d{7,8}$'
    clean_phone = re.sub(r'[-\s]', '', phone)
    return re.match(pattern, clean_phone) is not None

# API Routes

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Extract data
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    newsletter = data.get('newsletter', False)
    
    # Validate required fields
    if not all([first_name, last_name, email, password]):
        return jsonify({
            'success': False,
            'message': 'כל השדות הנדרשים חייבים להיות מלאים'
        }), 400
    
    # Validate email
    if not validate_email(email):
        return jsonify({
            'success': False,
            'message': 'כתובת האימייל אינה תקינה'
        }), 400
    
    # Validate phone (if provided)
    if phone and not validate_phone(phone):
        return jsonify({
            'success': False,
            'message': 'מספר הטלפון אינו תקין'
        }), 400
    
    # Validate password
    valid, message = validate_password(password)
    if not valid:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    # Check if user already exists
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({
            'success': False,
            'message': 'משתמש עם אימייל זה כבר קיים במערכת',
            'redirect': 'login.html'
        }), 409
    
    # Hash password
    password_hash = generate_password_hash(password)
    
    # Insert new user
    try:
        conn.execute('''
            INSERT INTO users (first_name, last_name, email, phone, password_hash, newsletter)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, password_hash, newsletter))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'ההרשמה בוצעה בהצלחה!',
            'user': {
                'firstName': first_name,
                'lastName': last_name,
                'email': email
            }
        }), 201
        
    except Exception as e:
        conn.close()
        return jsonify({
            'success': False,
            'message': f'שגיאה בשמירת המשתמש: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    # Validate required fields
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'נא למלא את כל השדות'
        }), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({
            'success': False,
            'message': 'כתובת האימייל אינה תקינה'
        }), 400
    
    # Check if user exists
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({
            'success': False,
            'message': 'המשתמש אינו קיים במערכת. האם תרצה להירשם?',
            'redirect': 'register.html'
        }), 404
    
    # Verify password
    if not check_password_hash(user_data['password_hash'], password):
        return jsonify({
            'success': False,
            'message': 'הסיסמה שגויה. נסה שוב.'
        }), 401
    
    # Login successful
    user_obj = User(user_data['id'], user_data['first_name'], user_data['last_name'], user_data['email'], user_data['phone'])
    login_user(user_obj, remember=remember)

    return jsonify({
        'success': True,
        'message': f'שלום {user_data["first_name"]}! התחברת בהצלחה',
        'user': {
            'id': user_data['id'],
            'firstName': user_data['first_name'],
            'lastName': user_data['last_name'],
            'email': user_data['email'],
            'phone': user_data['phone']
        }
    }), 200

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'התנתקת בהצלחה'})

@app.route('/api/current_user', methods=['GET'])
def get_current_user_api():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'firstName': current_user.first_name,
                'lastName': current_user.last_name,
                'email': current_user.email
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/check_user', methods=['POST'])
def check_user():
    """Check if user exists by email"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'exists': False}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT email FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    return jsonify({'exists': user is not None})

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (for debugging - remove in production!)"""
    conn = get_db_connection()
    users = conn.execute('SELECT id, first_name, last_name, email, phone, created_at FROM users').fetchall()
    conn.close()
    
    return jsonify({
        'users': [dict(user) for user in users],
        'count': len(users)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    user_count = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    conn.close()
    
    return jsonify({
        'total_users': user_count,
        'database': DATABASE
    })

# Static routes for serving HTML pages
@app.route('/')
def index():
    """Serve the index page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Serve the login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Serve the register page"""
    return render_template('register.html')

@app.route('/plan')
def plan_page():
    """Serve the event planning/filtering page"""
    return render_template('plan.html')

if __name__ == '__main__':
    print("🚀 Starting EasyVents API Server...")
    print("📍 Server running on: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000")
    print("⚠️  Press CTRL+C to stop the server")
    app.run(debug=True, port=5000)
