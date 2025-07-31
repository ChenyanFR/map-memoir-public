# Security Setup Guide

## Environment Variables

This project requires several API keys to function properly. **NEVER commit real API keys to version control.**

### Required API Keys

1. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Used for: GPT-based text generation
   - Set as: `OPENAI_API_KEY` in `server/.env`

2. **Google Gemini API Key**
   - Get from: https://makersuite.google.com/app/apikey
   - Used for: AI story generation
   - Set as: `GEMINI_API_KEY` in `server/.env`

3. **Google Maps API Key**
   - Get from: https://console.cloud.google.com/apis/credentials
   - Used for: Maps functionality
   - Set as: `VITE_GOOGLE_MAPS_KEY` in `frontend/.env`

4. **Firebase Configuration**
   - Get from: Firebase Console > Project Settings
   - Used for: Authentication and database
   - Multiple keys needed in `frontend/.env`

### Setup Instructions

1. Copy the example environment files:
   ```bash
   cp server/.env.example server/.env
   cp frontend/.env.example frontend/.env
   ```

2. Fill in your actual API keys in the `.env` files

3. **Never commit the .env files** - they are in .gitignore for security

### Security Best Practices

- ✅ Use environment variables for all secrets
- ✅ Never commit `.env` files
- ✅ Use `.env.example` files to document required variables
- ✅ Regularly rotate API keys
- ❌ Never put secrets in source code
- ❌ Never put secrets in README files
- ❌ Never share `.env` files publicly

## If Secrets Are Accidentally Committed

1. **Immediately revoke/rotate the exposed keys**
2. Remove them from the repository history
3. Add them to .gitignore if not already there
4. Create new keys and update your local .env files
