import { useEffect, useState } from 'react';

// Global flag to prevent multiple simultaneous loads
let isLoadingGoogleMaps = false;
let loadPromise = null;

export function useGoogleMaps(apiKey) {
  // Check if Google Maps API is already fully loaded
  const isFullyLoaded = () => {
    return !!(
      window.google &&
      window.google.maps &&
      window.google.maps.places &&
      window.google.maps.ControlPosition &&
      window.google.maps.Marker &&
      window.google.maps.InfoWindow
    );
  };

  // Initialize state based on current API status
  const [loaded, setLoaded] = useState(() => {
    const initialLoaded = isFullyLoaded();
    console.log('Initial Google Maps loaded state:', initialLoaded);
    return initialLoaded;
  });

  useEffect(() => {
    // Don't load if apiKey is invalid
    if (!apiKey || apiKey === 'your_google_maps_api_key_here') {
      console.warn('Invalid or missing Google Maps API key');
      return;
    }

    // Check if Google Maps API is already fully loaded
    const isFullyLoaded = () => {
      return !!(
        window.google &&
        window.google.maps &&
        window.google.maps.places &&
        window.google.maps.ControlPosition &&
        window.google.maps.Marker &&
        window.google.maps.InfoWindow
      );
    };

    // If already loaded, set state immediately
    if (isFullyLoaded()) {
      console.log('Google Maps API already fully loaded');
      setLoaded(true);
      return;
    }

    // If already loading, wait for existing promise
    if (isLoadingGoogleMaps && loadPromise) {
      console.log('Google Maps API already loading, waiting...');
      loadPromise.then(() => {
        if (isFullyLoaded()) {
          setLoaded(true);
        }
      }).catch(() => {
        setLoaded(false);
      });
      return;
    }

    // Start loading process
    isLoadingGoogleMaps = true;

    loadPromise = new Promise((resolve, reject) => {
      console.log('Starting Google Maps API load...');

      // Clean up any existing scripts first
      const existingScripts = document.querySelectorAll('script[src*="maps.googleapis.com"]');
      existingScripts.forEach(script => {
        console.log('Removing existing Google Maps script');
        script.remove();
      });

      // Clean up any existing global objects that might cause conflicts
      if (window.google && window.google.maps) {
        console.log('Google Maps API exists but may be incomplete, proceeding with reload');
      }

      // Create unique callback name to avoid conflicts
      const callbackName = `initGoogleMaps_${Date.now()}`;

      // Create new script element
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=${callbackName}`;
      script.async = true;
      script.defer = true;

      // Set up global callback
      window[callbackName] = () => {
        console.log('Google Maps API callback triggered');

        // Clean up callback
        delete window[callbackName];

        // Wait for API to be fully ready
        const checkReady = () => {
          if (isFullyLoaded()) {
            console.log('Google Maps API fully ready');
            isLoadingGoogleMaps = false;
            resolve();
          } else {
            console.log('Google Maps API not fully ready, checking again...');
            setTimeout(checkReady, 100);
          }
        };

        checkReady();
      };

      // Handle load errors
      script.onerror = (error) => {
        console.error('Failed to load Google Maps API:', error);
        isLoadingGoogleMaps = false;

        // Clean up callback
        delete window[callbackName];

        reject(error);
      };

      // Append script to document head
      document.head.appendChild(script);

      // Timeout fallback
      setTimeout(() => {
        if (isLoadingGoogleMaps) {
          console.warn('Google Maps API load timeout');
          isLoadingGoogleMaps = false;
          reject(new Error('Load timeout'));
        }
      }, 10000); // 10 second timeout
    });

    // Wait for load promise
    loadPromise.then(() => {
      if (isFullyLoaded()) {
        setLoaded(true);
      }
    }).catch((error) => {
      console.error('Google Maps load failed:', error);
      setLoaded(false);
    });

    // Cleanup function
    return () => {
      console.log('useGoogleMaps cleanup');
      // Note: We don't clean up the script or global state here
      // because other components might still be using it
    };
  }, [apiKey]);

  return loaded;
}