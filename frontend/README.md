# Map Memoir - Frontend

A beautiful, modern React application that transforms places into AI-generated stories with interactive maps and voice narration.

## ✨ Features

- **🗺️ Interactive Maps**: Google Maps integration with place search and selection
- **🤖 AI Storytelling**: Multiple narrative themes (Fairy Tale, Documentary, Mystery, etc.)
- **🎧 Voice Narration**: Text-to-speech audio generation for stories
- **📱 Responsive Design**: Beautiful UI that works on all devices
- **🎨 Modern UI/UX**: Built with Tailwind CSS and Framer Motion animations
- **⚡ Fast Performance**: Powered by Vite for lightning-fast development and builds

## 🛠️ Tech Stack

- **Frontend Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Animations**: Framer Motion
- **Icons**: Heroicons & Lucide React
- **Maps**: Google Maps JavaScript API
- **Notifications**: React Hot Toast
- **HTTP Client**: Fetch API with error handling

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Google Maps API key
- Backend server running (see server directory)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Environment Setup:**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your configurations:
   ```env
   VITE_GOOGLE_MAPS_KEY=your_google_maps_api_key_here
   VITE_API_BASE_URL=http://localhost:5000
   ```

### 🗺️ Google Maps API Setup

To use the map search functionality, you'll need a Google Maps API key:

1. **Go to the Google Cloud Console:**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Required APIs:**
   - Navigate to "APIs & Services" > "Library"
   - Enable these APIs:
     - **Maps JavaScript API**
     - **Places API**

3. **Create API Key:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key

4. **Configure API Key:**
   - Replace `your_google_maps_api_key_here` in your `.env` file
   - Example: `VITE_GOOGLE_MAPS_KEY=AIzaSyBvO...your_actual_key`

5. **Restrict API Key (Recommended):**
   - In the Google Cloud Console, edit your API key
   - Add HTTP referrers restriction: `localhost:*/*` for development
   - Add your production domain when deploying

**Note:** Without a valid API key, the app will show a demo mode with a preset Seoul location.

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── api/
│   │   └── backendApi.js          # API client with error handling
│   ├── components/
│   │   ├── ui/
│   │   │   └── Loading.jsx        # Loading components
│   │   ├── Header.jsx             # App header with branding
│   │   ├── Footer.jsx             # App footer
│   │   ├── MapSearch.jsx          # Interactive map search
│   │   ├── ThemeSelector.jsx      # Story theme selection
│   │   ├── StoryDisplay.jsx       # Story viewing with controls
│   │   └── VideoPlayer.jsx        # Enhanced video player
│   ├── hooks/
│   │   ├── useGoogleMaps.js       # Google Maps API hook
│   │   └── useAudioPlayer.js      # Audio playback management
│   ├── styles/
│   │   └── globals.css            # Global styles and Tailwind
│   ├── App.jsx                    # Main application component
│   └── main.jsx                   # Application entry point
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🎨 Design System

### Colors

- **Primary**: Blue tones (#0ea5e9)
- **Secondary**: Pink/Rose tones (#ec4899)
- **Success**: Green tones
- **Warning**: Yellow/Amber tones
- **Error**: Red tones

### Typography

- **Headers**: Playfair Display (serif)
- **Body**: Inter (sans-serif)

### Components

- **Cards**: Glass-morphism effects with subtle shadows
- **Buttons**: Gradient backgrounds with hover animations
- **Forms**: Clean inputs with focus states
- **Loading**: Smooth spinners and skeleton screens

## 🔧 Configuration

### Google Maps Setup

1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Maps JavaScript API
   - Places API
3. Add your domain to the API key restrictions
4. Update the `VITE_GOOGLE_MAPS_KEY` in your `.env` file

### Tailwind CSS

The project uses a custom Tailwind configuration with:
- Extended color palette
- Custom animations
- Component utilities
- Responsive breakpoints

### Framer Motion

Animations are configured for:
- Page transitions
- Component entrances
- Hover effects
- Loading states

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint (when configured)

## 🔌 API Integration

The frontend communicates with the backend through:

- **POST /generate_script** - Generate AI story
- **POST /generate_audio** - Generate voice narration
- **GET /health** - Check server status

All API calls include:
- Error handling with user feedback
- Loading states
- Toast notifications
- Automatic retries for failed requests

## 🎯 User Experience Flow

1. **Landing**: Beautiful hero section with clear call-to-action
2. **Location Search**: Interactive map with Google Places autocomplete
3. **Theme Selection**: Visual theme cards with descriptions
4. **Story Generation**: Loading states with progress indicators
5. **Story Display**: Rich text display with audio controls
6. **Sharing**: Copy and share functionality

## 🚀 Performance Optimizations

- **Code Splitting**: Dynamic imports for large components
- **Image Optimization**: Optimized assets and lazy loading
- **Bundle Analysis**: Vite's built-in bundling optimizations
- **Caching**: Browser caching for static assets
- **Preloading**: Critical resource preloading

## 🧪 Testing

The application includes:
- Component error boundaries
- API error handling
- User feedback for all states
- Graceful degradation for missing features

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Map Memoir application suite.

---

**Happy storytelling! 🗺️✨**
