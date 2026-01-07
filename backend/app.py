"""
EasyVents - Backend API Server
Flask server for user authentication and management
"""

from flask import Flask, request, jsonify, send_from_directory, render_template, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import glob
from image_manager import init_image_manager

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'super_secret_key_for_easyevents_session'  # Required for Flask-Login
CORS(app)  # Enable CORS for all routes

# Configure Database Path (Absolute Path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'easyevents.db')

# Use forward slashes for Windows compatibility in URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH.replace('\\', '/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Image Manager
image_manager = init_image_manager(os.path.join(BASE_DIR, 'static', 'images'))

# --- LOCAL IMAGE MANAGEMENT ---
def get_local_venue_image(venue_obj):
    """
    Get a local image for a venue based on its type.
    
    Args:
        venue_obj: Venue object with 'id' and 'style' attributes
        
    Returns:
        Relative path like '/static/images/hall/hall3.jpg'
        Defaults to '/static/images/hall/hall1.jpg' if no images found
    """
    # Determine folder based on style and name
    style_lower = venue_obj.style.lower() if venue_obj.style else ''
    name_lower = venue_obj.name.lower() if venue_obj.name else ''
    
    # Smart mapping: check style and name for clues
    folder = 'hall'  # default
    
    # Pool venues
    if 'pool' in style_lower or 'villa' in style_lower or 'בריכ' in name_lower or 'וילה' in name_lower:
        folder = 'pool'
    # Wedding venues
    elif 'wedding' in style_lower or 'boho' in style_lower or 'חתונ' in name_lower or 'גן' in name_lower:
        folder = 'wedding'
    # Hall venues (default)
    elif 'luxury' in style_lower or 'modern' in style_lower or 'rustic' in style_lower or 'hall' in style_lower or 'אולמ' in name_lower:
        folder = 'hall'
    
    images_dir = os.path.join(BASE_DIR, 'static', 'images', folder)
    
    # Find all images in the folder
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    images = []
    for ext in image_extensions:
        images.extend(glob.glob(os.path.join(images_dir, ext)))
        images.extend(glob.glob(os.path.join(images_dir, ext.upper())))
    
    if not images:
        # Fallback to hall folder if no images found
        images_dir = os.path.join(BASE_DIR, 'static', 'images', 'hall')
        for ext in image_extensions:
            images.extend(glob.glob(os.path.join(images_dir, ext)))
            images.extend(glob.glob(os.path.join(images_dir, ext.upper())))
    
    if not images:
        # Ultimate fallback
        return '/static/images/hall/hall1.jpg'
    
    # Select deterministically based on venue ID
    image_index = (venue_obj.id - 1) % len(images)
    selected_image = images[image_index]
    
    # Convert to relative path
    relative_path = selected_image.replace(BASE_DIR, '').replace('\\', '/')
    if relative_path.startswith('/'):
        return relative_path
    return '/' + relative_path

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200))

    style = db.Column(db.String(50))
    is_open_air = db.Column(db.Boolean, default=False)

    price = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return f"<Venue {self.name} in {self.city}>"
class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)      # Supplier name
    supplier_type = db.Column(db.String(50), nullable=False)
    # Examples: DJ, Catering, Designer, Photographer

    phone = db.Column(db.String(20))                      # Contact phone
    city = db.Column(db.String(60))                       # Service area / city
    price = db.Column(db.Integer)                         # Starting price / average price
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return f"<Supplier {self.name} ({self.supplier_type})>"


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
    """Initialize the database with users, events and event_vendors tables"""
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
            event_type TEXT,
            date TEXT,
            time_of_day TEXT,
            venue_type TEXT,
            style TEXT,
            region TEXT,
            budget TEXT,
            guests INTEGER,
            status TEXT DEFAULT 'תכנון',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            vendor_type TEXT NOT NULL,
            vendor_id INTEGER NOT NULL,
            vendor_name TEXT,
            vendor_price INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Initialize database on startup
init_db()

# --- IMAGE MANAGER API ---
@app.route('/api/images/manifest', methods=['GET'])
def get_image_manifest():
    """Get complete image manifest for all categories"""
    try:
        manifest = image_manager.get_image_mapping()
        return jsonify({
            'success': True,
            'categories': image_manager.CATEGORY_FOLDERS,
            'food_types': image_manager.FOOD_TYPES,
            'images': manifest,
            'total': sum(len(imgs) for imgs in manifest.values())
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/images/<category>', methods=['GET'])
@app.route('/api/images/<category>/<food_type>', methods=['GET'])
def get_category_images(category, food_type=None):
    """Get images for a specific category"""
    try:
        count = request.args.get('count', default=1, type=int)
        images = image_manager.get_images(category, food_type, count)
        
        return jsonify({
            'success': True,
            'category': category,
            'food_type': food_type,
            'count': len(images),
            'images': images
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/images/מדינתיים/events', methods=['GET'])
def get_government_events():
    """Get images for צווים ואירועים - ONLY from מדינתיים folder"""
    try:
        count = request.args.get('count', default=1, type=int)
        # Hard rule: ONLY images from מדינתיים folder, repeats if needed
        images = image_manager.get_images('מדינתיים', count=count)
        
        return jsonify({
            'success': True,
            'section': 'צווים ואירועים',
            'count': len(images),
            'images': images,
            'note': 'Uses ONLY images from static/images/מדינתיים/'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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

@app.route('/inspirations')
def inspirations():
    """Serve the wedding inspirations page"""
    return render_template('inspirations.html')

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



# Add Cart Routes
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to session cart"""
    data = request.get_json()
    item_id = data.get('id')
    item_type = data.get('type') # 'Venue' or 'Supplier'
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if already in cart
    for item in session['cart']:
        if item['id'] == item_id and item['type'] == item_type:
            return jsonify({'success': False, 'message': 'הפריט כבר קיים בסל'})
            
    session['cart'].append(data)
    session.modified = True
    
    return jsonify({'success': True, 'message': 'הפריט נוסף לסל בהצלחה', 'count': len(session['cart'])})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get cart contents"""
    cart = session.get('cart', [])
    return jsonify({'cart': cart, 'count': len(cart)})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({'success': True})

@app.route('/api/save_event', methods=['POST'])
@login_required
def save_event():
    """Save event with selected vendors to database"""
    data = request.get_json()
    
    # Get cart items from session
    cart = session.get('cart', [])
    
    if not cart:
        return jsonify({'success': False, 'message': 'הסל ריק. אנא בחר לפחות ספק אחד'}), 400
    
    try:
        conn = get_db_connection()
        
        # Create event record
        event_type = data.get('event_type', 'other')
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO events (user_id, event_type, status) VALUES (?, ?, ?)',
            (current_user.id, event_type, 'תכנון')
        )
        
        event_id = cursor.lastrowid
        
        # Add vendors to event
        for item in cart:
            cursor.execute(
                'INSERT INTO event_vendors (event_id, vendor_type, vendor_id, vendor_name, vendor_price) VALUES (?, ?, ?, ?, ?)',
                (event_id, item.get('type'), item.get('id'), item.get('name'), item.get('price'))
            )
        
        conn.commit()
        conn.close()
        
        # Clear cart after saving
        session['cart'] = []
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'האירוע נשמר בהצלחה!',
            'event_id': event_id,
            'redirect': f'/event/{event_id}/manage'
        }), 201
        
    except Exception as e:
        conn.close()
        return jsonify({
            'success': False,
            'message': f'שגיאה בשמירת האירוע: {str(e)}'
        }), 500

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with their saved events"""
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events WHERE user_id = ? ORDER BY created_at DESC',
                         (current_user.id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', events=events)

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
    
    # Get vendors for this event
    vendors = conn.execute('SELECT * FROM event_vendors WHERE event_id = ?',
                          (event_id,)).fetchall()
    
    # Get checklist items
    checklist_items = conn.execute(
        'SELECT * FROM checklist_items WHERE event_id = ? ORDER BY is_completed ASC, created_at DESC',
        (event_id,)
    ).fetchall()
    
    # Calculate progress
    total_count = len(checklist_items)
    completed_count = sum(1 for item in checklist_items if item['is_completed'])
    
    conn.close()
    
    return render_template('manage_event.html',
                         event=event,
                         vendors=vendors,
                         checklist_items=checklist_items,
                         total_count=total_count,
                         completed_count=completed_count)

@app.route('/api/event/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_event_api(event_id):
    """Get, update, or delete event"""
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT * FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        # Get event details
        vendors = conn.execute('SELECT * FROM event_vendors WHERE event_id = ?',
                              (event_id,)).fetchall()
        conn.close()
        return jsonify({
            'event': dict(event),
            'vendors': [dict(v) for v in vendors]
        })
    
    elif request.method == 'PUT':
        # Update event
        data = request.get_json()
        
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
    
    elif request.method == 'DELETE':
        # Delete event and its vendors
        conn.execute('DELETE FROM event_vendors WHERE event_id = ?', (event_id,))
        conn.execute('DELETE FROM checklist_items WHERE event_id = ?', (event_id,))
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/event/<int:event_id>/checklist', methods=['POST', 'GET'])
@login_required
def checklist_items_api(event_id):
    """Add or get checklist items"""
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            conn.close()
            return jsonify({'error': 'Title required'}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO checklist_items (event_id, title) VALUES (?, ?)',
            (event_id, title)
        )
        conn.commit()
        
        item_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': item_id}), 201
    
    elif request.method == 'GET':
        items = conn.execute('SELECT * FROM checklist_items WHERE event_id = ?',
                            (event_id,)).fetchall()
        conn.close()
        return jsonify({'items': [dict(item) for item in items]})

@app.route('/api/checklist/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def checklist_item_api(item_id):
    """Update or delete checklist item"""
    conn = get_db_connection()
    
    item = conn.execute('SELECT event_id FROM checklist_items WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (item['event_id'], current_user.id)).fetchone()
    
    if not event:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        is_completed = data.get('is_completed')
        
        conn.execute('UPDATE checklist_items SET is_completed = ? WHERE id = ?',
                    (is_completed, item_id))
        conn.commit()
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM checklist_items WHERE id = ?', (item_id,))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

def get_grouped_results():
    """Helper to fetch and group all results"""
    venues = Venue.query.all()
    suppliers = Supplier.query.all()
    
    grouped = {
        'אולמות וגנים': [],
        'צלמים': [],
        'תקליטנים': [],
        'קייטרינג': [],
        'להקות ותזמורות': [],
        'עיצוב אירועים': []
    }
    
    # Process Venues
    for v in venues:
        item = {
            'id': v.id,
            'type': 'Venue',
            'category': v.style or 'אולם',
            'name': v.name,
            'description': f"{v.city}, {v.address}. תפוסה: {v.capacity} איש",
            'price': v.price,
            'image': v.image_url or 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?q=80&w=800'
        }
        grouped['אולמות וגנים'].append(item)
        
    # Process Suppliers
    for s in suppliers:
        item = {
            'id': s.id,
            'type': 'Supplier',
            'category': s.supplier_type,
            'name': s.name,
            'description': f"{s.city}. טלפון: {s.phone}",
            'price': s.price,
            'image': s.image_url or 'https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=800'
        }
        
        # Map to categories
        if s.supplier_type == 'Photographer':
            grouped['צלמים'].append(item)
        elif s.supplier_type == 'DJ':
            grouped['תקליטנים'].append(item)
        elif s.supplier_type == 'Catering':
            grouped['קייטרינג'].append(item)
        elif s.supplier_type == 'Orchestra':
            grouped['להקות ותזמורות'].append(item)
        elif s.supplier_type == 'Designer':
            grouped['עיצוב אירועים'].append(item)
            
    return grouped

@app.route('/create_event', methods=['POST'])
def create_event():
    """Handle event creation form submission"""
    results = get_grouped_results()
    return render_template('results.html', results=results)

@app.route('/results')
def results_page():
    """Serve the results page"""
    results = get_grouped_results()
    return render_template('results.html', results=results)

if __name__ == '__main__':
    print("🚀 Starting EasyVents API Server...")
    print("📍 Server running on: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000")
    print("⚠️  Press CTRL+C to stop the server")
    app.run(debug=True, port=5000)
