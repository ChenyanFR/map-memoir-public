import React from 'react';
import { motion } from 'framer-motion';
import { 
  HeartIcon, 
  MapIcon, 
  SparklesIcon,
  GlobeAltIcon 
} from '@heroicons/react/24/outline';

const Footer = () => {
  return (
    <motion.footer
      className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white mt-20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="relative">
                <MapIcon className="w-8 h-8 text-primary-400" />
                <SparklesIcon className="w-4 h-4 text-yellow-400 absolute -top-1 -right-1" />
              </div>
              <h3 className="text-2xl font-serif font-bold">Map Memoir</h3>
            </div>
            <p className="text-gray-300 mb-6 leading-relaxed">
              Transform your favorite places into captivating stories with the power of AI. 
              Every location has a tale to tell, and we help you discover it.
            </p>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <span>Made with</span>
              <HeartIcon className="w-4 h-4 text-red-400" />
              <span>using AI technology</span>
            </div>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-primary-300">Features</h4>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                <span>AI Story Generation</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                <span>Interactive Maps</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                <span>Voice Narration</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                <span>Multiple Themes</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                <span>Story Sharing</span>
              </li>
            </ul>
          </div>

          {/* Technology */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-primary-300">Powered By</h4>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-center space-x-2">
                <GlobeAltIcon className="w-4 h-4 text-blue-400" />
                <span>Google Maps API</span>
              </li>
              <li className="flex items-center space-x-2">
                <SparklesIcon className="w-4 h-4 text-yellow-400" />
                <span>Gemini AI</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gradient-to-r from-blue-400 to-purple-400 rounded"></div>
                <span>React & Vite</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gradient-to-r from-green-400 to-blue-400 rounded"></div>
                <span>Tailwind CSS</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gradient-to-r from-purple-400 to-pink-400 rounded"></div>
                <span>Framer Motion</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2025 Map Memoir. Crafted with passion for storytelling.
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <motion.a 
                href="#" 
                className="hover:text-primary-400 transition-colors"
                whileHover={{ scale: 1.05 }}
              >
                Privacy Policy
              </motion.a>
              <motion.a 
                href="#" 
                className="hover:text-primary-400 transition-colors"
                whileHover={{ scale: 1.05 }}
              >
                Terms of Service
              </motion.a>
              <motion.a 
                href="#" 
                className="hover:text-primary-400 transition-colors"
                whileHover={{ scale: 1.05 }}
              >
                About
              </motion.a>
            </div>
          </div>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
