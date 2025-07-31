import React, { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { doc, setDoc, getDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db, signInWithGoogle, signInAsGuest, logOut } from '../config/firebase';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    // If Firebase auth is not initialized, set loading to false
    if (!auth) {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      
      if (firebaseUser && db) {
        // Load or create user profile
        await loadUserProfile(firebaseUser);
      } else {
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const loadUserProfile = async (firebaseUser) => {
    try {
      const userDocRef = doc(db, 'users', firebaseUser.uid);
      const userDoc = await getDoc(userDocRef);
      
      if (userDoc.exists()) {
        setUserProfile(userDoc.data());
      } else {
        // Create new user profile
        const newProfile = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName || 'Anonymous User',
          photoURL: firebaseUser.photoURL,
          isAnonymous: firebaseUser.isAnonymous,
          createdAt: serverTimestamp(),
          lastLoginAt: serverTimestamp(),
          preferences: {
            favoriteThemes: [],
            defaultMapCenter: { lat: 37.7749, lng: -122.4194 }, // San Francisco
            autoPlay: true,
            notifications: true
          },
          stats: {
            storiesCreated: 0,
            storiesShared: 0,
            totalListeningTime: 0
          }
        };
        
        await setDoc(userDocRef, newProfile);
        setUserProfile(newProfile);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      toast.error('Failed to load user profile');
    }
  };

  const updateUserProfile = async (updates) => {
    if (!user) return;
    
    try {
      const userDocRef = doc(db, 'users', user.uid);
      await setDoc(userDocRef, updates, { merge: true });
      setUserProfile(prev => ({ ...prev, ...updates }));
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleSignInWithGoogle = async () => {
    if (!auth) {
      toast.error('Authentication is not available. Please configure Firebase.');
      return;
    }
    
    try {
      await signInWithGoogle();
      toast.success('Welcome to Map Memoir!');
    } catch (error) {
      console.error('Error signing in with Google:', error);
      toast.error('Failed to sign in with Google');
    }
  };

  const handleSignInAsGuest = async () => {
    if (!auth) {
      toast.error('Authentication is not available. Please configure Firebase.');
      return;
    }
    
    try {
      await signInAsGuest();
      toast.success('Signed in as guest');
    } catch (error) {
      console.error('Error signing in as guest:', error);
      toast.error('Failed to sign in as guest');
    }
  };

  const handleLogOut = async () => {
    if (!auth) {
      toast.error('Authentication is not available.');
      return;
    }
    
    try {
      await logOut();
      toast.success('Signed out successfully');
    } catch (error) {
      console.error('Error signing out:', error);
      toast.error('Failed to sign out');
    }
  };

  const value = {
    user,
    userProfile,
    loading,
    signInWithGoogle: handleSignInWithGoogle,
    signInAsGuest: handleSignInAsGuest,
    logOut: handleLogOut,
    updateUserProfile,
    isAuthenticated: !!user,
    isAnonymous: user?.isAnonymous || false
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
