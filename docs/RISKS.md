# 🛡️ ניהול סיכונים (Risk Management) - Project EesyEvents

מסמך זה מפרט ומנתח את הסיכונים הפוטנציאליים בפיתוח ותחזוקת מערכת EesyEvents.
הסיכונים ממוינים בסדר יורד לפי **רמת הסיכון (Risk Level)** ו**הסבירות (Likelihood)**.

---

## 📊 RMMM Plan (Risk Mitigation, Monitoring, and Management)
עבור 3 הסיכונים הקריטיים ביותר (High Impact / High Probability).

### 1. 🚨 אובדן נתונים קריטי בבסיס הנתונים (Data Loss)
*   **רמת סיכון:** 1 (High - Catastrophic)
*   **סבירות:** High
*   **תיאור:** קריסת שרת, פגם בתוכנה או טעות אנוש הגורמת למחיקת פרטי אירועים, רשימות מוזמנים או מידע על ספקים.

**תוכנית פעולה (Mitigation):**
*   הגדרת גיבויים אוטומטיים (Automated Backups) כל 6 שעות לשרת מרוחק (Cloud Storage).
*   שימוש ב-Replica Set ל-DB כדי להבטיח זמינות מיידית במקרה של נפילת השרת הראשי.
*   הגבלת גישת מחיקה (DROP/DELETE) למנהלי מערכת בלבד ברמת ה-Production.

**מעקב (Monitoring):**
*   סקריפט יומי שבודק את תקינות קבצי הגיבוי ואת גודלם (מוודא שהגיבוי לא ריק).
*   התראות אוטומטיות למייל/SMS למנהל המערכת במקרה של כישלון בגיבוי.

**תוכנית מגירה (Contingency):**
*   שחזור מיידי (Point-in-time recovery) מהגיבוי התקין האחרון.
*   הודעה למשתמשים על חלון זמן של אובדן מידע (אם קיים) ומתן שירות VIP להזנה מחדש של נתונים שאבדו ידנית ע"י צוות תמיכה.

---

### 2. 🔓 פרצת אבטחה ודליפת פרטי משתמשים (Security Breach)
*   **רמת סיכון:** 1 (High - Catastrophic)
*   **סבירות:** Medium
*   **תיאור:** האקרים מנצלים חולשות (כגון SQL Injection) כדי לגנוב רשימות מוזמנים, טלפונים של ספקים או סיסמאות.

**תוכנית פעולה (Mitigation):**
*   שימוש ב-SQLAlchemy ORM בלבד (מונע SQL Injection באופן מובנה) במקום שאילתות ידניות.
*   הצפנת סיסמאות באמצעות `werkzeug.security` (PBKDF2/SHA256) כפי שמיושם במערכת.
*   ולידציה מחמירה (Server-side validation) על כל הקלטים המגיעים מהמשתמש.

**מעקב (Monitoring):**
*   הגדרת Logs לניסיונות התחברות כושלים ושימוש ב-Rate Limiting לחסימת ניסיונות Brute Force.
*   ביצוע סריקת קוד (Static Code Analysis) בכל העלאה לגיט לאיתור חולשות אבטחה.

**תוכנית מגירה (Contingency):**
*   השבתת הגישה למערכת באופן יזום עד לתיקון הפרצה.
*   איפוס סיסמאות יזום לכל המשתמשים ושליחת הודעת עדכון על אירוע האבטחה בהתאם לחוק.

---

### 3. 📉 קריסת המערכת בעומס משתמשים (System Crash / Performance)
*   **רמת סיכון:** 2 (Medium - Critical)
*   **סבירות:** High
*   **תיאור:** בעונת החתונות, ריבוי משתמשים מעלים תמונות בו-זמנית גורם לשרת "להיחנק" ולקרוס (Timeout).

**תוכנית פעולה (Mitigation):**
*   אופטימיזציה של תמונות בצד השרת לפני שמירה (כיווץ גודל ורזולוציה).
*   העברת קבצים סטטיים (תמונות, CSS) ל-CDN חיצוני ולא ישירות מהשרת.
*   שימוש ב-Gunicorn עם מספר Workers במקום שרת הפיתוח של Flask.

**מעקב (Monitoring):**
*   ניטור בזמן אמת של CPU ו-RAM בשרת (באמצעות כלי כמו New Relic או Datadog).
*   בדיקת זמני טעינה (Latency) והתראה כשהזמן עולה על 2 שניות.

**תוכנית מגירה (Contingency):**
*   הפעלה אוטומטית של שרתים נוספים (Auto-scaling) ב-Azure/AWS.
*   העברת האתר למצב "Read Only" (צפייה בלבד) זמנית כדי להוריד עומס מה-DB.

---

## 📋 רשימת הסיכונים המלאה (Risk Assessment Table)

| # | שם הסיכון | קטגוריה (Category) | סוג סיכון (Type) | סבירות (Likelihood) | רמת סיכון (Severity) |
|---|-----------|-------------------|------------------|---------------------|----------------------|
| **1** | **אובדן נתונים ב-DB** | Technology (TE) | Performance | High | **1 - High** |
| **2** | **פרצת אבטחה (Data Leak)** | Technology (TE) | Support | Medium | **1 - High** |
| **3** | **קריסה תחת עומס** | Dev Env (DE) | Performance | High | **2 - Medium** |
| **4** | **אי-תאימות למובייל** | Customer (CU) | Performance | High | **2 - Medium** |
| **5** | **חריגה בתקציב (ענן/שרתים)** | Business (BU) | Cost | Medium | **2 - Medium** |
| **6** | **ממשק משתמש מסורבל (UX)** | Customer (CU) | Support | Medium | **2 - Medium** |
| **7** | **באגים קריטיים ב-Production** | Process (PR) | Performance | Medium | **2 - Medium** |
| **8** | **תקלות באינטגרציה חיצונית** | Technology (TE) | Performance | Medium | **2 - Medium** |
| **9** | **עיכוב בשל חוסר כוח אדם** | Staff (ST) | Schedule | Low | **2 - Medium** |
| **10** | **חוסר בבדיקות אוטומטיות** | Process (PR) | Support | High | **3 - Low** |
| **11** | **קונפליקטים במיזוג קוד (Git)** | Process (PR) | Schedule | High | **3 - Low** |
| **12** | **איטיות בטעינת תמונות** | Product Size (PS) | Performance | High | **3 - Low** |
| **13** | **בעיות תאימות דפדפנים** | Customer (CU) | Support | Medium | **3 - Low** |
| **14** | **שגיאות בהגדרת סביבת פיתוח** | Dev Env (DE) | Schedule | Medium | **3 - Low** |
| **15** | **חוסר תיעוד טכני** | Staff (ST) | Support | Medium | **3 - Low** |
| **16** | **דרישות משתנות של הלקוח** | Business (BU) | Schedule | Medium | **3 - Low** |
| **17** | **שגיאות כתיב/תוכן באתר** | Product Size (PS) | Support | Medium | **4 - Negligible** |
| **18** | **זיהוי מיילים כספאם** | Technology (TE) | Performance | Medium | **4 - Negligible** |
| **19** | **עיצוב לא אחיד (CSS)** | Product Size (PS) | Performance | High | **4 - Negligible** |
| **20** | **תקלות בסביבת Staging** | Dev Env (DE) | Schedule | Low | **4 - Negligible** |

### 🔍 מקרא (Legend)
*   **רמת סיכון:** 1 (קריטי) עד 4 (זניח).
*   **קטגוריות:** TE (Technology), DE (Development Env), CU (Customer), BU (Business), PR (Process), ST (Staff), PS (Product Size).
*   **סוגים:** Performance (ביצועים), Cost (עלות), Support (תחזוקה), Schedule (לו"ז).
