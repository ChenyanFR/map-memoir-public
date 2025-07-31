import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  DocumentTextIcon, 
  EyeIcon, 
  BeakerIcon, 
  HeartIcon,
  FilmIcon,
  BookOpenIcon,
  GlobeAltIcon 
} from '@heroicons/react/24/outline';

const themes = [
  {
    id: 'fairy-tale',
    name: 'Fairy Tale',
    description: 'Magical and whimsical storytelling with enchanted elements',
    icon: SparklesIcon,
    color: 'from-purple-500 to-pink-500',
    emoji: '🧚‍♀️'
  },
  {
    id: 'documentary',
    name: 'Documentary',
    description: 'Factual and informative narrative with historical insights',
    icon: DocumentTextIcon,
    color: 'from-blue-500 to-cyan-500',
    emoji: '📚'
  },
  {
    id: 'mystery',
    name: 'Mystery',
    description: 'Intriguing and suspenseful tales with hidden secrets',
    icon: EyeIcon,
    color: 'from-gray-700 to-gray-900',
    emoji: '🔍'
  },
  {
    id: 'adventure',
    name: 'Adventure',
    description: 'Thrilling journeys and exciting explorations',
    icon: GlobeAltIcon,
    color: 'from-green-500 to-emerald-500',
    emoji: '🗺️'
  },
  {
    id: 'romance',
    name: 'Romance',
    description: 'Beautiful love stories and heartwarming moments',
    icon: HeartIcon,
    color: 'from-rose-500 to-pink-500',
    emoji: '💕'
  },
  {
    id: 'sci-fi',
    name: 'Sci-Fi',
    description: 'Futuristic tales with technological wonders',
    icon: BeakerIcon,
    color: 'from-indigo-500 to-purple-500',
    emoji: '🚀'
  },
  {
    id: 'historical',
    name: 'Historical',
    description: 'Stories from the past with period authenticity',
    icon: BookOpenIcon,
    color: 'from-amber-500 to-orange-500',
    emoji: '📜'
  },
  {
    id: 'thriller',
    name: 'Thriller',
    description: 'Edge-of-your-seat suspense and intense drama',
    icon: FilmIcon,
    color: 'from-red-500 to-rose-500',
    emoji: '🎬'
  }
];

function ThemeSelector({ onSelect, selectedPlace }) {
  const [hoveredTheme, setHoveredTheme] = useState(null);

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="card">
        <div className="mb-8">
          <h2 className="section-title">🎨 Choose Your Story Theme</h2>
          <p className="section-subtitle">
            How would you like to tell the story of <span className="font-semibold text-primary-600">{selectedPlace?.name}</span>?
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {themes.map((theme, index) => {
            const IconComponent = theme.icon;
            return (
              <motion.button
                key={theme.id}
                onClick={() => onSelect(theme.name)}
                onMouseEnter={() => setHoveredTheme(theme.id)}
                onMouseLeave={() => setHoveredTheme(null)}
                className="group relative p-6 rounded-2xl border border-gray-200 bg-white hover:bg-gray-50 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-primary-200 text-left"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.5 }}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                {/* Background Gradient */}
                <div className={`absolute inset-0 bg-gradient-to-br ${theme.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded-lg bg-gradient-to-br ${theme.color} group-hover:scale-110 transition-transform duration-300`}>
                      <IconComponent className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-2xl">{theme.emoji}</span>
                  </div>
                  
                  <h3 className="font-semibold text-gray-800 mb-2 group-hover:text-gray-900">
                    {theme.name}
                  </h3>
                  
                  <p className="text-sm text-gray-600 group-hover:text-gray-700 leading-relaxed">
                    {theme.description}
                  </p>
                </div>

                {/* Hover Effect Border */}
                <div className={`absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-primary-200 transition-colors duration-300`}></div>
              </motion.button>
            );
          })}
        </div>
        
        {hoveredTheme && (
          <motion.div
            className="mt-6 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl border border-primary-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <p className="text-sm text-primary-700 font-medium">
              💡 <span className="font-semibold">{themes.find(t => t.id === hoveredTheme)?.name}</span> style will create{' '}
              {themes.find(t => t.id === hoveredTheme)?.description.toLowerCase()}
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

export default ThemeSelector;
