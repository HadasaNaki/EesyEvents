"""
EasyVents - Backend API Server
Flask server for user authentication and management
"""

from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
import os
from datetime import datetime, timedelta
import uuid
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

# Ensure database directory exists
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

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

# Database configuration used by raw SQLite connections
DATABASE = DB_PATH

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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Initialize database on startup
init_db()

# Create SQLAlchemy tables and add sample data
with app.app_context():
    db.create_all()
    print("✅ SQLAlchemy tables created!")
    
    # Add sample user if users table is empty
    conn = get_db_connection()
    existing_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
    if existing_users['count'] == 0:
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('123456')
        conn.execute('''
            INSERT INTO users (first_name, last_name, email, phone, password_hash, newsletter)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('הדסה', 'נקי', 'hadasa5806@gmail.com', '050-1234567', password_hash, False))
        conn.commit()
        print("✅ Sample user added! (hadasa5806@gmail.com / 123456)")
    conn.close()
    
    # Add sample data if tables are empty
    if Venue.query.count() == 0:
        sample_venues = [
            Venue(name="אולם פאר", city="תל אביב", address="דרך מנחם בגין 132", style="מודרני", capacity=300, price=15000, phone="03-1234567", is_open_air=False),
            Venue(name="גן אירועים רויאל", city="רמת גן", address="רחוב ביאליק 45", style="קלאסי", capacity=200, price=12000, phone="03-7654321", is_open_air=True),
            Venue(name="בית ברטון", city="ירושלים", address="רחוב יפו 15", style="רומנטי", capacity=150, price=18000, phone="02-5551234", is_open_air=False),
            Venue(name="אחוזת פסטורל", city="כפר סבא", address="שדרות ירושלים 89", style="כפרי", capacity=250, price=14000, phone="09-7412369", is_open_air=True),
            Venue(name="מלון דן פנורמה", city="תל אביב", address="רחוב דוד המלך 12", style="יוקרתי", capacity=500, price=25000, phone="03-5191234", is_open_air=False),
            Venue(name="גן אירועים הזית", city="חיפה", address="שדרות בן גוריון 67", style="כפרי", capacity=180, price=11000, phone="04-8234567", is_open_air=True),
            Venue(name="אולם ויסטה", city="נתניה", address="רחוב הרצל 234", style="מודרני", capacity=400, price=17000, phone="09-8765432", is_open_air=False),
            Venue(name="גן העדן", city="רעננה", address="רחוב אחוזה 56", style="יוקרתי", capacity=220, price=20000, phone="09-7456321", is_open_air=True),
            Venue(name="אולמי סמדר", city="פתח תקווה", address="רחוב ז'בוטינסקי 189", style="קלאסי", capacity=350, price=16000, phone="03-9321456", is_open_air=False),
            Venue(name="בית הכנסת הגדול", city="בני ברק", address="רחוב רבי עקיבא 78", style="מסורתי", capacity=300, price=13000, phone="03-5798642", is_open_air=False),
            Venue(name="גן האירועים הקסום", city="הרצליה", address="רחוב סוקולוב 123", style="יוקרתי", capacity=280, price=22000, phone="09-9584123", is_open_air=True),
            Venue(name="אולם המלכות", city="תל אביב", address="רחוב דיזנגוף 167", style="מודרני", capacity=450, price=19000, phone="03-5123698", is_open_air=False),
        ]
        db.session.add_all(sample_venues)
        db.session.commit()
        print("✅ Sample venues added!")
    
    if Supplier.query.count() == 0:
        sample_suppliers = [
            # DJ & מוזיקה (10)
            Supplier(name="DJ רועי מיקס", supplier_type="DJ", city="תל אביב", price=3500, phone="050-1234567", image_url="https://images.unsplash.com/photo-1571266028243-d220c6c36e49?w=800"),
            Supplier(name="DJ שמעון אלקטרו", supplier_type="DJ", city="ירושלים", price=3000, phone="050-8529637", image_url="https://images.unsplash.com/photo-1574391884720-bbc3740c59d1?w=800"),
            Supplier(name="DJ אלכס פארטי", supplier_type="DJ", city="חיפה", price=4000, phone="050-9871234", image_url="https://images.unsplash.com/photo-1598387993281-cecf8b71a8f8?w=800"),
            Supplier(name="DJ דניאל סאונד", supplier_type="DJ", city="רמת גן", price=3800, phone="050-4562378", image_url="https://images.unsplash.com/photo-1571266028243-d220c6c36e49?w=800"),
            Supplier(name="DJ מיכאל ביטס", supplier_type="DJ", city="נתניה", price=3200, phone="050-7893214", image_url="https://images.unsplash.com/photo-1574391884720-bbc3740c59d1?w=800"),
            Supplier(name="להקת הכוכבים", supplier_type="מוזיקה חיה", city="תל אביב", price=8000, phone="050-7412589", image_url="https://images.unsplash.com/photo-1511735111819-9a3f7709049c?w=800"),
            Supplier(name="תזמורת הזהב", supplier_type="מוזיקה חיה", city="ירושלים", price=10000, phone="050-3692581", image_url="https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=800"),
            Supplier(name="להקת הרמוני", supplier_type="מוזיקה חיה", city="חיפה", price=7500, phone="050-1593578", image_url="https://images.unsplash.com/photo-1519683109079-d5f539e1542f?w=800"),
            Supplier(name="DJ יוסי פרו", supplier_type="DJ", city="פתח תקווה", price=3600, phone="050-9517536", image_url="https://images.unsplash.com/photo-1598387993281-cecf8b71a8f8?w=800"),
            Supplier(name="DJ עמית בס", supplier_type="DJ", city="רעננה", price=4200, phone="050-7531598", image_url="https://images.unsplash.com/photo-1571266028243-d220c6c36e49?w=800"),
            
            # צלמים (12)
            Supplier(name="צלמים מקצועיים בע\"מ", supplier_type="צילום", city="רמת גן", price=4500, phone="050-7654321", image_url="https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=800"),
            Supplier(name="צילום יוקרתי", supplier_type="צילום", city="נתניה", price=5000, phone="050-1472583", image_url="https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=800"),
            Supplier(name="סטודיו לייט", supplier_type="צילום", city="ירושלים", price=5500, phone="050-3698521", image_url="https://images.unsplash.com/photo-1606800052052-a08af7148866?w=800"),
            Supplier(name="צילום אומנותי", supplier_type="צילום", city="חיפה", price=4800, phone="050-9517532", image_url="https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=800"),
            Supplier(name="פוקוס סטודיו", supplier_type="צילום", city="תל אביב", price=6000, phone="050-3574196", image_url="https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=800"),
            Supplier(name="צלם המלכים", supplier_type="צילום", city="הרצליה", price=7000, phone="050-9638524", image_url="https://images.unsplash.com/photo-1606800052052-a08af7148866?w=800"),
            Supplier(name="פרספקטיב צילום", supplier_type="צילום", city="רעננה", price=5200, phone="050-7418529", image_url="https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=800"),
            Supplier(name="מומנטום צילום", supplier_type="צילום", city="פתח תקווה", price=4700, phone="050-8527419", image_url="https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=800"),
            Supplier(name="סטודיו פיקסל", supplier_type="צילום", city="בני ברק", price=4200, phone="050-3698527", image_url="https://images.unsplash.com/photo-1606800052052-a08af7148866?w=800"),
            Supplier(name="צילום בוטיק", supplier_type="צילום", city="כפר סבא", price=5800, phone="050-1593574", image_url="https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=800"),
            Supplier(name="לנס מאסטר", supplier_type="צילום", city="ראשון לציון", price=4900, phone="050-7539512", image_url="https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=800"),
            Supplier(name="אימג' פרפקט", supplier_type="צילום", city="חולון", price=4400, phone="050-9517538", image_url="https://images.unsplash.com/photo-1606800052052-a08af7148866?w=800"),
            
            # קייטרינג (8)
            Supplier(name="קייטרינג דלוקס", supplier_type="קייטרינג", city="תל אביב", price=180, phone="03-9876543", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=800"),
            Supplier(name="קייטרינג VIP", supplier_type="קייטרינג", city="רמת גן", price=220, phone="03-5741236", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800"),
            Supplier(name="אוכל מהלב", supplier_type="קייטרינג", city="ירושלים", price=150, phone="02-6543210", image_url="https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?w=800"),
            Supplier(name="מטעמי השף", supplier_type="קייטרינג", city="חיפה", price=200, phone="04-8527419", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=800"),
            Supplier(name="קייטרינג פרימיום", supplier_type="קייטרינג", city="נתניה", price=190, phone="09-7531594", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800"),
            Supplier(name="טעים בכרם", supplier_type="קייטרינג", city="הרצליה", price=210, phone="09-9584127", image_url="https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?w=800"),
            Supplier(name="אוכל טוב", supplier_type="קייטרינג", city="פתח תקווה", price=170, phone="03-9321458", image_url="https://images.unsplash.com/photo-1555244162-803834f70033?w=800"),
            Supplier(name="שף פרטי", supplier_type="קייטרינג", city="רעננה", price=250, phone="09-7456329", image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800"),
            
            # פרחים ועיצוב (10)
            Supplier(name="פרחים של אהבה", supplier_type="פרחים", city="הרצליה", price=2500, phone="09-9517531", image_url="https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800"),
            Supplier(name="עיצוב אירועים פלוס", supplier_type="עיצוב", city="תל אביב", price=4000, phone="03-7539514", image_url="https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800"),
            Supplier(name="פרחי השדה", supplier_type="פרחים", city="חיפה", price=2200, phone="04-8527419", image_url="https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=800"),
            Supplier(name="בלום דיזיין", supplier_type="פרחים", city="רמת גן", price=2800, phone="03-5741239", image_url="https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800"),
            Supplier(name="פרחי היוקרה", supplier_type="פרחים", city="ירושלים", price=3000, phone="02-6543215", image_url="https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=800"),
            Supplier(name="עיצוב מושלם", supplier_type="עיצוב", city="נתניה", price=4500, phone="09-7531596", image_url="https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800"),
            Supplier(name="פרפקט דקור", supplier_type="עיצוב", city="הרצליה", price=5000, phone="09-9584129", image_url="https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=800"),
            Supplier(name="פרחים ברוח", supplier_type="פרחים", city="כפר סבא", price=2400, phone="09-7412376", image_url="https://images.unsplash.com/photo-1522673607200-164d1b6ce486?w=800"),
            Supplier(name="אומנות בפרחים", supplier_type="פרחים", city="רעננה", price=2600, phone="09-7456327", image_url="https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=800"),
            Supplier(name="סטודיו עיצוב", supplier_type="עיצוב", city="פתח תקווה", price=3800, phone="03-9321459", image_url="https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800"),
            
            # איפור ושיער (8)
            Supplier(name="מעצבת שיער ואיפור רוני", supplier_type="איפור", city="תל אביב", price=1500, phone="050-2345678", image_url="https://images.unsplash.com/photo-1560869713-7d0a29430803?w=800"),
            Supplier(name="סטודיו ביוטי", supplier_type="איפור", city="ירושלים", price=1800, phone="050-8741236", image_url="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=800"),
            Supplier(name="מראה מושלם", supplier_type="איפור", city="רמת גן", price=1600, phone="050-3698524", image_url="https://images.unsplash.com/photo-1560869713-7d0a29430803?w=800"),
            Supplier(name="גלאם סטייל", supplier_type="איפור", city="חיפה", price=1700, phone="050-7531592", image_url="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=800"),
            Supplier(name="ביוטי לאונג'", supplier_type="איפור", city="נתניה", price=1550, phone="050-9584126", image_url="https://images.unsplash.com/photo-1560869713-7d0a29430803?w=800"),
            Supplier(name="סטודיו שיק", supplier_type="איפור", city="הרצליה", price=2000, phone="050-7456324", image_url="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=800"),
            Supplier(name="מייקאפ ארט", supplier_type="איפור", city="רעננה", price=1650, phone="050-9321457", image_url="https://images.unsplash.com/photo-1560869713-7d0a29430803?w=800"),
            Supplier(name="הייר & מייקאפ", supplier_type="איפור", city="פתח תקווה", price=1750, phone="050-7539518", image_url="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=800"),
            
            # אטרקציות (6)
            Supplier(name="אטרקציות לאירועים", supplier_type="אטרקציות", city="רמת גן", price=3000, phone="050-9638527", image_url="https://images.unsplash.com/photo-1496337589254-7e19d01cec44?w=800"),
            Supplier(name="משחקים וכיף", supplier_type="אטרקציות", city="פתח תקווה", price=2500, phone="050-1593574", image_url="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800"),
            Supplier(name="פאן פארק", supplier_type="אטרקציות", city="תל אביב", price=3500, phone="050-7531597", image_url="https://images.unsplash.com/photo-1496337589254-7e19d01cec44?w=800"),
            Supplier(name="אטרקציות פרימיום", supplier_type="אטרקציות", city="הרצליה", price=4000, phone="050-9584128", image_url="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800"),
            Supplier(name="כיף וחוויה", supplier_type="אטרקציות", city="נתניה", price=2800, phone="050-7456326", image_url="https://images.unsplash.com/photo-1496337589254-7e19d01cec44?w=800"),
            Supplier(name="אטרקציות ישראל", supplier_type="אטרקציות", city="ירושלים", price=3200, phone="050-3698526", image_url="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=800"),
            
            # וידאו (6)
            Supplier(name="סרטי אירועים פרו", supplier_type="וידאו", city="תל אביב", price=5000, phone="050-7539519", image_url="https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=800"),
            Supplier(name="וידאו מושלם", supplier_type="וידאו", city="רמת גן", price=4500, phone="050-9321458", image_url="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"),
            Supplier(name="פילם סטודיו", supplier_type="וידאו", city="ירושלים", price=5500, phone="050-7456328", image_url="https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=800"),
            Supplier(name="וידאוגרף מקצועי", supplier_type="וידאו", city="חיפה", price=4800, phone="050-9584130", image_url="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"),
            Supplier(name="סינמה לאירועים", supplier_type="וידאו", city="נתניה", price=4700, phone="050-7531598", image_url="https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=800"),
            Supplier(name="מוביקס פרודקשן", supplier_type="וידאו", city="הרצליה", price=6000, phone="050-3698528", image_url="https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"),
        ]
        db.session.add_all(sample_suppliers)
        db.session.commit()
        print("✅ Sample suppliers added!")

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

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password_api():
    try:
        data = request.json
        email = data.get('email')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'message': 'אם האימייל קיים במערכת, נשלח אליו קישור לאיפוס'}), 200
            
        token = str(uuid.uuid4())
        expiry = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        conn.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?', 
                    (token, expiry, user['id']))
        conn.commit()
        conn.close()
        
        print(f"PASSWORD RESET LINK: http://localhost:5000/reset-password/{token}")
        
        return jsonify({'message': 'אם האימייל קיים במערכת, נשלח אליו קישור לאיפוס'}), 200
    except Exception as e:
        print(f"Error in forgot_password_api: {e}")
        return jsonify({'message': 'שגיאה פנימית'}), 500

@app.route('/reset-password/<token>')
def reset_password_page(token):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE reset_token = ?', (token,)).fetchone()
    conn.close()
    
    if not user:
        return render_template('login.html'), 400
        
    return render_template('reset_password.html', token=token)

@app.route('/api/reset-password/<token>', methods=['POST'])
def reset_password_api(token):
    try:
        data = request.json
        password = data.get('password')
        
        if not password:
            return jsonify({'message': 'חסרה סיסמה'}), 400

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE reset_token = ?', (token,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'message': 'קישור לא תקין או פג תוקף'}), 400
            
        reset_expiry_str = user['reset_token_expiry']
        if reset_expiry_str:
            try:
                expiry = datetime.strptime(reset_expiry_str, '%Y-%m-%d %H:%M:%S.%f')
                if datetime.now() > expiry:
                    conn.close()
                    return jsonify({'message': 'הקישור פג תוקף'}), 400
            except ValueError:
                 pass
        
        hashed = generate_password_hash(password)
        conn.execute('UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?',
                    (hashed, user['id']))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'הסיסמה שונתה בהצלחה'}), 200
    except Exception as e:
        print(f"Error in reset_password_api: {e}")
        return jsonify({'message': 'שגיאה פנימית'}), 500

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

@app.route('/api/save_cart_to_event', methods=['POST'])
@login_required
def save_cart_to_event():
    """Save cart items to most recent event or create new one"""
    data = request.get_json()
    cart_items = data.get('cart_items', [])
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'הסל ריק. אנא בחר לפחות ספק אחד'}), 400
    
    try:
        conn = get_db_connection()
        
        # Get user's most recent event
        event = conn.execute(
            'SELECT * FROM events WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
            (current_user.id,)
        ).fetchone()
        
        if not event:
            # Create new event if none exists
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO events (user_id, event_type, status) VALUES (?, ?, ?)',
                (current_user.id, 'other', 'תכנון')
            )
            event_id = cursor.lastrowid
        else:
            event_id = event['id']
        
        # Add vendors to event
        cursor = conn.cursor()
        for item in cart_items:
            cursor.execute(
                'INSERT INTO event_vendors (event_id, vendor_type, vendor_id, vendor_name, vendor_price) VALUES (?, ?, ?, ?, ?)',
                (event_id, item.get('type'), item.get('id'), item.get('name'), item.get('price'))
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'הספקים נוספו בהצלחה! ({len(cart_items)} ספקים)',
            'event_id': event_id,
            'redirect': f'/event/{event_id}/manage'
        }), 201
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'message': f'שגיאה בשמירת הספקים: {str(e)}'
        }), 500

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
    
    # Get vendors for this event with full details
    vendors = conn.execute('''
        SELECT 
            ev.id,
            ev.vendor_name,
            ev.vendor_type,
            ev.vendor_price,
            ev.created_at
        FROM event_vendors ev
        WHERE ev.event_id = ?
        ORDER BY ev.created_at DESC
    ''', (event_id,)).fetchall()
    
    # Get checklist items
    checklist_items = conn.execute(
        'SELECT * FROM checklist_items WHERE event_id = ? ORDER BY is_completed ASC, created_at DESC',
        (event_id,)
    ).fetchall()
    
    # Get guests
    guests = conn.execute(
        'SELECT * FROM guests WHERE event_id = ? ORDER BY created_at DESC',
        (event_id,)
    ).fetchall()
    
    # Calculate progress
    total_count = len(checklist_items)
    checklist_completed = sum(1 for item in checklist_items if item['is_completed'])
    
    conn.close()
    
    return render_template('manage_event.html',
                         event=event,
                         vendors=vendors,
                         checklist_items=checklist_items,
                         guests=guests,
                         total_count=total_count,
                         completed_count=checklist_completed)

# ==================== GUEST MANAGEMENT API ====================

@app.route('/api/event/<int:event_id>/guests', methods=['GET', 'POST'])
@login_required
def manage_guests(event_id):
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if request.method == 'GET':
        guests = conn.execute('SELECT * FROM guests WHERE event_id = ?', (event_id,)).fetchall()
        conn.close()
        return jsonify({'success': True, 'guests': [dict(g) for g in guests]})

    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone', '')
        invites = data.get('invites_count', 1)
        
        if not name:
            conn.close()
            return jsonify({'success': False, 'message': 'Name is required'}), 400
            
        try:
            conn.execute(
                'INSERT INTO guests (event_id, name, phone, invites_count) VALUES (?, ?, ?, ?)',
                (event_id, name, phone, invites)
            )
            conn.commit()
            guest_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.close()
            return jsonify({'success': True, 'id': guest_id, 'message': 'Guest added successfully'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/event/<int:event_id>/guests/batch', methods=['POST'])
@login_required
def batch_add_guests(event_id):
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        raw_text = data.get('text', '')
        default_invites = int(data.get('default_invites', 1))
        
        added_count = 0
        
        # Split by lines
        lines = raw_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Basic parsing: Try to extract name, phone, count
            # Formats supported:
            # "Name"
            # "Name - 5" (5 invites)
            # "Name - 0501234567"
            # "Name - 0501234567 - 5"
            
            parts = [p.strip() for p in line.split('-')]
            name = parts[0]
            phone = ''
            invites = default_invites
            
            if len(parts) > 1:
                # Check if second part is number (invites) or phone
                second = parts[1]
                if second.isdigit() and len(second) < 5: # Likely invite count
                    invites = int(second)
                else:
                    phone = second
                    
            if len(parts) > 2:
                 # Check third part
                 third = parts[2]
                 if third.isdigit():
                     invites = int(third)
            
            if name:
                conn.execute(
                    'INSERT INTO guests (event_id, name, phone, invites_count) VALUES (?, ?, ?, ?)',
                    (event_id, name, phone, invites)
                )
                added_count += 1
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Successfully added {added_count} guests'})
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/event/<int:event_id>/guests/<int:guest_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_single_guest(event_id, guest_id):
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if request.method == 'DELETE':
        conn.execute('DELETE FROM guests WHERE id = ? AND event_id = ?', (guest_id, event_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Guest deleted'})

    elif request.method == 'PUT':
        data = request.get_json()
        status = data.get('status')
        
        if status:
            conn.execute('UPDATE guests SET status = ? WHERE id = ? AND event_id = ?', 
                        (status, guest_id, event_id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Guest updated'})

# ==================== VENDOR MANAGEMENT API ====================

@app.route('/api/event/<int:event_id>/vendor/<int:item_id>', methods=['DELETE'])
@login_required
def delete_vendor(event_id, item_id):
    conn = get_db_connection()
    
    # Verify ownership
    event = conn.execute('SELECT id FROM events WHERE id = ? AND user_id = ?',
                        (event_id, current_user.id)).fetchone()
    if not event:
        conn.close()
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        conn.execute('DELETE FROM event_vendors WHERE id = ? AND event_id = ?', (item_id, event_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Vendor removed successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

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
    """Helper to fetch and group filtered results"""
    from sqlalchemy import or_

    # Get filter params from request.args
    args = request.args
    
    # Base Queries
    venues_query = Venue.query
    suppliers_query = Supplier.query

    # --- Filtering Logic ---
    
    # 1. Region Filtering
    # Handle comma-separated list or multiple args
    region_arg = args.get('region')
    if region_arg:
        selected_regions = region_arg.split(',')
        region_city_map = {
            'north': ['חיפה', 'טבריה', 'עכו', 'צפת', 'נצרת', 'קרית שמונה'],
            'sharon': ['נתניה', 'הרצליה', 'כפר סבא', 'רעננה', 'הוד השרון', 'רמת השרון'],
            'center': ['תל אביב', 'רמת גן', 'גבעתיים', 'בני ברק', 'פתח תקווה', 'חולון', 'בת ים', 'ראשון לציון'],
            'jerusalem': ['ירושלים', 'בית שמש', 'מבשרת ציון', 'מעלה אדומים'],
            'south': ['באר שבע', 'אשדוד', 'אשקלון', 'אילת', 'דימונה']
        }
        allowed_cities = []
        for r in selected_regions:
            allowed_cities.extend(region_city_map.get(r, []))
        
        if allowed_cities:
            venues_query = venues_query.filter(Venue.city.in_(allowed_cities))
            suppliers_query = suppliers_query.filter(Supplier.city.in_(allowed_cities))

    # 2. Venue Type Filtering (Venues only)
    venue_type = args.get('venue_type')
    if venue_type:
        type_keywords = {
            'hall': ['אולם'],
            'garden': ['גן'],
            'hotel': ['מלון'],
            'synagogue': ['בית כנסת'],
            'restaurant': ['מסעדה'],
        }
        keywords = type_keywords.get(venue_type)
        if keywords:
            venues_query = venues_query.filter(or_(*[Venue.name.like(f'%{k}%') for k in keywords]))

    # 3. Style Filtering (Venues mostly)
    style = args.get('style')
    if style:
        style_map = {
            'luxury': 'יוקרתי',
            'modern': 'מודרני',
            'rustic': 'כפרי',
            'vintage': 'וינטג',
            'boho': 'בוהו',
            'classic': 'קלאסי'
        }
        hebrew_style = style_map.get(style)
        if hebrew_style:
             venues_query = venues_query.filter(Venue.style.like(f'%{hebrew_style}%'))

    # 4. Guest Capacity (Venues)
    guests = args.get('guests', type=int)
    if guests:
         venues_query = venues_query.filter(Venue.capacity >= guests)

    # 5. Budget Filtering (Venues) - Rough estimation
    budget = args.get('budget')
    if budget:
        # Assuming Venue.price is total rental or base price.
        # This logic is approximate as we don't have proper max/min price columns logic
        budget_map = {
            'low': 50000,
            'medium': 100000,
            'high': 200000,
            'premium': 350000,
            'luxury': 999999999
        }
        max_price = budget_map.get(budget)
        if max_price:
             venues_query = venues_query.filter(Venue.price <= max_price)

    # Fetch Results
    venues = venues_query.all()
    suppliers = suppliers_query.all()
    
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
        
        # Map to categories (support both Hebrew and English)
        supplier_type = s.supplier_type.lower()
        if 'צילום' in supplier_type or 'photograph' in supplier_type or 'וידאו' in supplier_type or 'video' in supplier_type:
            grouped['צלמים'].append(item)
        elif 'dj' in supplier_type or 'תקליטן' in supplier_type:
            grouped['תקליטנים'].append(item)
        elif 'קייטרינג' in supplier_type or 'catering' in supplier_type:
            grouped['קייטרינג'].append(item)
        elif 'מוזיקה' in supplier_type or 'orchestra' in supplier_type or 'להקה' in supplier_type or 'תזמורת' in supplier_type:
            grouped['להקות ותזמורות'].append(item)
        elif 'עיצוב' in supplier_type or 'designer' in supplier_type or 'פרחים' in supplier_type or 'דקור' in supplier_type or 'איפור' in supplier_type or 'makeup' in supplier_type or 'אטרקציות' in supplier_type:
            grouped['עיצוב אירועים'].append(item)
            
    return grouped

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
