import { useState, useRef, useCallback } from "react";
import { fetchAudio, playAudioBuffer } from "../api/backendApi";
import toast from "react-hot-toast";

export function useAudioPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const audioContextRef = useRef(null);
  const sourceRef = useRef(null);
  const gainNodeRef = useRef(null);

  const muteAudio = useCallback(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.setValueAtTime(
        0,
        gainNodeRef.current.context.currentTime
      );
      setIsMuted(true);
    }
  }, []);

  const unmuteAudio = useCallback(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.setValueAtTime(
        1,
        gainNodeRef.current.context.currentTime
      );
      setIsMuted(false);
    }
  }, []);
  const stopAudio = useCallback(() => {
    if (sourceRef.current) {
      try {
        sourceRef.current.stop();
        console.log("here");
      } catch (error) {
        // Source may already be stopped
      }
      sourceRef.current = null;
    }
    setIsPlaying(false);
    setCurrentAudio(null);
  }, []);

  const playAudio = useCallback(
    async (script, theme) => {
      if (isPlaying) {
        stopAudio();
        return;
      }

      setIsLoading(true);

      try {
        // Fetch audio data
        const audioBuffer = await fetchAudio(script, theme);

        // Create or resume audio context
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext ||
            window.webkitAudioContext)();
        }

        const audioContext = audioContextRef.current;

        if (audioContext.state === "suspended") {
          await audioContext.resume();
        }
        // Decode and play audio
        const decodedBuffer = await audioContext.decodeAudioData(audioBuffer);
        const source = audioContext.createBufferSource();

        // create or reuse gain node for mute/unmute
        let gainNode = gainNodeRef.current;
        if (!gainNode) {
          gainNode = audioContext.createGain();
          gainNodeRef.current = gainNode;
          gainNode.connect(audioContext.destination);
        }
        // set gain based on mute state
        gainNode.gain.setValueAtTime(isMuted ? 0 : 1, audioContext.currentTime);

        source.buffer = decodedBuffer;
        source.connect(gainNode);

        sourceRef.current = source;
        setCurrentAudio(decodedBuffer);
        setIsPlaying(true);

        source.onended = () => {
          setIsPlaying(false);
          setCurrentAudio(null);
          sourceRef.current = null;
        };

        source.start();
      } catch (error) {
        console.error("Audio playback error:", error);
        toast.error("Failed to play audio narration");
        setIsPlaying(false);
      } finally {
        setIsLoading(false);
        console.log("finally");
      }
    },
    [isPlaying, stopAudio]
  );
  
  return {
    isPlaying,
    isLoading,
    isMuted,
    currentAudio,
    playAudio,
    stopAudio,
    muteAudio,
    unmuteAudio,
  };
}
