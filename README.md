# 🗺️ Map Memoir

**Transform your favorite places into captivating stories with AI-powered storytelling and immersive audio experiences.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Google Maps](https://img.shields.io/badge/Google%20Maps-Platform-red.svg)](https://developers.google.com/maps)

---

## 🌟 What is Map Memoir?

Map Memoir bridges the gap between geographical information and emotional connection. While Google Maps shows you *where* places are, Map Memoir tells you *why* they matter. Every location has stories, memories, and cultural significance—we use AI to bring these narratives to life.

### ✨ Key Features

- 🗺️ **Interactive Real-time Maps** - Dynamic location selection with GPS integration
- 🤖 **AI-Powered Storytelling** - Context-aware narratives using Google Gemini
- 🎭 **8 Creative Themes** - Adventure, Romance, Documentary, Mystery, Fairy Tale, Sci-Fi, Historical, Thriller
- 🎧 **Premium Audio Narration** - High-quality TTS with theme-matched voices
- 📱 **Responsive Design** - Seamless experience across all devices
- 🔐 **Secure Authentication** - Google OAuth and guest access options

---

## 🚀 Live Demo

> **🚧 Coming Soon!** - Currently preparing deployment. Check back for live demo links.

---

## 📸 Screenshots

### Interactive Map Interface
*Real-time geolocation with smart search and dynamic markers*

### Theme Selection
*8 creative storytelling themes that transform any location*

### Story Experience  
*AI-generated narratives with premium audio controls*

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and development server
- **Google Maps JavaScript API** - Interactive mapping
- **Web Audio API** - Real-time audio playback
- **Tailwind CSS** - Utility-first styling

### Backend
- **Flask** - Python web framework
- **Google Gemini API** - AI story generation
- **ElevenLabs TTS** - Premium voice synthesis
- **OpenAI TTS** - Backup audio service
- **Firebase** - Authentication and data storage

### APIs & Services
- **Google Maps Platform** (5+ APIs)
  - Maps JavaScript API
  - Geolocation API
  - Places API
  - Geocoding API
  - Static Maps API
- **AI Services**
  - Google Gemini LLM
  - ElevenLabs Text-to-Speech
  - OpenAI Text-to-Speech

---

## 🏗️ Architecture

```
Frontend (React + Vite) → Backend (Flask) → AI Services (Gemini + TTS)
       ↓                        ↓                    ↓
Interactive Maps          API Orchestration    Story Generation
Responsive UI            Error Handling        Audio Synthesis
Audio Controls           Rate Limiting         Theme Matching
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google Maps API Key
- OpenAI/ElevenLabs API Keys

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChenyanFR/map-memoir-public.git
   cd map-memoir-public
   ```

2. **Setup Backend**
   ```bash
   cd server
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   
   # Create .env file
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run the Application**
   ```bash
   # Terminal 1: Start Backend
   cd server
   python app.py
   
   # Terminal 2: Start Frontend
   cd frontend
   npm run dev
   ```

5. **Access the Application**
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8000`

---

## 🔧 Configuration

### Environment Variables

#### Backend (`server/.env`)
```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
PORT=8000
```

#### Frontend (`frontend/.env.local`)
```env
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
VITE_BACKEND_URL=http://localhost:8000
```

---

## 🎯 How It Works

1. **Location Selection** - Users choose a location via map search or automatic geolocation
2. **Theme Choice** - Select from 8 creative storytelling themes
3. **AI Generation** - Google Gemini creates location-specific narratives
4. **Audio Synthesis** - Premium TTS converts stories to immersive audio
5. **Story Experience** - Users enjoy interactive story with audio controls

---

## 🎭 Story Themes

| Theme | Description | Voice Style |
|-------|-------------|-------------|
| 🏰 **Adventure** | Thrilling journeys and exciting explorations | Energetic, dynamic |
| 💕 **Romance** | Beautiful love stories and heartwarming moments | Warm, intimate |
| 📚 **Documentary** | Factual narratives with historical insights | Authoritative, clear |
| 🔍 **Mystery** | Intriguing tales with hidden secrets | Dramatic, suspenseful |
| ✨ **Fairy Tale** | Magical and whimsical storytelling | Enchanting, playful |
| 🚀 **Sci-Fi** | Futuristic tales with technological wonders | Modern, innovative |
| 🏛️ **Historical** | Stories from the past with period authenticity | Classic, dignified |
| ⚡ **Thriller** | Edge-of-your-seat suspense and drama | Intense, gripping |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📋 Roadmap

### 🎬 Enhanced Visualization
- **Earth Studio Integration** - Cinematic 3D flyovers and aerial visualizations
- **Interactive Story Maps** - Multi-location narratives with connected paths
- **Augmented Reality** - Location-based AR story experiences

### 🤖 Advanced AI Features
- **Personalized Narratives** - Stories adapted to user preferences
- **Multi-Language Support** - 10+ languages with native speaker voices
- **Enhanced Context** - Real-time data integration (weather, events)

### 👥 Social & Community
- **Story Sharing Network** - User-generated content and discovery
- **Collaborative Features** - Community-contributed narratives
- **Travel Integration** - Tourism board partnerships

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Maps Platform** - For comprehensive mapping capabilities
- **Google Gemini** - For AI-powered story generation
- **ElevenLabs** - For premium voice synthesis
- **OpenAI** - For backup TTS services
- **Firebase** - For authentication and data storage

---

## 📞 Contact

**Project Link:** [https://github.com/ChenyanFR/map-memoir-public](https://github.com/ChenyanFR/map-memoir-public)

---

<div align="center">

**Transform your world, one story at a time** 🌍✨

*Built with ❤️ for the Google Maps Platform Hackathon*

</div>