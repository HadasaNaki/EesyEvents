"""
EasyEvents - Backend API Server
Flask server for user authentication, venues, and suppliers management
"""

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
from datetime import datetime

# ============================================================================
# 1. APPLICATION INITIALIZATION
# ============================================================================

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'super_secret_key_for_easyevents_session'
CORS(app)

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'easyevents.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================================================
# 2. DATABASE MODELS
# ============================================================================

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    newsletter = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"


class Venue(db.Model):
    """Venue model for event locations"""
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    city = db.Column(db.String(60), nullable=False, index=True)
    address = db.Column(db.String(200))
    style = db.Column(db.String(50))  # e.g., Luxury, Boho, Modern
    is_open_air = db.Column(db.Boolean, default=False)
    price = db.Column(db.Integer)  # Average price per guest
    phone = db.Column(db.String(20))
    capacity = db.Column(db.Integer)  # Maximum number of guests
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Venue {self.name} in {self.city}>"
    
    def to_dict(self):
        """Convert venue to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'address': self.address,
            'style': self.style,
            'is_open_air': self.is_open_air,
            'price': self.price,
            'phone': self.phone,
            'capacity': self.capacity
        }


class Supplier(db.Model):
    """Supplier model for event services"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    supplier_type = db.Column(db.String(50), nullable=False, index=True)  # DJ, Catering, Designer, Photographer, etc.
    city = db.Column(db.String(60), index=True)  # Service area
    phone = db.Column(db.String(20))
    price = db.Column(db.Integer)  # Starting price / average price
    cuisine_type = db.Column(db.String(50))  # For Catering: Meat, Dairy, Vegan, Private Chef, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Supplier {self.name} ({self.supplier_type})>"
    
    def to_dict(self):
        """Convert supplier to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'supplier_type': self.supplier_type,
            'city': self.city,
            'phone': self.phone,
            'price': self.price,
            'cuisine_type': self.cuisine_type
        }


# ============================================================================
# 3. FLASK-LOGIN SETUP
# ============================================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


@login_manager.user_loader
def load_user(user_id):
    """Load user from database for Flask-Login"""
    return db.session.get(User, int(user_id))


# ============================================================================
# 4. VALIDATION FUNCTIONS
# ============================================================================

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


# ============================================================================
# 5. DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database and create all tables"""
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database initialized successfully!")
            print("[OK] Tables created: users, venues, suppliers")
        except Exception as e:
            print(f"[ERROR] Error initializing database: {str(e)}")


# Initialize database on application startup
init_db()



# ============================================================================
# 6. AUTHENTICATION API ENDPOINTS
# ============================================================================

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
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            'success': False,
            'message': 'משתמש עם אימייל זה כבר קיים במערכת',
            'redirect': 'login.html'
        }), 409
    
    # Create new user
    try:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            newsletter=newsletter
        )
        db.session.add(new_user)
        db.session.commit()
        
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
        db.session.rollback()
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
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            'success': False,
            'message': 'המשתמש אינו קיים במערכת. האם תרצה להירשם?',
            'redirect': 'register.html'
        }), 404
    
    # Verify password
    if not check_password_hash(user.password_hash, password):
        return jsonify({
            'success': False,
            'message': 'הסיסמה שגויה. נסה שוב.'
        }), 401
    
    # Login successful
    login_user(user, remember=remember)
    return jsonify({
        'success': True,
        'message': f'שלום {user.first_name}! התחברת בהצלחה',
        'user': {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
            'phone': user.phone
        }
    }), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user"""
    logout_user()
    return jsonify({'success': True, 'message': 'התנתקת בהצלחה'})


@app.route('/api/current_user', methods=['GET'])
def get_current_user_api():
    """Get current logged-in user"""
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
    
    user = User.query.filter_by(email=email).first()
    return jsonify({'exists': user is not None})


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (for debugging - remove in production!)"""
    users = User.query.all()
    return jsonify({
        'users': [
            {
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'phone': u.phone,
                'created_at': u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ],
        'count': len(users)
    })




# ============================================================================
# 7. VENUE API ENDPOINTS
# ============================================================================

@app.route('/api/venues', methods=['GET'])
def get_venues():
    """Get all venues"""
    venues = Venue.query.all()
    return jsonify({
        'success': True,
        'venues': [v.to_dict() for v in venues],
        'count': len(venues)
    })


@app.route('/api/venues/<int:venue_id>', methods=['GET'])
def get_venue(venue_id):
    """Get a specific venue by ID"""
    venue = Venue.query.get(venue_id)
    if not venue:
        return jsonify({'success': False, 'message': 'Venue not found'}), 404
    return jsonify({'success': True, 'venue': venue.to_dict()})


@app.route('/api/venues', methods=['POST'])
@login_required
def create_venue():
    """Create a new venue (admin only)"""
    data = request.get_json()
    
    try:
        new_venue = Venue(
            name=data.get('name'),
            city=data.get('city'),
            address=data.get('address'),
            style=data.get('style'),
            is_open_air=data.get('is_open_air', False),
            price=data.get('price'),
            phone=data.get('phone'),
            capacity=data.get('capacity')
        )
        db.session.add(new_venue)
        db.session.commit()
        return jsonify({'success': True, 'venue': new_venue.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# 8. SUPPLIER API ENDPOINTS
# ============================================================================

@app.route('/api/suppliers', methods=['GET'])
def get_all_suppliers():
    """Get all suppliers"""
    suppliers = Supplier.query.all()
    return jsonify({
        'success': True,
        'suppliers': [s.to_dict() for s in suppliers],
        'count': len(suppliers)
    })


@app.route('/api/suppliers/<supplier_type>', methods=['GET'])
def get_suppliers_by_type(supplier_type):
    """Get all suppliers of a given type"""
    suppliers = Supplier.query.filter_by(supplier_type=supplier_type).all()
    return jsonify({
        'success': True,
        'supplier_type': supplier_type,
        'suppliers': [s.to_dict() for s in suppliers],
        'count': len(suppliers)
    })


@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get a specific supplier by ID"""
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    return jsonify({'success': True, 'supplier': supplier.to_dict()})


@app.route('/api/suppliers', methods=['POST'])
@login_required
def create_supplier():
    """Create a new supplier (admin only)"""
    data = request.get_json()
    
    try:
        new_supplier = Supplier(
            name=data.get('name'),
            supplier_type=data.get('supplier_type'),
            city=data.get('city'),
            phone=data.get('phone'),
            price=data.get('price')
        )
        db.session.add(new_supplier)
        db.session.commit()
        return jsonify({'success': True, 'supplier': new_supplier.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# 9. STATISTICS & ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    user_count = User.query.count()
    venue_count = Venue.query.count()
    supplier_count = Supplier.query.count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': user_count,
            'total_venues': venue_count,
            'total_suppliers': supplier_count
        }
    })


# ============================================================================
# 10. TEST DATA INSERTION ROUTES (Development Only)
# ============================================================================

@app.route('/api/dev/seed-venues', methods=['POST'])
def seed_venues():
    """Insert test venue data (development only)"""
    test_venues = [
        Venue(
            name='אולם הזהב',
            city='תל אביב',
            address='רחוב דיזנגוף 123',
            style='Luxury',
            is_open_air=False,
            price=5000,
            phone='03-1234567',
            capacity=300
        ),
        Venue(
            name='גן הירוק',
            city='ירושלים',
            address='רחוב בן יהודה 456',
            style='Boho',
            is_open_air=True,
            price=3000,
            phone='02-9876543',
            capacity=200
        ),
        Venue(
            name='מרכז המודרני',
            city='חיפה',
            address='רחוב הנמל 789',
            style='Modern',
            is_open_air=False,
            price=4000,
            phone='04-5555555',
            capacity=250
        )
    ]
    
    try:
        for venue in test_venues:
            if not Venue.query.filter_by(name=venue.name).first():
                db.session.add(venue)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Added {len(test_venues)} test venues'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/dev/seed-suppliers', methods=['POST'])
def seed_suppliers():
    """Insert test supplier data (development only)"""
    test_suppliers = [
        Supplier(
            name='DJ דני',
            supplier_type='DJ',
            city='תל אביב',
            phone='050-1234567',
            price=2000
        ),
        Supplier(
            name='קייטרינג גוט - בשר',
            supplier_type='Catering',
            city='תל אביב',
            phone='03-9876543',
            price=150,
            cuisine_type='בשר'
        ),
        Supplier(
            name='קייטרינג גוט - חלבי',
            supplier_type='Catering',
            city='תל אביב',
            phone='03-9876543',
            price=140,
            cuisine_type='חלבי'
        ),
        Supplier(
            name='קייטרינג גוט - טבעוני',
            supplier_type='Catering',
            city='תל אביב',
            phone='03-9876543',
            price=130,
            cuisine_type='טבעוני'
        ),
        Supplier(
            name='שף פרטי - אלון',
            supplier_type='Catering',
            city='תל אביב',
            phone='050-3333333',
            price=200,
            cuisine_type='שף פרטי'
        ),
        Supplier(
            name='צלם מיקי',
            supplier_type='Photographer',
            city='ירושלים',
            phone='054-1111111',
            price=3000
        ),
        Supplier(
            name='מעצבת שרה',
            supplier_type='Designer',
            city='חיפה',
            phone='050-2222222',
            price=2500
        )
    ]
    
    try:
        for supplier in test_suppliers:
            if not Supplier.query.filter_by(name=supplier.name).first():
                db.session.add(supplier)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Added {len(test_suppliers)} test suppliers'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# 11. STATIC ROUTES FOR SERVING HTML PAGES
# ============================================================================

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
    """Serve the results page with real data from database"""
    # Get filter parameters
    venue_type = request.args.get('venue_type', '')
    style = request.args.get('style', '')
    region = request.args.get('region', '')
    budget = request.args.get('budget', '')
    guests = request.args.get('guests', '')
    
    # Get venues from database
    venues = Venue.query.all()
    
    # Get suppliers from database (all types)
    suppliers = Supplier.query.all()
    
    # Simple filtering
    if style:
        venues = [v for v in venues if v.style and v.style.lower() == style.lower()]
    
    if budget:
        try:
            budget_int = int(budget)
            venues = [v for v in venues if v.price and v.price <= budget_int]
        except:
            pass
    
    if guests:
        try:
            guests_int = int(guests)
            venues = [v for v in venues if v.capacity and v.capacity >= guests_int]
        except:
            pass
    
    # Pass data to template
    return render_template('results.html', 
                         venues=venues, 
                         suppliers=suppliers,
                         filters={
                             'venue_type': venue_type,
                             'style': style,
                             'region': region,
                             'budget': budget,
                             'guests': guests
                         })


# ============================================================================
# 12. APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[START] Starting EasyEvents API Server")
    print("="*60)
    print("[INFO] Server running on: http://localhost:5000")
    print("[INFO] API Documentation:")
    print("[INFO]    GET    /api/venues                - Get all venues")
    print("[INFO]    GET    /api/suppliers/<type>      - Get suppliers by type")
    print("[INFO]    GET    /api/stats                 - Get database stats")
    print("[INFO]    POST   /api/dev/seed-venues       - Add test venues")
    print("[INFO]    POST   /api/dev/seed-suppliers    - Add test suppliers")
    print("="*60)
    print("[INFO] Press CTRL+C to stop the server\n")
    app.run(debug=True, port=5000)
