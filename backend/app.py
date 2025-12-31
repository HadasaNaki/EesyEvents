"""
EasyVents - Backend API Server
Flask server for user authentication and management
"""

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, flash
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
    """Create a database connection with timeout to prevent locking"""
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')  # Better concurrency
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
    """Initialize the database with users and events tables"""
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

    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            date TEXT,
            time_of_day TEXT,
            venue_type TEXT,
            style TEXT,
            region TEXT,
            budget TEXT,
            guests INTEGER,
            status TEXT DEFAULT 'planning',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id)
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

@app.route('/create_event', methods=['POST'])
def create_event():
    """Handle event creation from plan page"""
    # Get form data
    data = request.form.to_dict(flat=False) # Get lists for all fields

    # Process data for DB
    event_type = data.get('event_type', [None])[0]
    date = data.get('date', [None])[0]
    time_of_day = data.get('time_of_day', [None])[0]
    venue_type = data.get('venue_type', [None])[0]
    style = data.get('style', [None])[0]
    budget = data.get('budget', [None])[0]
    guests = data.get('guests', [None])[0]

    # Handle region (could be multiple)
    regions = data.get('region', [])
    region_str = ','.join(regions) if regions else None

    # If no event_type selected, default to 'other'
    if not event_type:
        event_type = 'other'

    if not current_user.is_authenticated:
        # If not logged in, just redirect to results with the args
        # We flatten the dict for url_for, but keep lists if needed?
        # url_for handles lists by repeating keys, which is what we want for GET params
        return redirect(url_for('results_page', **request.form))

    # If logged in, save the event
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO events (
            user_id, event_type, date, time_of_day,
            venue_type, style, region, budget, guests
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_user.id,
        event_type,
        date,
        time_of_day,
        venue_type,
        style,
        region_str,
        budget,
        guests
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('results_page', **request.form))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their events"""
    conn = get_db_connection()
    events = conn.execute('''
        SELECT * FROM events
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (current_user.id,)).fetchall()
    conn.close()

    return render_template('dashboard.html', events=events)

@app.route('/api/event/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    """Update event details"""
    data = request.get_json()
    
    conn = get_db_connection()
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Build update query dynamically based on provided fields
    allowed_fields = ['event_type', 'date', 'time_of_day', 'venue_type', 'style', 'region', 'budget', 'guests', 'status']
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            updates.append(f'{field} = ?')
            values.append(data[field])
    
    if updates:
        values.append(event_id)
        query = f'UPDATE events SET {", ".join(updates)} WHERE id = ?'
        conn.execute(query, values)
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/api/event/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete an event"""
    conn = get_db_connection()
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete checklist items first
    conn.execute('DELETE FROM checklist_items WHERE event_id = ?', (event_id,))
    # Delete event
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/event/<int:event_id>/manage')
@login_required
def manage_event(event_id):
    """Event management page with checklist"""
    conn = get_db_connection()

    # Get event and verify ownership
    event = conn.execute('SELECT * FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()

    if not event:
        conn.close()
        return redirect(url_for('dashboard'))

    # Get checklist items
    checklist_items = conn.execute('''
        SELECT * FROM checklist_items
        WHERE event_id = ?
        ORDER BY is_completed ASC, created_at DESC
    ''', (event_id,)).fetchall()

    # Calculate progress
    total_count = len(checklist_items)
    completed_count = sum(1 for item in checklist_items if item['is_completed'])

    conn.close()

    return render_template('manage_event.html',
                         event=event,
                         checklist_items=checklist_items,
                         total_count=total_count,
                         completed_count=completed_count)

# API Endpoints for Checklist
@app.route('/api/event/<int:event_id>/checklist', methods=['POST'])
@login_required
def add_checklist_item(event_id):
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db_connection()
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403

    conn.execute('INSERT INTO checklist_items (event_id, title) VALUES (?, ?)',
                (event_id, title))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/checklist/<int:item_id>', methods=['PUT'])
@login_required
def update_checklist_item(item_id):
    data = request.get_json()
    is_completed = data.get('is_completed')

    conn = get_db_connection()
    # Verify ownership via join
    item = conn.execute('''
        SELECT i.id FROM checklist_items i
        JOIN events e ON i.event_id = e.id
        WHERE i.id = ? AND e.user_id = ?
    ''', (item_id, current_user.id)).fetchone()

    if not item:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403

    conn.execute('UPDATE checklist_items SET is_completed = ? WHERE id = ?',
                (1 if is_completed else 0, item_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/checklist/<int:item_id>', methods=['DELETE'])
@login_required
def delete_checklist_item(item_id):
    conn = get_db_connection()
    # Verify ownership via join
    item = conn.execute('''
        SELECT i.id FROM checklist_items i
        JOIN events e ON i.event_id = e.id
        WHERE i.id = ? AND e.user_id = ?
    ''', (item_id, current_user.id)).fetchone()

    if not item:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403

    conn.execute('DELETE FROM checklist_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

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

@app.route('/results')
def results_page():
    """Serve the results page"""
    return render_template('results.html')

if __name__ == '__main__':
    print("🚀 Starting EasyVents API Server...")
    print("📍 Server running on: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000")
    print("⚠️  Press CTRL+C to stop the server")
    app.run(debug=True, port=5000)
