import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Login = () => {
  return (
    <div className="min-h-screen flex items-center justify-center pt-20 relative overflow-hidden">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/90 backdrop-blur-xl p-8 md:p-12 rounded-2xl shadow-2xl text-center max-w-md w-full relative z-10 border border-white/50"
      >
        <h2 className="text-3xl font-bold text-[#800020] mb-2">ברוכים השבים</h2>
        <p className="text-gray-500 mb-8">התחברו לחשבון שלכם</p>
        
        <div className="space-y-4">
          <div className="h-12 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-center text-gray-400">
            טופס התחברות בבנייה...
          </div>
          <button className="btn btn-primary w-full">
            התחבר
          </button>
        </div>

        <div className="mt-6 text-sm text-gray-500">
          עדיין אין לך חשבון?{' '}
          <Link to="/register" className="text-[#800020] font-bold hover:underline">
            הירשם עכשיו
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
