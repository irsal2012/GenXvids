# GenXvids - Comprehensive Video Generator Platform

A full-featured video generation platform supporting multiple video creation methods including text-to-video, template-based videos, slideshows, social media content, and AI avatars.

## 🚀 Features

- **Text-to-Video Generation**: Convert text descriptions into engaging videos
- **Template-Based Videos**: Customize pre-made templates with your content
- **Slideshow Creator**: Transform images and text into presentation videos
- **Social Media Generator**: Create platform-optimized content
- **AI Avatar Videos**: Generate talking head videos with AI
- **Cross-Platform**: Web application and mobile apps (iOS/Android)

## 🏗️ Architecture

This is a monorepo containing:

- `apps/backend` - Node.js/Express API server
- `apps/web` - React.js web application
- `apps/mobile` - React Native mobile application
- `packages/shared` - Shared utilities and types
- `packages/video-engine` - Core video processing engine

## 🛠️ Tech Stack

### Backend
- Python + FastAPI
- PostgreSQL + Redis
- FFmpeg for video processing
- WebSockets for real-time updates
- AI/ML libraries (PyTorch, Transformers, etc.)

### Frontend
- React.js + TypeScript
- Tailwind CSS
- Redux Toolkit
- Canvas API + WebGL

### Mobile
- React Native + Expo
- Shared components with web

### AI/ML
- TensorFlow.js
- MediaPipe
- OpenCV.js

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- FFmpeg
- PostgreSQL
- Redis

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd GenXvids

# Install dependencies
npm run install:all

# Set up environment variables
cp apps/backend/.env.example apps/backend/.env
# Edit the .env file with your configuration

# Start development servers
npm run dev
```

### Individual Services

```bash
# Backend only
npm run dev:backend

# Web app only
npm run dev:web

# Mobile app only
npm run dev:mobile
```

## 📱 Development

### Project Structure
```
GenXvids/
├── apps/
│   ├── backend/          # API server
│   ├── web/             # React web app
│   └── mobile/          # React Native app
├── packages/
│   ├── shared/          # Shared utilities
│   └── video-engine/    # Video processing
├── docs/               # Documentation
└── scripts/           # Build scripts
```

### Available Scripts
- `npm run dev` - Start all development servers
- `npm run build` - Build all applications
- `npm run test` - Run all tests
- `npm run lint` - Lint all code
- `npm run format` - Format all code

## 🎥 Video Generation Features

### 1. Text-to-Video
- AI-powered scene generation
- Automatic voice synthesis
- Dynamic text animations
- Background music integration

### 2. Template System
- Pre-designed video templates
- Drag-and-drop customization
- Real-time preview
- Export in multiple formats

### 3. Social Media Optimization
- Platform-specific aspect ratios
- Trending templates
- Batch processing
- Auto-captioning

### 4. AI Avatar Generation
- Static image animation
- Lip-sync technology
- Gesture simulation
- Custom avatar creation

## 🔧 Configuration

### Environment Variables
Create `.env` files in each app directory:

#### Backend (.env)
```
NODE_ENV=development
PORT=3001
DATABASE_URL=postgresql://user:password@localhost:5432/genxvids
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret
UPLOAD_PATH=./uploads
```

#### Web (.env)
```
REACT_APP_API_URL=http://localhost:3001
REACT_APP_WS_URL=ws://localhost:3001
```

## 📚 API Documentation

The API documentation is available at `http://localhost:3001/docs` when running the backend server.

## 🧪 Testing

```bash
# Run all tests
npm run test

# Run backend tests
npm run test --workspace=apps/backend

# Run web tests
npm run test --workspace=apps/web
```

## 🚀 Deployment

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Build all applications
npm run build

# Start production server
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the API documentation

## 🗺️ Roadmap

- [ ] Phase 1: Core video processing and templates
- [ ] Phase 2: AI-powered features
- [ ] Phase 3: Mobile application
- [ ] Phase 4: Advanced social media tools
- [ ] Phase 5: Performance optimization and deployment
# GenXvids
