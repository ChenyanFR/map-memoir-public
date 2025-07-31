import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Helper function for API requests with error handling
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

export async function fetchScript(place, theme) {
  try {
    const loadingToast = toast.loading('Generating your story...');

    const response = await apiRequest('/generate_script', {
      method: 'POST',
      body: JSON.stringify({ place, theme }),
    });

    const data = await response.json();

    toast.success('Story generated successfully!', { id: loadingToast });
    return data.script;
  } catch (error) {
    toast.error(`Failed to generate story: ${error.message}`);
    throw error;
  }
}

export async function fetchAudio(script, theme) {
  try {
    const loadingToast = toast.loading('Creating audio narration...');

    const response = await apiRequest('/generate_audio', {
      method: 'POST',
      body: JSON.stringify({ script, theme }),
    });

    if (!response.ok) {
      throw new Error('Audio generation failed');
    }

    const arrayBuffer = await response.arrayBuffer();

    toast.success('Audio generated successfully!', { id: loadingToast });
    return arrayBuffer;
  } catch (error) {
    toast.error(`Failed to generate audio: ${error.message}`);
    throw error;
  }
}

export async function playAudioBuffer(audioBuffer) {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    // Resume audio context if it's suspended (browser autoplay policy)
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    const decodedBuffer = await audioContext.decodeAudioData(audioBuffer);
    const source = audioContext.createBufferSource();

    source.buffer = decodedBuffer;
    source.connect(audioContext.destination);
    source.start(0);

    return new Promise((resolve, reject) => {
      source.onended = resolve;
      source.onerror = reject;
    });
  } catch (error) {
    console.error('Audio playback error:', error);
    throw new Error('Failed to play audio');
  }
}

export async function checkServerHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Server health check failed:', error);
    return false;
  }
}

// Export API utilities
export const api = {
  fetchScript,
  fetchAudio,
  playAudioBuffer,
  checkServerHealth,
};

// Add new SOTA TTS function
export async function fetchSOTAAudio(text, theme = "documentary") {
  try {
    const loadingToast = toast.loading('Generating premium audio...');

    const response = await apiRequest('/api/audio/generate', {
      method: 'POST',
      body: JSON.stringify({ text, theme }),
    });

    const data = await response.json();

    if (data.success) {
      toast.success('Premium audio generated!', { id: loadingToast });
      return {
        audio: data.audio,
        provider: data.provider,
        quality: data.quality,
        description: data.description
      };
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    toast.error(`Failed to generate premium audio: ${error.message}`);
    throw error;
  }
}