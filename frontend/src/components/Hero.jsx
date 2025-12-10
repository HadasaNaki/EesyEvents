import React from 'react';
import { motion } from 'framer-motion';

const Hero = () => {
  return (
    <section className="hero-section" id="home">
      <div className="container">
        <div className="hero-content">
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="hero-title"
          >
            פסגת האירוח וההפקה
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
            className="hero-subtitle"
          >
            חוויה אקסקלוסיבית של דיוק, אלגנטיות וטעם משובח.<br/>
            הפלטפורמה שמעניקה לאירוע שלך את המעמד הראוי לו.
          </motion.p>
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="hero-buttons"
          >
            <a href="/register" className="btn btn-hero-primary">התחל לתכנן</a>
            <button className="btn btn-hero-secondary">גלה עוד</button>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
