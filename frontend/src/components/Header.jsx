import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Header = () => {
  return (
    <motion.header 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="main-header"
    >
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <Link to="/">
              <img src="/logo.png" alt="EasyVents" className="logo-img" />
            </Link>
          </div>
          
          <nav className="main-nav hidden md:block">
            <ul>
              {['דף הבית', 'תכונות', 'אודות', 'צור קשר'].map((item) => (
                <li key={item}>
                  <a href={`#${item === 'דף הבית' ? 'home' : 'features'}`}>
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div className="header-actions">
            <Link to="/login" className="btn btn-secondary">
              התחבר
            </Link>
            <Link to="/register" className="btn btn-primary">
              הרשם
            </Link>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
