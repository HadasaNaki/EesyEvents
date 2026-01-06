import os
import random
from pathlib import Path
from app import app, db, Venue, Supplier, get_local_venue_image, image_manager

# --- LOCAL IMAGES ONLY ---
# Using ImageManager for strict folder-based image selection

# Track image indices per category
_image_indices = {}

def get_venue_image(style, venue_index=0):
    """Selects a unique venue image - uses ImageManager for strict folder rules"""
    # Determine category based on style
    if 'pool' in style.lower() or 'villa' in style.lower():
        category = 'pool'
    elif 'wedding' in style.lower() or 'garden' in style.lower():
        category = 'wedding'
    else:
        category = 'hall'
    
    # Get image using ImageManager
    images = image_manager.get_images(category, count=100)
    if not images:
        return None
    
    # Return image by index (rotates through all available images)
    return images[venue_index % len(images)]

def get_supplier_image(type_, subtype=None):
    """Suppliers use provider-specific images from ImageManager - STRICT folder rules"""
    # Map supplier types to image categories
    category_map = {
        'Catering': 'food',
        'DJ': 'dj',
        'Orchestra': 'orchestra',
        'Photographer': 'photographers',
        'Designer': 'design'
    }
    
    category = category_map.get(type_)
    if not category:
        # No matching category - return None instead of fake fallback
        return None
    
    # For food, determine food_type based on subtype
    if category == 'food':
        food_type_map = {
            'Meat_Chef': 'Meat',
            'Meat_Asado': 'Meat',
            'Dairy_Boutique': 'Milk',
            'Sushi_Luxury': 'Neutral',
            'Street_Food': 'Neutral',
            'Dessert': 'Neutral'
        }
        food_type = food_type_map.get(subtype, 'Neutral')
        # Get ALL images for food
        images = image_manager.get_images('food', food_type=food_type, count=100)
    else:
        # For other categories, get ALL images (not just 1)
        images = image_manager.get_images(category, count=100)
    
    if not images:
        return None
    
    # Get next image in rotation for this category
    if category not in _image_indices:
        _image_indices[category] = 0
    
    image_url = images[_image_indices[category] % len(images)]
    _image_indices[category] += 1
    
    return image_url

def seed_data():
    print("🌱 Seeding database with ISRAELI VENUES...")
    print("📸 Real names, Real venues!")
    print("🖼️ Images can repeat - we focus on quality!")
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # --- VENUES (אולמות בישראל) ---
        venues_data = [
            # HALLS (אולמות)
            ('אולם הוד', 'תל אביב', 'רחוב דיזנגוף 50', 'Luxury_Hall', False, 280, 450),
            ('אולם השרון', 'ראשון לציון', 'רחוב הרצל 15', 'Luxury_Hall', False, 320, 600),
            ('אולם מלכי', 'ירושלים', 'דרך חברון 12', 'Luxury_Hall', False, 350, 750),
            ('אולם כרמל', 'חיפה', 'רחוב פאנאדי 8', 'Luxury_Hall', False, 300, 550),
            ('אולם הרימון', 'פתח תקווה', 'אבן גבירול 22', 'Luxury_Hall', False, 290, 500),
            ('אולם יהלום', 'נתניה', 'רחוב גרנדציה 5', 'Luxury_Hall', False, 310, 480),
            ('אולם אילת', 'אילת', 'רחוב משה דיין 1', 'Modern_Loft', False, 400, 350),
            ('לופט קונספט', 'תל אביב', 'רחוב פלורנטין 35', 'Modern_Loft', False, 450, 200),
            
            # GARDENS / WEDDING VENUES (גנים לחתונה)
            ('גן הורדים', 'קיסריה', 'רחוב העתיקות 3', 'Garden_Classic', True, 500, 600),
            ('גן המלך', 'רעננה', 'רחוב הפארק 10', 'Garden_Classic', True, 450, 500),
            ('גן הנוער', 'ראשון לציון', 'כיכר התרבות 2', 'Garden_Classic', True, 380, 450),
            ('גן העץ', 'רחובות', 'רחוב המדע 7', 'Garden_Classic', True, 420, 550),
            ('גן הגן', 'קיבוץ געש', 'דרך החוף 1', 'Boho_Nature', True, 350, 400),
            ('גן הטבע', 'משמר השרון', 'רחוב השדות 6', 'Boho_Nature', True, 370, 450),
            
            # POOL VILLAS (וילות עם בריכה)
            ('וילת הבריכה', 'קיסריה', 'רחוב הדרים 5', 'Villa_Pool', True, 6000, 120),
            ('וילה בנוף', 'סביון', 'רחוב הזית 2', 'Villa_Pool', True, 7500, 150),
            ('וילת המים', 'כפר סבא', 'רחוב הגפן 8', 'Villa_Pool', True, 5000, 100),
            ('וילה לבנה', 'הרצליה', 'רחוב הגלים 3', 'Villa_Pool', True, 8000, 130),
            ('וילת השקיעה', 'אילת', 'רחוב הים 4', 'Villa_Pool', True, 6500, 110),
            ('בריכת קריסטל', 'מושב בצרה', 'דרך הגן 1', 'Villa_Pool', True, 5500, 95),
            ('וילה בשדה', 'קיבוץ יגור', 'דרך הכניסה 1', 'Rustic_Barn', True, 3500, 80),
            ('אסם יקום', 'יקום', 'דרך המושב 1', 'Rustic_Barn', True, 3000, 70),
        ]

        print(f"🏠 Adding {len(venues_data)} venues...")
        for idx, (name, city, addr, style, open_air, price, cap) in enumerate(venues_data):
            v = Venue(
                name=name,
                city=city,
                address=addr,
                style=style.split('_')[0],
                is_open_air=open_air,
                price=price,
                capacity=cap,
                phone=f"03-{random.randint(1000000, 9999999)}",
                image_url=None
            )
            db.session.add(v)
            db.session.flush()
            # Get local image with rotation - NO REPEATS
            v.image_url = get_venue_image(style, idx)

        # --- SUPPLIERS ---
        # Structure: (Name, Type, Subtype, City, Price)
        suppliers_data = [
            # DESIGNERS
            ('עיצובים מהלב', 'Designer', 'Floral', 'תל אביב', 5000),
            ('פרחי ירושלים', 'Designer', 'Floral', 'ירושלים', 4500),
            ('סטייל ועיצוב', 'Designer', 'Table', 'חיפה', 6000),
            ('עיצוב אירועים יוקרתי', 'Designer', 'Floral', 'הרצליה', 8000),
            ('מג\'יק טאץ\'', 'Designer', 'Table', 'ראשון לציון', 5500),
            ('פרחים וצבעים', 'Designer', 'Floral', 'באר שבע', 4000),
            ('עיצוב שולחנות בוטיק', 'Designer', 'Table', 'רעננה', 4500),
            ('עיצוב חופות', 'Designer', 'Floral', 'נתניה', 3500),
            ('וינטג\' סטייל', 'Designer', 'Table', 'יפו', 5500),
            
            # ORCHESTRAS
            ('תזמורת הלב', 'Orchestra', 'Live', 'כל הארץ', 12000),
            ('צלילי המזרח', 'Orchestra', 'Live', 'באר שבע', 10000),
            ('הלהקה החיה', 'Orchestra', 'Live', 'תל אביב', 15000),
            ('סימפוניה', 'Orchestra', 'Live', 'ירושלים', 13000),
            ('מקצב הלב', 'Orchestra', 'Live', 'חיפה', 11000),
            
            # DJs
            ('DJ Ronen', 'DJ', 'Party', 'תל אביב', 4000),
            ('DJ Galit', 'DJ', 'Wedding', 'הרצליה', 4500),
            ('DJ BeatMaster', 'DJ', 'Party', 'ראשון לציון', 3500),
            ('DJ Party', 'DJ', 'Party', 'חיפה', 3000),
            ('DJ Sky', 'DJ', 'Party', 'אילת', 5000),
            ('DJ Melody', 'DJ', 'Wedding', 'ירושלים', 4200),
            ('DJ Groove', 'DJ', 'Party', 'רמת גן', 4000),
            ('DJ Wedding', 'DJ', 'Wedding', 'פתח תקווה', 3900),
            ('DJ Soul', 'DJ', 'Wedding', 'יפו', 4300),

            # CATERING - MEAT
            ('קייטרינג השף', 'Catering', 'Meat_Chef', 'נתניה', 250),
            ('בשרים על האש', 'Catering', 'Meat_Asado', 'אשדוד', 200),
            ('קייטרינג גורמה', 'Catering', 'Meat_Chef', 'תל אביב', 350),
            ('שף בוטיק', 'Catering', 'Meat_Chef', 'הרצליה', 400),
            ('אסאדו בטבע', 'Catering', 'Meat_Asado', 'כל הארץ', 300),
            ('בשרים מעושנים', 'Catering', 'Meat_Asado', 'ראשון לציון', 330),
            ('פוד טראק המבורגר', 'Catering', 'Street_Food', 'מרכז', 160),

            # CATERING - DAIRY / SUSHI / DESSERT
            ('טעמים וריחות', 'Catering', 'Dairy_Boutique', 'פתח תקווה', 220),
            ('מתוקים ומלוחים', 'Catering', 'Dessert', 'רמת גן', 280),
            ('סושי לאירועים', 'Catering', 'Sushi_Luxury', 'תל אביב', 320),
            ('פיצה בטאבון', 'Catering', 'Street_Food', 'כל הארץ', 150),
            ('קייטרינג חלבי', 'Catering', 'Dairy_Boutique', 'ירושלים', 240),
            ('קינוחים ומתוקים', 'Catering', 'Dessert', 'תל אביב', 120),
            ('סושי סטריט', 'Catering', 'Street_Food', 'תל אביב', 180), # Sushi Stand

            # PHOTOGRAPHERS
            ('פוקוס צילום', 'Photographer', 'Moments', 'חולון', 8000),
            ('רגעים יפים', 'Photographer', 'Moments', 'רמת גן', 7500),
            ('קליק אחד', 'Photographer', 'Artistic', 'ירושלים', 6500),
            ('עדשה רחבה', 'Photographer', 'Artistic', 'תל אביב', 9000),
            ('זכרונות מתוקים', 'Photographer', 'Moments', 'חיפה', 7000),
            ('פלאש', 'Photographer', 'Moments', 'באר שבע', 6000),
            ('סטודיו אור', 'Photographer', 'Artistic', 'ראשון לציון', 8500),
            ('צילום אמנותי', 'Photographer', 'Artistic', 'הרצליה', 9500),
            ('וידאו וסטילס', 'Photographer', 'Moments', 'פתח תקווה', 7800),
        ]

        for name, type_, subtype, city, price in suppliers_data:
            s = Supplier(
                name=name,
                supplier_type=type_,
                city=city,
                price=price,
                phone=f"050-{random.randint(1000000, 9999999)}",
                image_url=get_supplier_image(type_, subtype)
            )
            db.session.add(s)

            db.session.add(s)

        # --- GENERATE 200+ EXTRA ITEMS ---
        print("🚀 Generating 200+ extra items...")
        
        cities = ['תל אביב', 'ירושלים', 'חיפה', 'ראשון לציון', 'פתח תקווה', 'אשדוד', 'נתניה', 'באר שבע', 'חולון', 'רמת גן', 'הרצליה', 'כפר סבא', 'רעננה', 'מודיעין', 'חדרה', 'לוד', 'רמלה', 'נס ציונה', 'גדרה', 'אופקים', 'דימונה', 'מצפה רמון', 'אילת', 'קיסריה', 'יפו']
        adjectives = ['היוקרתי', 'הקסום', 'המושלם', 'בטבע', 'על הים', 'האורבני', 'הכפרי', 'המודרני', 'הקלאסי', 'המלכותי', 'הרומנטי', 'הנעים', 'המיוחד', 'של חלומות', 'בנוף']
        venue_nouns = ['אחוזת', 'גני', 'אולמי', 'חצר', 'משכן', 'ארמון', 'בית', 'מתחם', 'קטע', 'מרחב', 'אולם', 'גן', 'בריכת']
        venue_adjectives = ['יוקרה', 'קסם', 'שלום', 'טבע', 'עירוני', 'כפרי', 'עץ', 'אבן', 'זכוכית']
        
        # Generate 120 Extra Venues
        print("  📍 Adding 120 new venues...")
        venue_counter = len(venues_data)
        
        for i in range(120):
            # Randomly choose venue type
            venue_type = random.choice(['hall', 'pool', 'wedding'])
            
            if venue_type == 'pool':
                base_style = 'Villa'
                open_air = True
                image_url = get_venue_image('Villa_Pool', venue_counter)
            elif venue_type == 'wedding':
                base_style = 'Garden'
                open_air = True
                image_url = get_venue_image('Garden_Classic', venue_counter)
            else:
                base_style = 'Luxury'
                open_air = False
                image_url = get_venue_image('Luxury_Hall', venue_counter)
                
            city = random.choice(cities)
            
            name = f"{random.choice(venue_nouns)} {random.choice(venue_adjectives)}"
            if random.random() > 0.6:
                name += f" - {city}"
                
            v = Venue(
                name=name,
                city=city,
                address=f"רחוב {random.choice(['הזית', 'הגפן', 'הים', 'הפרחים', 'הראשונים', 'הנחל', 'הגיא', 'הבוקר'])} {random.randint(1, 200)}",
                style=base_style,
                is_open_air=open_air,
                price=random.randint(180, 800),
                capacity=random.randint(50, 1200),
                phone=f"0{random.choice(['3','4','8','9'])}-{random.randint(1000000, 9999999)}",
                image_url=image_url
            )
            venue_counter += 1
            db.session.add(v)

        # Generate 120 Extra Suppliers
        print("  🎵 Adding 120 new suppliers...")
        supplier_types = {
            'Catering': ['Meat_Chef', 'Meat_Asado', 'Dairy_Boutique', 'Sushi_Luxury', 'Street_Food', 'Dessert'],
            'DJ': ['Party', 'Wedding'],
            'Photographer': ['Artistic', 'Moments'],
            'Designer': ['Floral', 'Table'],
            'Orchestra': ['Live']
        }
        
        catering_names = ['קייטרינג', 'בשרים', 'סושי', 'קינוחים', 'טעמים', 'פיצה', 'עוגות', 'שפע']
        dj_names = ['DJ', 'דיג\'יי', 'מוזיקה', 'סאונד', 'ביט']
        photographer_names = ['צילום', 'קליק', 'עדשה', 'קאמרה', 'זיכרון']
        designer_names = ['עיצוב', 'דקור', 'פרחים', 'סטייל', 'הפקה']
        orchestra_names = ['תזמורת', 'להקה', 'צלילים', 'מוזיקה', 'סימפוניה']
        surnames = ['כהן', 'לוי', 'ישראל', 'רון', 'גל', 'אור', 'שיר', 'דן', 'עמי', 'שלום', 'ברק', 'אדם', 'אריה', 'חן', 'דוד']
        
        for i in range(120):
            sType = random.choice(list(supplier_types.keys()))
            sSubtype = random.choice(supplier_types[sType])
            
            # Choose name based on type
            if sType == 'Catering':
                name = f"{random.choice(catering_names)} {random.choice(surnames)}"
            elif sType == 'DJ':
                name = f"{random.choice(dj_names)} {random.choice(surnames)}"
            elif sType == 'Photographer':
                name = f"{random.choice(photographer_names)} {random.choice(surnames)}"
            elif sType == 'Designer':
                name = f"{random.choice(designer_names)} {random.choice(surnames)}"
            else:  # Orchestra
                name = f"{random.choice(orchestra_names)} {random.choice(surnames)}"
            
            if random.random() > 0.6:
                name += f" {random.choice(adjectives).strip('הה')}"
                
            s = Supplier(
                name=name,
                supplier_type=sType,
                city=random.choice(cities),
                price=random.randint(1000, 20000) if sType != 'Catering' else random.randint(120, 600),
                phone=f"05{random.randint(0, 9)}-{random.randint(1000000, 9999999)}",
                image_url=get_supplier_image(sType, sSubtype)
            )
            db.session.add(s)

        db.session.commit()
        print("✅ Data seeded successfully with STRICT VISUAL LOGIC!")

if __name__ == '__main__':
    seed_data()
