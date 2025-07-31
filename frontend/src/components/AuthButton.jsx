import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UserIcon, 
  UserPlusIcon, 
  ArrowRightOnRectangleIcon,
  MapIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner } from './ui/Loading';

const AuthModal = ({ isOpen, onClose }) => {
  const { signInWithGoogle, signInAsGuest, loading } = useAuth();
  const [isSigningIn, setIsSigningIn] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsSigningIn(true);
    try {
      await signInWithGoogle();
      onClose();
    } catch (error) {
      console.error('Sign in error:', error);
    } finally {
      setIsSigningIn(false);
    }
  };

  const handleGuestSignIn = async () => {
    setIsSigningIn(true);
    try {
      await signInAsGuest();
      onClose();
    } catch (error) {
      console.error('Guest sign in error:', error);
    } finally {
      setIsSigningIn(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="relative">
                <MapIcon className="w-10 h-10 text-primary-600" />
                <SparklesIcon className="w-5 h-5 text-yellow-500 absolute -top-1 -right-1" />
              </div>
              <h2 className="text-2xl font-serif font-bold text-gray-800">Map Memoir</h2>
            </div>
            <p className="text-gray-600">
              Sign in to save your stories and access them anywhere
            </p>
          </div>

          {/* Sign In Options */}
          <div className="space-y-4">
            <motion.button
              onClick={handleGoogleSignIn}
              disabled={isSigningIn}
              className="w-full flex items-center justify-center space-x-3 bg-white border-2 border-gray-200 hover:border-primary-300 text-gray-700 font-medium py-4 px-6 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-200 disabled:opacity-50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isSigningIn ? (
                <LoadingSpinner size="sm" text="" />
              ) : (
                <>
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span>Continue with Google</span>
                </>
              )}
            </motion.button>

            <motion.button
              onClick={handleGuestSignIn}
              disabled={isSigningIn}
              className="w-full flex items-center justify-center space-x-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-4 px-6 rounded-xl transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-gray-300 disabled:opacity-50"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <UserIcon className="w-5 h-5" />
              <span>Continue as Guest</span>
            </motion.button>
          </div>

          {/* Benefits */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-800 mb-3">With an account you can:</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                <span>Save and organize your stories</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                <span>Access your stories from any device</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                <span>Share stories with friends</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                <span>Discover stories from other users</span>
              </li>
            </ul>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const UserButton = ({ onClick }) => {
  const { user, userProfile, logOut, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <motion.button
        onClick={onClick}
        className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-200"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <UserPlusIcon className="w-5 h-5" />
        <span>Sign In</span>
      </motion.button>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <div className="flex items-center space-x-2">
        {user.photoURL ? (
          <img 
            src={user.photoURL} 
            alt="Profile" 
            className="w-8 h-8 rounded-full border-2 border-primary-200"
          />
        ) : (
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <UserIcon className="w-5 h-5 text-primary-600" />
          </div>
        )}
        <div className="hidden md:block">
          <p className="text-sm font-medium text-gray-800">
            {userProfile?.displayName || user.displayName || 'Anonymous'}
          </p>
          {user.isAnonymous && (
            <p className="text-xs text-gray-500">Guest User</p>
          )}
        </div>
      </div>
      
      <motion.button
        onClick={logOut}
        className="flex items-center space-x-1 text-gray-600 hover:text-red-600 font-medium py-1 px-2 rounded transition-colors duration-200"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title="Sign Out"
      >
        <ArrowRightOnRectangleIcon className="w-4 h-4" />
        <span className="hidden md:inline">Sign Out</span>
      </motion.button>
    </div>
  );
};

const AuthButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <UserButton onClick={() => setIsModalOpen(true)} />
      <AuthModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
};

export default AuthButton;
