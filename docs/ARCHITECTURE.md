# EasyVents - מפת ארכיטקטורה (Python Flask Only)

מסמך זה מתאר את המבנה הארכיטקטוני של המערכת לאחר המעבר ל-Flask מלא.

## 🔄 תרשים זרימה כללי

המערכת בנויה בארכיטקטורת **Server-Side Rendering (SSR)**:

1.  **Server (השרת)**: שרת Python Flask שמגיש דפי HTML מוכנים (Templates) ומנהל את ה-API.
2.  **Client (הלקוח)**: דפדפן שמציג את ה-HTML ומריץ JavaScript מינימלי לאינטראקציות.
3.  **Database (מסד הנתונים)**: קובץ SQLite ששומר את המידע.

---

## 📂 מבנה הפרויקט

```
easyevent/
├── backend/
│   ├── app.py                    # שרת Flask ראשי
│   ├── templates/                # קבצי HTML (Jinja2)
│   │   ├── base.html             # תבנית בסיס (Header/Footer)
│   │   ├── index.html            # דף הבית
│   │   ├── login.html            # דף התחברות
│   │   └── register.html         # דף הרשמה
│   └── static/                   # קבצים סטטיים
│       ├── css/                  # סגנונות (Tailwind מורץ)
│       ├── js/                   # סקריפטים
│       └── images/               # תמונות ולוגו
├── database/
│   └── easyevents.db             # מסד הנתונים
└── requirements.txt              # תלויות Python
```

---

## 🛠️ איך זה עובד?

### הגשת דפים (Routing)
*   כשהמשתמש נכנס ל-`/`, השרת מריץ את הפונקציה `index()` ב-`app.py`.
*   הפונקציה מחזירה את `render_template('index.html')`.
*   `index.html` יורש מ-`base.html`, שמכיל את ה-Header, Footer וקישורים ל-CSS.

### אינטראקציות (Forms & API)
*   טפסי התחברות והרשמה משתמשים ב-JavaScript (בתוך ה-HTML או ב-`main.js`) כדי לשלוח בקשות `fetch` לשרת.
*   השרת מעבד את הבקשה בנתיבי `/api/...` ומחזיר JSON.
*   ה-JavaScript בדפדפן מקבל את התשובה ומבצע הפניה (Redirect) או מציג שגיאה.

---

## 📝 מדריך לעריכה

### שינוי עיצוב
*   ערוך את קבצי ה-HTML בתיקיית `backend/templates/`.
*   העיצוב מבוסס על Tailwind CSS שכבר קומפל לתוך `backend/static/css/style.css`.
*   לשינויים קטנים, ניתן להוסיף `style` בתוך ה-HTML או לערוך את ה-CSS ישירות (זהירות, הוא קובץ גדול).

### שינוי לוגיקה
*   ערוך את `backend/app.py` לשינוי התנהגות השרת, אימות נתונים, או עבודה מול מסד הנתונים.

### הוספת דף חדש
1.  צור קובץ HTML חדש ב-`backend/templates/` (למשל `about.html`).
2.  הוסף לו `{% extends "base.html" %}`.
3.  הוסף נתיב חדש ב-`backend/app.py`:
    ```python
    @app.route('/about')
    def about():
        return render_template('about.html')
    ```
