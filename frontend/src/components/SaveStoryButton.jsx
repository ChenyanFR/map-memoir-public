import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookmarkIcon,
  GlobeAltIcon,
  LockClosedIcon,
  TagIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import StoryService from '../services/StoryService';
import { LoadingSpinner } from './ui/Loading';
import toast from 'react-hot-toast';

const SaveStoryModal = ({ isOpen, onClose, story, selectedPlace, theme }) => {
  const { user, isAuthenticated } = useAuth();
  const [isSaving, setIsSaving] = useState(false);
  const [isPublic, setIsPublic] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [customTags, setCustomTags] = useState('');

  // Prevent body scroll and ensure modal stays on top
  useEffect(() => {
    if (isOpen) {
      // Store current scroll position
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollTop}px`;
      document.body.style.width = '100%';
      
      return () => {
        // Restore scroll
        document.body.style.overflow = '';
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        window.scrollTo(0, scrollTop);
      };
    }
  }, [isOpen]);

  const handleSave = async () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to save stories');
      return;
    }

    if (!title.trim()) {
      toast.error('Please enter a title for your story');
      return;
    }

    setIsSaving(true);
    try {
      // Clean the place data to remove any functions
      const cleanPlace = selectedPlace ? {
        name: selectedPlace.name,
        address: selectedPlace.address || selectedPlace.formatted_address,
        lat: selectedPlace.lat,
        lng: selectedPlace.lng,
        placeId: selectedPlace.placeId,
        // Remove any functions or complex objects
      } : null;

      const storyData = {
        title: title.trim(),
        description: description.trim(),
        content: story,
        place: cleanPlace,
        theme,
        isPublic,
        customTags: customTags.split(',').map(tag => tag.trim()).filter(Boolean)
      };

      console.log('Saving story data:', storyData);

      await StoryService.saveStory(user.uid, storyData);
      toast.success('Story saved successfully!');
      onClose();
      setTitle('');
      setDescription('');
      setCustomTags('');
      setIsPublic(false);
    } catch (error) {
      console.error('Error saving story:', error);
      toast.error('Failed to save story. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-start justify-center pt-8 px-4 overflow-y-auto"
        style={{ 
          zIndex: 99999,
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 mb-8"
          style={{ 
            zIndex: 100000,
            position: 'relative'
          }}
          initial={{ scale: 0.9, opacity: 0, y: -20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: -20 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <BookmarkSolidIcon className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-800">Save Story</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
              aria-label="Close modal"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Story Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm font-medium text-gray-600">Location:</span>
              <span className="text-sm text-gray-800">{selectedPlace?.name}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-600">Theme:</span>
              <span className="text-sm bg-primary-100 text-primary-800 px-2 py-1 rounded-full">
                {theme}
              </span>
            </div>
          </div>

          {/* Form */}
          <div className="space-y-4 mb-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Story Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter a memorable title..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors"
                maxLength={100}
                autoFocus
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a brief description..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors resize-none"
                maxLength={300}
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <TagIcon className="w-4 h-4 inline mr-1" />
                Custom Tags (Optional)
              </label>
              <input
                type="text"
                value={customTags}
                onChange={(e) => setCustomTags(e.target.value)}
                placeholder="adventure, travel, memories..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-colors"
              />
              <p className="text-xs text-gray-500 mt-1">Separate tags with commas</p>
            </div>

            {/* Privacy Settings */}
            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                {isPublic ? (
                  <GlobeAltIcon className="w-5 h-5 text-green-600" />
                ) : (
                  <LockClosedIcon className="w-5 h-5 text-gray-600" />
                )}
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    {isPublic ? 'Public Story' : 'Private Story'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {isPublic
                      ? 'Anyone can discover and view this story'
                      : 'Only you can see this story'
                    }
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-4 focus:ring-gray-200"
              disabled={isSaving}
            >
              Cancel
            </button>
            <motion.button
              onClick={handleSave}
              disabled={isSaving || !title.trim()}
              className="flex-1 flex items-center justify-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-4 rounded-lg transition-colors focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:opacity-50 disabled:cursor-not-allowed"
              whileHover={{ scale: isSaving ? 1 : 1.02 }}
              whileTap={{ scale: isSaving ? 1 : 0.98 }}
            >
              {isSaving ? (
                <LoadingSpinner size="sm" text="Saving..." />
              ) : (
                <>
                  <BookmarkSolidIcon className="w-5 h-5" />
                  <span>Save Story</span>
                </>
              )}
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const SaveStoryButton = ({ story, selectedPlace, theme, className = "" }) => {
  const { isAuthenticated } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleClick = () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to save stories');
      return;
    }
    
    // Scroll to top before opening modal
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Small delay to allow scroll animation
    setTimeout(() => {
      setIsModalOpen(true);
    }, 200);
  };

  const handleClose = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <motion.button
        onClick={handleClick}
        className={`flex items-center space-x-2 btn-secondary ${className}`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        title="Save Story"
      >
        <BookmarkIcon className="w-5 h-5" />
        <span>Save Story</span>
      </motion.button>

      <SaveStoryModal
        isOpen={isModalOpen}
        onClose={handleClose}
        story={story}
        selectedPlace={selectedPlace}
        theme={theme}
      />
    </>
  );
};

export default SaveStoryButton;