import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import MapSearch from './components/MapSearch';
import ThemeSelector from './components/ThemeSelector';
import StoryDisplay from './components/StoryDisplay';
import VideoPlayer from './components/VideoPlayer';
import Footer from './components/Footer';
import { LoadingOverlay, LoadingCard } from './components/ui/Loading';
import { AuthProvider } from './contexts/AuthContext';
import { fetchScript, checkServerHealth } from './api/backendApi';
import { useAudioPlayer } from './hooks/useAudioPlayer';
import toast from 'react-hot-toast';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

function AppContent() {
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [story, setStory] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [isGeneratingStory, setIsGeneratingStory] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking');
  const [currentStep, setCurrentStep] = useState(1);
  
  const { isMuted, unmuteAudio, muteAudio, isPlaying, isLoading: isLoadingAudio, stopAudio, playAudio, currentAudio } = useAudioPlayer();

  // Check server health on component mount
  useEffect(() => {
    const checkServer = async () => {
      try {
        const isHealthy = await checkServerHealth();
        setServerStatus(isHealthy ? 'online' : 'offline');
        
        if (!isHealthy) {
          toast('Backend server is offline. You can still explore the demo with limited functionality.', {
            icon: '⚠️',
            duration: 4000,
          });
        }
      } catch (error) {
        setServerStatus('offline');
        toast('Backend server is not available. Some features will be limited.', {
          icon: '⚠️',
          duration: 4000,
        });
      }
    };

    checkServer();
  }, []);

  const handlePlaceSelect = (place) => {
    console.log("✅ Selected Place:", place);
    setSelectedPlace(place);
    setCurrentStep(2);
    setSelectedTheme(null);
    setStory('');
    setVideoUrl(null);
  };

  const handleThemeSelect = async (theme) => {
    if (!selectedPlace) {
      toast.error('Please select a place first');
      return;
    }

    setSelectedTheme(theme);
    setIsGeneratingStory(true);
    setCurrentStep(3);
    
    try {
      const generatedStory = await fetchScript(selectedPlace, theme);
      setStory(generatedStory);
      setCurrentStep(4);
    } catch (error) {
      console.error("Error generating story:", error);
      toast.error('Failed to generate story. Please try again.');
      setCurrentStep(2);
    } finally {
      setIsGeneratingStory(false);
    }
  };

  const handlePlayAudio = async () => {
    if (!story || !selectedTheme) {
      toast.error('No story available to play');
      return;
    }

    await playAudio(story, selectedTheme);
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1: return "Choose a Location";
      case 2: return "Select Story Theme";
      case 3: return "Generating Story";
      case 4: return "Your Story is Ready";
      default: return "Map Memoir";
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 1: return "Search for any place in the world to begin your story";
      case 2: return `Tell the story of ${selectedPlace?.name} in your preferred style`;
      case 3: return "Our AI is crafting a unique story for your chosen location";
      case 4: return "Enjoy your personalized story with audio narration";
      default: return "Transform places into stories with AI";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />

      {/* Server Status Indicator */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <motion.div
          className={`flex items-center space-x-2 text-sm p-3 rounded-lg ${
            serverStatus === "online"
              ? "bg-green-50 border border-green-200 text-green-700"
              : serverStatus === "offline"
              ? "bg-red-50 border border-red-200 text-red-700"
              : "bg-yellow-50 border border-yellow-200 text-yellow-700"
          }`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {serverStatus === "online" ? (
            <CheckCircleIcon className="w-4 h-4" />
          ) : (
            <ExclamationTriangleIcon className="w-4 h-4" />
          )}
          <span>
            Server Status:{" "}
            {serverStatus === "online"
              ? "Connected"
              : serverStatus === "offline"
              ? "Disconnected"
              : "Checking..."}
          </span>
        </motion.div>
      </div>

      {/* Progress Indicator */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-3xl md:text-4xl font-serif font-bold text-gray-800 mb-2">
            {getStepTitle()}
          </h1>
          <p className="text-lg text-gray-600 mb-8">{getStepDescription()}</p>

          {/* Step Progress Bar */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <motion.div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    step <= currentStep
                      ? "bg-primary-500 text-white"
                      : "bg-gray-200 text-gray-400"
                  }`}
                  initial={{ scale: 0.8 }}
                  animate={{
                    scale: step === currentStep ? 1.1 : 1,
                    backgroundColor:
                      step <= currentStep ? "#0ea5e9" : "#e5e7eb",
                  }}
                  transition={{ duration: 0.3 }}
                >
                  {step}
                </motion.div>
                {step < 4 && (
                  <div
                    className={`w-16 h-1 mx-2 ${
                      step < currentStep ? "bg-primary-500" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="space-y-12">
          {/* Step 1: Location Selection */}
          <AnimatePresence>
            {currentStep >= 1 && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.6 }}
              >
                <MapSearch onSelect={handlePlaceSelect} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step 2: Theme Selection */}
          <AnimatePresence>
            {currentStep >= 2 && selectedPlace && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <ThemeSelector
                  onSelect={handleThemeSelect}
                  selectedPlace={selectedPlace}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step 3: Story Generation Loading */}
          <AnimatePresence>
            {isGeneratingStory && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.6 }}
              >
                <LoadingCard
                  title="Crafting Your Story"
                  description={`Creating a ${selectedTheme} story about ${selectedPlace?.name}...`}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step 4: Story Display */}
          <AnimatePresence>
            {story && !isGeneratingStory && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <StoryDisplay
                  story={story}
                  isAudioPlaying={isPlaying}
                  isMuted={isMuted}
                  unmuteAudio={unmuteAudio}
                  muteAudio={muteAudio}
                  currentAudio={currentAudio}
                  onStopAudio={stopAudio}
                  theme={selectedTheme}
                  selectedPlace={selectedPlace}
                  onPlayAudio={handlePlayAudio}
                  isLoadingAudio={isLoadingAudio}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Video Player (when video is available) */}
          <AnimatePresence>
            {videoUrl && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -40 }}
                transition={{ duration: 0.6 }}
              >
                <VideoPlayer
                  url={videoUrl}
                  title={`Video Story of ${selectedPlace?.name}`}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Loading Overlay */}
      <LoadingOverlay
        isVisible={isLoadingAudio}
        text="Generating audio narration..."
      />

      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
