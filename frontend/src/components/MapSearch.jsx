import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { MagnifyingGlassIcon, MapPinIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { useGoogleMaps } from '../hooks/useGoogleMaps';
import { LoadingSpinner } from './ui/Loading';

function MapSearch({ onSelect }) {
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_KEY;
  const isValidApiKey = apiKey && apiKey !== 'your_google_maps_api_key_here';
  const { isLoaded: mapsLoaded, error: mapsError } = useGoogleMaps(apiKey);

  const mapRef = useRef(null);
  const inputRef = useRef(null);
  const map = useRef(null);
  const marker = useRef(null);
  const [searchValue, setSearchValue] = useState('');
  const [isMapReady, setIsMapReady] = useState(false);
  const [mapError, setMapError] = useState(null);

  // New York City coordinates as default fallback
  const NYC_COORDINATES = { lat: 40.7128, lng: -74.0060 };

  // Direct check for Google Maps readiness (backup for hook issues)
  const isGoogleMapsDirectlyReady = () => {
    return !!(
      window.google &&
      window.google.maps &&
      window.google.maps.places &&
      window.google.maps.ControlPosition &&
      window.google.maps.Marker &&
      window.google.maps.InfoWindow
    );
  };

  // Use either hook result or direct check
  const isMapsActuallyLoaded = mapsLoaded || isGoogleMapsDirectlyReady();

  // Show API key configuration message if key is not properly set
  if (!isValidApiKey) {
    return (
      <motion.div
        className="card max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center py-12">
          <MapPinIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">Google Maps API Key Required</h3>
          <p className="text-gray-600 mb-6">
            To use the map search functionality, please configure your Google Maps API key.
          </p>
          <div className="bg-gray-50 p-4 rounded-lg text-left max-w-md mx-auto">
            <p className="text-sm text-gray-700 mb-2">
              <strong>Steps to configure:</strong>
            </p>
            <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
              <li>Get a Google Maps API key from the Google Cloud Console</li>
              <li>Enable the Maps JavaScript API and Places API</li>
              <li>Update the <code className="bg-gray-200 px-1 rounded">VITE_GOOGLE_MAPS_KEY</code> in your .env file</li>
              <li>Restart the development server</li>
            </ol>
          </div>
          <button
            onClick={() => onSelect({
              name: 'New York, NY, USA',
              lat: NYC_COORDINATES.lat,
              lng: NYC_COORDINATES.lng,
              formatted_address: 'New York, NY, USA'
            })}
            className="btn-primary mt-6"
          >
            Use Demo Location (New York)
          </button>
        </div>
      </motion.div>
    );
  }

  // Check if Google Maps is fully loaded
  const isGoogleMapsReady = () => {
    return !!(
      window.google &&
      window.google.maps &&
      window.google.maps.Map &&
      window.google.maps.ControlPosition &&
      window.google.maps.places &&
      window.google.maps.places.Autocomplete
    );
  };

  // Initialize map with comprehensive error handling
  const initializeMap = (center) => {
    try {
      console.log('Checking Google Maps readiness...');

      if (!isGoogleMapsReady()) {
        throw new Error('Google Maps API not fully loaded yet');
      }

      if (!mapRef.current) {
        throw new Error('Map container not available');
      }

      console.log('Creating map instance...');

      // Create map instance with safe property access
      map.current = new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: 13,
        styles: [
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#e9e9e9" }, { lightness: 17 }]
          },
          {
            featureType: "landscape",
            elementType: "geometry",
            stylers: [{ color: "#f5f5f5" }, { lightness: 20 }]
          },
          {
            featureType: "road.highway",
            elementType: "geometry.fill",
            stylers: [{ color: "#ffffff" }, { lightness: 17 }]
          },
          {
            featureType: "road.highway",
            elementType: "geometry.stroke",
            stylers: [{ color: "#ffffff" }, { lightness: 29 }, { weight: 0.2 }]
          },
          {
            featureType: "road.arterial",
            elementType: "geometry",
            stylers: [{ color: "#ffffff" }, { lightness: 18 }]
          },
          {
            featureType: "road.local",
            elementType: "geometry",
            stylers: [{ color: "#ffffff" }, { lightness: 16 }]
          },
          {
            featureType: "poi",
            elementType: "geometry",
            stylers: [{ color: "#f5f5f5" }, { lightness: 21 }]
          }
        ],
        mapTypeControl: false,
        fullscreenControl: true,
        streetViewControl: false,
        zoomControl: true,
        // Safe access to ControlPosition
        zoomControlOptions: {
          position: window.google.maps.ControlPosition.RIGHT_BOTTOM
        }
      });

      console.log('Map instance created successfully');

      // Wait for map to be fully initialized
      window.google.maps.event.addListenerOnce(map.current, 'idle', () => {
        console.log('Map is fully loaded and idle');
        setupAutocomplete();
        setIsMapReady(true);
        setMapError(null);
      });

    } catch (error) {
      console.error('Error initializing map:', error);
      setMapError(error.message);
      setIsMapReady(false);

      // Retry after a short delay if API is not ready
      if (error.message.includes('not fully loaded')) {
        setTimeout(() => {
          console.log('Retrying map initialization...');
          initializeMap(center);
        }, 1000);
      }
    }
  };

  // Setup Google Places Autocomplete with comprehensive error handling
  const setupAutocomplete = () => {
    try {
      if (!inputRef.current) {
        console.warn('Input reference not available for autocomplete');
        return;
      }

      if (!isGoogleMapsReady()) {
        console.warn('Google Maps not fully ready for autocomplete');
        return;
      }

      console.log('Setting up autocomplete...');

      // Initialize autocomplete
      const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
        fields: ['geometry', 'name', 'formatted_address', 'photos', 'place_id'],
        types: ['establishment', 'geocode']
      });

      // Handle place selection
      autocomplete.addListener('place_changed', () => {
        try {
          const place = autocomplete.getPlace();

          if (!place.geometry || !place.geometry.location) {
            console.log('No geometry found for selected place');
            return;
          }

          const location = place.geometry.location;

          // Update map view to selected location
          map.current.setCenter(location);
          map.current.setZoom(15);

          // Remove existing marker if any
          if (marker.current) {
            marker.current.setMap(null);
          }

          // Create new marker for selected place
          marker.current = new window.google.maps.Marker({
            map: map.current,
            position: location,
            title: place.name,
            animation: window.google.maps.Animation.DROP,
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 10,
              fillColor: '#0ea5e9',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 3
            }
          });

          // Create info window for marker
          const infoWindow = new window.google.maps.InfoWindow({
            content: `
              <div class="p-2">
                <h3 class="font-semibold text-gray-800">${place.name}</h3>
                <p class="text-sm text-gray-600">${place.formatted_address}</p>
              </div>
            `
          });

          // Show info window on marker click
          marker.current.addListener('click', () => {
            infoWindow.open(map.current, marker.current);
          });

          // Call parent component's onSelect callback with place data
          onSelect({
            name: place.name,
            address: place.formatted_address,
            lat: location.lat(),
            lng: location.lng(),
            placeId: place.place_id,
            photos: place.photos
          });

          console.log('Place selected successfully:', place.name);
        } catch (error) {
          console.error('Error handling place selection:', error);
        }
      });

      console.log('Autocomplete setup completed');
    } catch (error) {
      console.error('Error setting up autocomplete:', error);
    }
  };

  // Request user's current location and update map
  const requestUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          console.log('User location obtained:', userLocation);

          // Smooth transition to user location if map is ready
          if (map.current && isMapReady) {
            map.current.panTo(userLocation);
            map.current.setZoom(13);
          }
        },
        (error) => {
          console.log('Geolocation error:', error.message);
          console.log('Using default location (NYC)');
        },
        {
          enableHighAccuracy: false,
          timeout: 5000,
          maximumAge: 300000
        }
      );
    } else {
      console.log('Geolocation is not supported by this browser');
    }
  };

  useEffect(() => {
    console.log('MapSearch useEffect triggered', {
      mapsLoaded,
      isMapsActuallyLoaded,
      isGoogleMapsReady: isGoogleMapsDirectlyReady(),
      inputRefExists: !!inputRef.current,
      mapRefExists: !!mapRef.current
    });

    if (!isMapsActuallyLoaded) {
      console.log('Maps not loaded yet, waiting...');
      return;
    }

    if (!mapRef.current) {
      console.log('Map ref not ready yet, waiting...');
      return;
    }

    if (!isGoogleMapsDirectlyReady()) {
      console.log('Google Maps API not fully ready, retrying...');
      const retryTimer = setTimeout(() => {
        if (isGoogleMapsDirectlyReady()) {
          initializeMap(NYC_COORDINATES);
        }
      }, 500);
      return () => clearTimeout(retryTimer);
    }

    console.log('All conditions met, initializing map...');

    // Initialize map immediately
    initializeMap(NYC_COORDINATES);

  }, [mapsLoaded, isMapsActuallyLoaded]);

  // Request user location after map is ready
  useEffect(() => {
    if (isMapReady) {
      requestUserLocation();
    }
  }, [isMapReady]);

  // Show loading state while maps API is loading
  if (!isMapsActuallyLoaded) {
    return (
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center py-12">
          <LoadingSpinner text="Loading Google Maps API..." />
          <div className="mt-4 text-xs text-gray-500">
            <p>API Key: {apiKey ? '✓' : '✗'}</p>
            <p>Hook Status: {mapsLoaded ? '✓' : '⏳'}</p>
            <p>Direct Check: {isGoogleMapsDirectlyReady() ? '✓' : '⏳'}</p>
            {mapsError && (
              <p className="text-red-500">Error: {mapsError}</p>
            )}
          </div>
        </div>
      </motion.div>
    );
  }

  // Show error state if map failed to initialize
  if (mapError && !isMapReady) {
    return (
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-red-700 mb-2">Map Loading Failed</h3>
          <p className="text-red-600 mb-4">{mapError}</p>
          <div className="bg-red-50 p-4 rounded-lg text-left max-w-md mx-auto mb-4">
            <p className="text-sm text-red-700 mb-2">
              <strong>Troubleshooting:</strong>
            </p>
            <ul className="text-xs text-red-600 space-y-1">
              <li>• Check if Maps JavaScript API is enabled</li>
              <li>• Check if Places API is enabled</li>
              <li>• Verify API key permissions</li>
              <li>• Check browser console for more details</li>
            </ul>
          </div>
          <button
            onClick={() => {
              setMapError(null);
              setIsMapReady(false);
              setTimeout(() => initializeMap(NYC_COORDINATES), 100);
            }}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Search Input Section */}
      <div className="card">
        <div className="mb-6">
          <h2 className="section-title">🗺️ Choose Your Location</h2>
          <p className="section-subtitle">
            Search for any place in the world and let AI craft its story
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="Search for a place, landmark, or address..."
            className="input-field pl-12 pr-4 text-lg"
            disabled={!isMapReady}
          />

          {searchValue && (
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
              <MapPinIcon className="h-5 w-5 text-primary-500 animate-bounce-gentle" />
            </div>
          )}
        </div>
      </div>

      {/* Map Container */}
      <motion.div
        className="map-container h-96 md:h-[500px]"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        {!isMapReady && (
          <div className="absolute inset-0 bg-gray-100 rounded-2xl flex items-center justify-center z-10">
            <div className="text-center">
              <LoadingSpinner text="Initializing map..." />
              <div className="mt-4 text-xs text-gray-500">
                <p>Google API: {isGoogleMapsReady() ? '✓' : '⏳'}</p>
                <p>Map Ready: {isMapReady ? '✓' : '⏳'}</p>
              </div>
            </div>
          </div>
        )}

        <div ref={mapRef} className="w-full h-full rounded-2xl" />
      </motion.div>
    </motion.div>
  );
}

export default MapSearch;