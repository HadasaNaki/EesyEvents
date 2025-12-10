import React from 'react';
import Hero from './Hero';
import { motion } from 'framer-motion';

const LandingPage = () => {
  return (
    <main className="main-content">
      <Hero />
      
      {/* Event Types Section */}
      <section className="event-types-section">
        <div className="container">
          <h2 className="section-title">סוגי אירועים שאנחנו תומכים בהם</h2>
          <p className="section-subtitle">תכנון מקצועי לכל סוג של אירוע</p>
          <div className="event-types-grid">
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="event-type-card"
            >
              <img 
                src="https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2069&auto=format&fit=crop" 
                alt="חתונות" 
                className="event-image"
              />
              <h3>חתונות</h3>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="event-type-card"
            >
              <img 
                src="https://images.unsplash.com/photo-1513151233558-d860c5398176?q=80&w=2070&auto=format&fit=crop" 
                alt="בר/בת מצווה" 
                className="event-image"
              />
              <h3>בר/בת מצווה</h3>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="event-type-card"
            >
              <img 
                src="https://images.unsplash.com/photo-1541532713592-79a0317b6b77?q=80&w=1888&auto=format&fit=crop" 
                alt="מסיבות רווקות" 
                className="event-image"
              />
              <h3>מסיבות רווקות</h3>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="event-type-card"
            >
              <img 
                src="https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=2069&auto=format&fit=crop" 
                alt="אירועים עסקיים" 
                className="event-image"
              />
              <h3>אירועים עסקיים</h3>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="container">
          <h2 className="section-title">איך זה עובד?</h2>
          <p className="section-subtitle">4 שלבים פשוטים לאירוע מושלם</p>
          <div className="steps-grid">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="step-card"
            >
              <div className="step-number">1</div>
              <h3>הירשם והתחבר</h3>
              <p>פתח חשבון אישי בקלות תוך דקה</p>
            </motion.div>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="step-card"
            >
              <div className="step-number">2</div>
              <h3>צור אירוע חדש</h3>
              <p>הגדר את סוג האירוע, תאריך ותקציב</p>
            </motion.div>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="step-card"
            >
              <div className="step-number">3</div>
              <h3>נהל ותכנן</h3>
              <p>הוסף משימות, בחר ספקים ושלח הזמנות</p>
            </motion.div>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="step-card"
            >
              <div className="step-number">4</div>
              <h3>תהנה מהאירוע</h3>
              <p>הגע רגוע לאירוע המושלם שלך</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <motion.h2
               initial={{ opacity: 0, scale: 0.9 }}
               whileInView={{ opacity: 1, scale: 1 }}
               viewport={{ once: true }}
            >
              מוכנים להתחיל את התכנון?
            </motion.h2>
            <p>הצטרפו אלינו והפכו את האירוע שלכם למציאות</p>
            <a href="/register" className="btn btn-large btn-cta">צור אירוע חדש</a>
          </div>
        </div>
      </section>
    </main>
  );
};

export default LandingPage;
