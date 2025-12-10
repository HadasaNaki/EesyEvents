import React from 'react';

const Footer = () => {
  return (
    <footer className="main-footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>🎉 EasyVents</h3>
            <p>פלטפורמה חכמה לניהול אירועים - חתונות, בר/בת מצוות ואירועים עסקיים</p>
          </div>
          <div className="footer-section">
            <h4>קישורים מהירים</h4>
            <ul>
              <li><a href="#home">דף הבית</a></li>
              <li><a href="#features">תכונות</a></li>
              <li><a href="#about">אודות</a></li>
              <li><a href="#contact">צור קשר</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>תמיכה</h4>
            <ul>
              <li><a href="#">מרכז עזרה</a></li>
              <li><a href="#">שאלות נפוצות</a></li>
              <li><a href="#">תנאי שימוש</a></li>
              <li><a href="#">מדיניות פרטיות</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>צור קשר</h4>
            <ul>
              <li>📧 info@easyvents.co.il</li>
              <li>📱 03-1234567</li>
              <li>📍 תל אביב, ישראל</li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 EasyVents. כל הזכויות שמורות.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
