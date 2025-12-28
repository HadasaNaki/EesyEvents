# EasyEvents - Setup Guide

## For Team Members

### Step 1: Clone or Update Repository
If you haven't cloned yet:
```bash
git clone https://github.com/HadasaNaki/EesyEvents.git
cd EesyEvents
git checkout main
```

If you already cloned:
```bash
git fetch origin
git reset --hard origin/main
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Flask Server
```bash
python backend/app.py
```

Server will run at: `http://localhost:5000`

### Step 5: Access the Website
- **Home:** http://localhost:5000
- **Planning:** http://localhost:5000/plan
- **Results:** http://localhost:5000/results

---

## Current Features

✅ **Database**
- SQLite with SQLAlchemy ORM
- 20 Venues + 54 Suppliers
- User authentication system

✅ **Frontend**
- Hebrew RTL support
- Icon-based card design
- Responsive grid layout (3-2-1 columns)
- Beautiful typography (Assistant + Rubik fonts)

✅ **API Endpoints**
- GET /api/venues - All venues
- GET /api/suppliers - All suppliers
- GET /api/suppliers/<type> - By category
- GET /api/stats - Database statistics
- POST /api/register - User registration
- POST /api/login - User login

---

## Project Structure
```
EesyEvents/
├── backend/
│   ├── app.py              # Flask application & routes
│   ├── templates/          # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── index.html     # Home page
│   │   ├── plan.html      # Event planning form
│   │   ├── results.html   # Results with venues & suppliers
│   │   ├── login.html     # Login page
│   │   └── register.html  # Registration page
│   └── static/            # CSS, JS, images
├── database/
│   └── easyevents.db      # SQLite database
├── requirements.txt       # Python dependencies
└── DESIGN_GUIDELINES.md   # UI/UX documentation
```

---

## Troubleshooting

### Pull doesn't show changes
Try:
```bash
git fetch origin
git reset --hard origin/main
```

### Flask server won't start
1. Make sure virtual environment is activated
2. Check Python version: `python --version` (should be 3.8+)
3. Reinstall dependencies: `pip install -r requirements.txt`

### Database issues
Delete old database and restart:
```bash
rm database/easyevents.db
python backend/app.py
```

---

## Recent Changes (Dec 25, 2025)

🎨 **UI/UX Improvements:**
- Refactored results page with icon-based card design
- Added location badges to cards
- Implemented clean stat rows (capacity, price icons)
- Added cuisine type tags for catering
- Save/favorite heart button on each card

📊 **Data Expansion:**
- Increased venues from 3 to 20
- Increased suppliers from 7 to 54
- Added 4 catering cuisine types (בשרי, חלבי, טבעוני, שף פרטי)

📝 **Documentation:**
- Created DESIGN_GUIDELINES.md
- Created UX_WRITING_GUIDE.md
- Added comprehensive comments in code

---

**Questions?** Check DESIGN_GUIDELINES.md for UI details.
