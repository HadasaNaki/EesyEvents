# 🎉 EasyVents - Platform for Event Management & Production

[![GitHub](https://img.shields.io/badge/GitHub-EesyEvents-blue)](https://github.com/HadasaNaki/EesyEvents)
[![Status](https://img.shields.io/badge/Status-Active%20Development-success)]()
[![Tech Stack](https://img.shields.io/badge/Stack-React%20%2B%20Python-blueviolet)]()

## 📖 Project Description

**EasyVents** is a professional platform for planning and managing events - weddings, bar/bat mitzvahs, bachelorette parties, and business events.

The system centralizes all production stages in one place:
- ✅ Budget planning
- 👥 Vendor selection
- 📋 Task management
- 📧 Digital invitations
- 📅 Scheduling and coordination
- 🎨 Luxury event design features

### 🎯 Project Goal
To provide users with a simple, comfortable, and professional planning experience, while saving time and preventing errors. With a focus on **modern luxury design** and **seamless user experience**.

---

## 👥 Development Team

- **Efrat Brinkman** - 215704883
- **Hillel Uchana** - 327605234
- **Hadasa Naki** - 327787628

**Institution:** Lev Academic Center (JCT)  
**Start Date:** October 22, 2025

---

## 🛠️ Tech Stack

### Architecture: Full Stack (React + Python)
The application uses a **modern, professional separation** between frontend and backend:

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Frontend** | React 18.2 + Vite | Latest | Modern, fast UI with smooth animations |
| **State Management** | Framer Motion | 11.0.0 | Luxury animations & transitions |
| **Routing** | React Router DOM | 6.22.0 | Client-side navigation |
| **Styling** | Tailwind CSS + Custom CSS | 3.4.1 | Modern responsive design |
| **Backend** | Python Flask | 3.1.2 | REST API server |
| **Database** | SQLite | Built-in | User data & event management |
| **Security** | Werkzeug (Password Hashing) | 3.1.3 | Secure authentication |
| **CORS** | Flask-CORS | 6.0.1 | Cross-origin requests |
| **Build Tool** | Vite | 5.4.21 | Fast development & production builds |
| **Version Control** | Git & GitHub | - | Collaborative development |

### Design Features
- **Typography:** Heebo (Modern Bold Sans-Serif) for luxury presentation
- **Color Scheme:** Burgundy (#800020) & Beige (#F0E6D2) gradient
- **Visual Effects:** Gold accents, sophisticated shadows, smooth animations
- **Responsive:** Mobile-first design with Tailwind CSS

### 📦 Python Dependencies
See `requirements.txt` for complete list of all packages and versions.

---

## 📁 Project Structure

```
easyevent/
│
├── 📂 frontend/                    # React + Vite Frontend (Modern SPA)
│   ├── index.html                  # Main HTML entry point
│   ├── package.json                # Frontend dependencies (React, Vite, etc)
│   ├── vite.config.js              # Vite build configuration
│   ├── tailwind.config.js          # Tailwind CSS configuration
│   ├── postcss.config.js           # PostCSS configuration
│   │
│   ├── 📂 public/                  # Static assets
│   │   └── logo.png                # Company logo
│   │
│   └── 📂 src/                     # React source code
│       ├── main.jsx                # React app entry point
│       ├── App.jsx                 # Main App component
│       ├── index.css               # Global styles + custom design
│       │
│       └── 📂 components/          # React Components
│           ├── Header.jsx          # Navigation header (Framer Motion)
│           ├── Hero.jsx            # Hero section with luxury title
│           ├── LandingPage.jsx      # Main landing page layout
│           ├── Footer.jsx          # Footer component
│           ├── Login.jsx           # User login form
│           └── Register.jsx        # User registration form
│
├── 📂 backend/                     # Python Flask API Server
│   └── app.py                      # Flask REST API with endpoints
│
├── 📂 database/                    # Database files
│   └── easyevents.db               # SQLite database (auto-created)
│
├── 📂 docs/                        # Documentation
│
├── Configuration Files:
│   ├── .gitignore                  # Git ignore rules
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # This file
│
└── 📂 .venv/                       # Python virtual environment (auto-created)
```

---

## 🚀 Installation & Setup Guide

### ✅ Prerequisites
- **Python 3.8+** installed
- **Node.js 16+** and **npm** installed (for React/Vite)
- **Git** installed
- Modern web browser (Chrome, Firefox, Edge)
- Code editor (VS Code recommended)

### 📥 Installation Steps

#### Step 1: Clone the Repository
```bash
git clone https://github.com/HadasaNaki/EesyEvents.git
cd easyevent
```

#### Step 2: Create Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Install Frontend Dependencies (React/Vite)
```bash
cd frontend
npm install
cd ..
```

#### Step 5: Start the Backend Server
**In a terminal window (venv activated):**
```bash
python backend/app.py
```
✅ Backend runs on: `http://localhost:5000`

You'll see:
```
✅ Database initialized successfully!
🚀 Starting EasyVents API Server...
📍 Server running on: http://localhost:5000
```

#### Step 6: Start the Frontend Development Server
**In a new terminal window (from the frontend folder):**
```bash
cd frontend
npm run dev
```
✅ Frontend runs on: `http://localhost:5173`

You'll see:
```
VITE v5.4.21  ready in 2116 ms
➜  Local:   http://localhost:5173/
```

#### ✨ Access the Application
Open your browser and navigate to:
```
http://localhost:5173
```

---

## 📖 Available Scripts

### Frontend Commands
```bash
cd frontend

# Development mode (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run ESLint
npm run lint
```

### Backend Commands
```bash
# Start Flask server (from project root, with venv activated)
python backend/app.py

# Server runs on http://localhost:5000
```

### ⚙️ Troubleshooting

#### Issue: Port 5000 already in use
```bash
# Windows - Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

#### Issue: Port 5173 already in use
```bash
# Kill Vite development server or use a different port
cd frontend
npm run dev -- --port 5174
```

#### Issue: npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -r node_modules package-lock.json

# Reinstall
npm install
```

#### Issue: Python dependencies not installing
```bash
# Ensure venv is activated, then upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔄 Git Workflow

### Creating a Feature Branch
```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your_feature_name

# Examples:
git checkout -b feature/event_dashboard
git checkout -b fix/styling_issue
```

### Making Changes & Committing
```bash
# Check status
git status

# Add files
git add .

# Commit with clear message
git commit -m "Descriptive message about changes"
```

### Pushing Changes
```bash
# Push to remote
git push -u origin feature/your_feature_name

# Subsequent pushes
git push
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### User Registration
```
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password"
}
```

#### User Login
```
POST /api/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password"
}
```

#### Get All Users (for development)
```
GET /api/users
```

---

## 🎨 Design System

### Color Palette
- **Primary Burgundy:** `#800020`
- **Dark Burgundy:** `#660018`
- **Beige/Cream:** `#F0E6D2`
- **Gold Accent:** `#C5A059`
- **Background Gradient:** `#4a0015 → #F0E6D2`

### Typography
- **Display Font:** Heebo (Bold, Black 900)
- **Body Font:** Rubik (Regular, 400-700)
- **UI Font:** Assistant (Clean, Modern)

### Visual Effects
- **Shadows:** Gold accents with soft drop shadows
- **Animations:** Framer Motion for smooth transitions
- **Responsive:** Mobile-first design approach

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Frontend (React + Vite)** | ✅ Active | Modern SPA with luxury design |
| **Backend (Flask API)** | ✅ Active | User authentication & database |
| **Database (SQLite)** | ✅ Active | User management |
| **Authentication** | ✅ Complete | Secure password hashing |
| **Responsive Design** | ✅ Complete | Mobile & desktop support |
| **Animations** | ✅ Complete | Framer Motion integration |

---

## 📝 TODO List

### ✅ Completed
- [x] Basic HTML/CSS structure
- [x] Navigation menu
- [x] Complete landing page
- [x] Registration form
- [x] Login form
- [x] **Professional Backend (Flask + SQLite)** ✨
- [x] **User authentication with password hashing** ✨
- [x] **React + Vite Setup** ✨
- [x] **Luxury Visual Design (Heebo font, gold accents)** ✨

### 🔄 In Progress
- [ ] User dashboard
- [ ] Event creation & management
- [ ] Vendor marketplace
- [ ] Budget planning tools
- [ ] Task management system
- [ ] Digital invitations

### 📅 Planned
- [ ] Mobile app (React Native)
- [ ] AI-powered vendor recommendations
- [ ] Payment integration
- [ ] Email notifications
- [ ] Analytics & reporting

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Rules
- Always create a new branch for features
- Write clear commit messages
- Test your changes before pushing
- Update README if adding new features

---

## 📞 Support & Contact

For issues or questions:
1. Check existing GitHub issues
2. Create a new GitHub issue with detailed description
3. Contact the development team

---

## 📄 License

This project is part of the JCT Lev Academic Center curriculum.

---

## 🎯 Next Steps

1. **Clone the repository**
2. **Follow the Installation section above**
3. **Start coding!** 🚀

---

**Last Updated:** December 10, 2025  
**Version:** 2.0.0 (React + Python)
- [x] **API RESTful מלא** ✨
- [x] **בסיס נתונים SQLite** ✨

### 🚧 בתהליך
- [ ] דף ניהול אירועים (Dashboard)
- [ ] דף יצירת אירוע חדש
- [ ] אזור אישי למשתמש מחובר

### 📅 לעתיד
- [ ] מערכת ניהול תקציב
- [ ] חיפוש וסינון ספקים
- [ ] מערכת משימות (To-Do)
- [ ] הזמנות דיגיטליות
- [ ] אינטגרציה עם Google Calendar
- [ ] מערכת דירוגים וחוות דעת

---

## 🐛 דיווח על באגים

אם מצאת באג, פתח issue ב-GitHub עם:
1. תיאור הבעיה
2. צעדים לשחזור
3. התנהגות צפויה vs. התנהגות בפועל
4. צילומי מסך (אם רלוונטי)

---

## 📞 צור קשר

- **Repository:** https://github.com/HadasaNaki/EesyEvents
- **Issues:** https://github.com/HadasaNaki/EesyEvents/issues

---

## 📄 רישיון

© 2025 EasyVents. כל הזכויות שמורות.

פרויקט אקדמי - המכון האקדמי לב (JCT)

---

## 🎓 הערות למפתחים

### שימושיות
- **כל שינוי צריך להיות בברנץ' נפרד**
- **אל תעבוד ישירות על main**
- **תמיד עדכן את הברנץ' שלך לפני תחילת עבודה**
- **כתוב הודעות קומיט ברורות ומפורטות**
- **סקור את הקוד של חברי הצוות**

### טיפים
- השתמש ב-Git Extensions או SourceTree לניהול ויזואלי
- הגדר .gitignore נכון כדי לא להעלות קבצים מיותרים
- צור commits קטנים ותכופים במקום אחד גדול
- בדוק את הקוד לפני push (בדיקת syntax, styling)

---

**בהצלחה בפיתוח! 🚀**
