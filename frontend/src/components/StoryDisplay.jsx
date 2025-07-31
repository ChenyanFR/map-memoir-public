import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  PlayIcon, 
  PauseIcon, 
  SpeakerWaveIcon, 
  SpeakerXMarkIcon,
  DocumentDuplicateIcon,
  ShareIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline';
import { LoadingSpinner } from './ui/Loading';
import SaveStoryButton from './SaveStoryButton';
import toast from 'react-hot-toast';

function StoryDisplay({
  story,
  theme,
  isAudioPlaying,
  currentAudio: audio,
  isMuted: mute,
  unmuteAudio,
  muteAudio,
  selectedPlace,
  onStopAudio,
  onPlayAudio,
  isLoadingAudio = false,
}) {
  const [isPlaying, setIsPlaying] = useState(isAudioPlaying);
  const [isMuted, setIsMuted] = useState(mute);
  const [currentAudio, setCurrentAudio] = useState(null);
  const storyRef = useRef(null);

  const handlePlayPause = async () => {
    setCurrentAudio(audio);
    if (isPlaying) {
      // Pause audio
      if (currentAudio) {
        await onStopAudio();
        setIsPlaying(false);
        setCurrentAudio(null);
      }
    } else {
      // Play audio
      try {
        setIsPlaying((prev) => !prev);  
        await onPlayAudio();
      } catch (error) {
        setIsPlaying(false);
        toast.error("Failed to play audio");
      }
    }
  };

  const handleCopyStory = async () => {
    try {
      await navigator.clipboard.writeText(story);
      toast.success("Story copied to clipboard!");
    } catch (error) {
      toast.error("Failed to copy story");
    }
  };

  const handleShareStory = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Story of ${selectedPlace?.name}`,
          text: story,
          url: window.location.href,
        });
      } catch (error) {
        if (error.name !== "AbortError") {
          toast.error("Failed to share story");
        }
      }
    } else {
      // Fallback to copy to clipboard
      handleCopyStory();
    }
  };

  const formatStoryText = (text) => {
    // Split story into paragraphs and add proper spacing
    return text.split("\n").map((paragraph, index) => {
      if (paragraph.trim() === "") return null;
      return (
        <motion.p
          key={index}
          className="mb-4 leading-relaxed text-gray-700"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.5 }}
        >
          {paragraph}
        </motion.p>
      );
    });
  };

  function handleOnMuteAndUnMute() {
    if (isMuted) {
      unmuteAudio();
      setIsMuted((prev) => !prev);
    } else {
      muteAudio()
       setIsMuted((prev) => !prev);
    }
  }

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Story Header */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <BookOpenIcon className="w-8 h-8 text-primary-600" />
              <h2 className="text-2xl md:text-3xl font-serif font-bold text-gray-800">
                The Story of {selectedPlace?.name}
              </h2>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full font-medium">
                {theme} Style
              </span>
              <span className="flex items-center space-x-1">
                <span>📍</span>
                <span>{selectedPlace?.address}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mb-6">
          <motion.button
            onClick={handlePlayPause}
            disabled={isLoadingAudio}
            className="btn-primary flex items-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoadingAudio ? (
              <LoadingSpinner size="sm" text="" />
            ) : isPlaying ? (
              <PauseIcon className="w-5 h-5" />
            ) : (
              <PlayIcon className="w-5 h-5" />
            )}
            <span>
              {isLoadingAudio
                ? "Generating..."
                : isPlaying
                ? "Pause"
                : "Play Narration"}
            </span>
          </motion.button>

          <SaveStoryButton
            story={story}
            selectedPlace={selectedPlace}
            theme={theme}
          />

          <motion.button
            onClick={handleOnMuteAndUnMute}
            className="btn-secondary flex items-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isMuted ? (
              <SpeakerXMarkIcon className="w-5 h-5" />
            ) : (
              <SpeakerWaveIcon className="w-5 h-5" />
            )}
            <span>{isMuted ? "Unmute" : "Mute"}</span>
          </motion.button>

          <motion.button
            onClick={handleCopyStory}
            className="btn-secondary flex items-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <DocumentDuplicateIcon className="w-5 h-5" />
            <span>Copy</span>
          </motion.button>

          <motion.button
            onClick={handleShareStory}
            className="btn-secondary flex items-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <ShareIcon className="w-5 h-5" />
            <span>Share</span>
          </motion.button>
        </div>

        {/* Audio Controls */}
        {isPlaying && (
          <motion.div
            className="bg-gradient-to-r from-primary-50 to-secondary-50 p-4 rounded-xl border border-primary-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex items-center space-x-3">
              <SpeakerWaveIcon className="w-5 h-5 text-primary-600" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-primary-700">
                    Playing narration...
                  </span>
                </div>
                <div className="mt-1 h-1 bg-primary-200 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Story Content */}
      <motion.div
        className="card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        <div
          ref={storyRef}
          className="prose prose-lg max-w-none"
          style={{
            fontFamily: "Georgia, serif",
            lineHeight: "1.8",
            fontSize: "1.1rem",
          }}
        >
          {formatStoryText(story)}
        </div>
      </motion.div>

      {/* Story Stats */}
      <motion.div
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-600">
            {story.split(" ").length}
          </div>
          <div className="text-sm text-gray-600">Words</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-secondary-600">
            {story.split("\n").filter((p) => p.trim()).length}
          </div>
          <div className="text-sm text-gray-600">Paragraphs</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {Math.ceil(story.split(" ").length / 200)}
          </div>
          <div className="text-sm text-gray-600">Min Read</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-purple-600">{theme}</div>
          <div className="text-sm text-gray-600">Style</div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default StoryDisplay;
