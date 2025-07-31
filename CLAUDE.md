# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository contains ConfluSum, an AI-based personalized Confluence document summarization service. The project demonstrates Claude best practices for rapid MVP development and AI-powered document processing.

## Project Overview

ConfluSum is a full-stack application that:
- Takes Confluence document URLs as input
- Allows users to select personas (Developer/Product Manager/Designer)
- Generates personalized summaries using Claude AI and Confluence MCP
- Collects user feedback for validation
- Features a Google-style React frontend with Material-UI

## Development Commands

### Backend (FastAPI)
```bash
# Setup backend environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run backend server
source venv/bin/activate && python main.py
# Server runs on http://127.0.0.1:8000
# API endpoints available at /api/*

# Environment setup
cp .env.example .env
# Edit .env with your Claude API key and Confluence credentials
```

### Frontend (React + TypeScript)
```bash
# Setup and run React development server
cd react-app
npm install
npm start
# Development server runs on http://localhost:3000

# Build for production
npm run build
# Builds to ./build/ directory, served by FastAPI

# Run tests
npm test
```

### Full Application
```bash
# Run complete application (React served by FastAPI)
cd backend
source venv/bin/activate && python main.py
# Access at http://127.0.0.1:8000
```

## Architecture Overview

### Dual Frontend Approach
The project maintains two frontend implementations:
1. **Legacy Frontend** (`frontend/`): Simple HTML/CSS/JS for initial prototyping
2. **Production Frontend** (`react-app/`): React + TypeScript + Material-UI, served by FastAPI

### Backend Architecture (FastAPI)
- **`main.py`**: FastAPI application with API routes (`/api/*`) and React app serving
- **`models.py`**: Pydantic models for API request/response validation
- **`services/`**: Business logic layer
  - `confluence_service.py`: Handles Confluence URL validation and content extraction
  - `claude_service.py`: Claude AI integration with persona-specific prompt templates
  - `feedback_service.py`: User feedback collection and statistics

### Frontend Architecture (React)
- **`src/context/AppContext.tsx`**: Global state management using React Context
- **`src/services/api.ts`**: Axios-based API client with TypeScript interfaces
- **`src/pages/`**: Main application screens (HomePage, SummaryPage)
- **`src/components/`**: Reusable UI components (PersonaSelector)

### Key Integration Points
1. **API-Frontend Communication**: React app calls FastAPI endpoints at `/api/*`
2. **State Management**: React Context manages URL, persona selection, and summary data
3. **Routing**: FastAPI serves React build files while preserving API routes
4. **Error Handling**: Consistent error handling across API and UI layers

### Persona System
The application uses three distinct persona templates in `claude_service.py`:
- **Developer**: Focuses on technical requirements, APIs, implementation details
- **Product Manager**: Emphasizes business goals, timelines, decision points
- **Designer**: Highlights UX/UI requirements, user experience, design guidelines

Each persona has dedicated prompt templates that extract relevant information from Confluence documents.

### Data Flow
1. User enters Confluence URL → Frontend validates format
2. URL sent to `/api/validate-url` → Backend validates access
3. User selects persona → Frontend sends to `/api/summarize`
4. Backend fetches document → Claude AI processes with persona template
5. Summary returned to frontend → Displayed with feedback options
6. User feedback sent to `/api/feedback` → Stored for analytics

## Environment Configuration

Required environment variables in `backend/.env`:
- `ANTHROPIC_API_KEY`: Claude AI API key
- `CONFLUENCE_BASE_URL`: Your Confluence instance URL
- `CONFLUENCE_USERNAME`: Confluence username
- `CONFLUENCE_API_TOKEN`: Confluence API token
- `DEBUG`: Set to `True` for development
- `HOST`, `PORT`: Server configuration

## Development Notes

### MVP Approach
This is a rapid prototype focused on validation rather than production-ready code:
- Mock data is used when API credentials are not configured
- Simple file-based feedback storage (no database required)
- Prioritize speed and validation over scalability

### Success Criteria
The MVP aims to validate:
- 70%+ positive user feedback
- Clear differentiation between persona-based summaries  
- 30-second average response time
- 90%+ technical reliability

When working on this project, prioritize rapid iteration and user feedback collection over complex features.