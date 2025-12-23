# 🎉 EasyVents - Platform for Event Management & Production

[![GitHub](https://img.shields.io/badge/GitHub-EesyEvents-blue)](https://github.com/HadasaNaki/EesyEvents)
[![Status](https://img.shields.io/badge/Status-Active%20Development-success)]()
[![Tech Stack](https://img.shields.io/badge/Stack-Python%20Flask-blueviolet)]()

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

### Architecture: Python Flask (SSR)
The application uses a robust **Flask** backend with server-side rendering:

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend** | Python Flask | 3.1.2 | Web Server & API |
| **Templating** | Jinja2 | Built-in | HTML Rendering |
| **Styling** | Tailwind CSS | 3.4.1 | Modern responsive design (Pre-compiled) |
| **Database** | SQLite | Built-in | User data & event management |
| **Security** | Werkzeug | 3.1.3 | Secure authentication |
| **CORS** | Flask-CORS | 6.0.1 | Cross-origin requests |

---

## 📁 **מבנה הפרויקט - איפה כל דבר נמצא**

```
easyevent/
├── backend/
│   ├── app.py                    # שרת Flask ראשי
│   ├── templates/                # קבצי HTML
│   │   ├── base.html             # תבנית בסיס
│   │   ├── index.html            # דף הבית
│   │   ├── login.html            # דף התחברות
│   │   └── register.html         # דף הרשמה
│   └── static/                   # קבצים סטטיים
│       ├── css/                  # סגנונות
│       ├── js/                   # סקריפטים
│       └── images/               # תמונות
├── database/
│   └── easyevents.db             # מסד הנתונים
└── README.md                     # קובץ זה
```

---

## 🚀 **איך להריץ את הפרויקט**

### התקנה ראשונית:
```bash
# התקן תלויות Python
pip install -r requirements.txt
```

### הרצה:
```bash
# הרץ את השרת
python backend/app.py
```

האתר יהיה זמין בכתובת: `http://localhost:5000`

---

## 🎨 עיצוב וממשק משתמש

הפרויקט משתמש בעיצוב יוקרתי המבוסס על פלטת צבעים של בורדו, זהב ובז'.
העיצוב מיושם באמצעות Tailwind CSS וכולל אנימציות CSS מותאמות אישית לחווית משתמש חלקה.

---

## 🔒 אבטחה

- **סיסמאות**: מוצפנות באמצעות `Werkzeug` (PBKDF2).
- **אימות**: בדיקות תקינות בצד הלקוח ובצד השרת.
- **SQL Injection**: שימוש בפרמטרים מוגנים בשאילתות.
