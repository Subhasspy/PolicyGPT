# PolicyGPT

PolicyGPT is a full-stack application that helps users analyze and translate insurance policy documents using Azure OpenAI and Azure Translator services. The application provides automated summarization, on-the-fly personalization, and multi-language translation capabilities.

## Features

- PDF document upload and processing
- Automated document summarization using Azure OpenAI
- On-the-fly personalization based on user preferences (reading level, interests, age group)
- Multi-language translation support for summaries
- User feedback system with summary refinement
- Real-time progress tracking
- Concurrent file processing
- Responsive web interface
- Large document handling with automatic chunking and recursive summarization

## Tech Stack

### Frontend (Angular)
- Angular 19
- TypeScript
- RxJS
- ngx-markdown for markdown rendering
- Standalone components architecture
- Server-side rendering (SSR) support

### Backend (FastAPI)
- Python 3.x
- FastAPI
- Azure OpenAI integration
- Azure Translator API integration
- PyPDF2 for PDF processing
- Async processing with aiohttp
- Caching support

## Prerequisites

Before running the application, make sure you have:

1. Node.js (Latest LTS version)
2. Python 3.x
3. Azure OpenAI API access
4. Azure Translator API access
5. pip (Python package manager)
6. npm (Node.js package manager)

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd PolicyGPT
```

2. Set up the backend:
```bash
cd PolicyGPT
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the PolicyGPT directory with your Azure credentials:
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_openai_endpoint
OPENAI_MODEL_NAME=your_openai_model_name
AZURE_TRANSLATOR_KEY=your_translator_key
AZURE_TRANSLATOR_ENDPOINT=your_translator_endpoint
AZURE_TRANSLATOR_REGION=your_translator_region
```

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd PolicyGPT
python run.py
```
The backend will start on http://localhost:8000

2. Start the frontend development server:
```bash
cd frontend
ng serve
```
The frontend will be available at http://localhost:4200

## API Documentation

### Backend Endpoints

- `GET /`: Health check endpoint
- `GET /languages`: Get supported translation languages
- `GET /customer-interests`: Get available customer interests for personalization
- `POST /upload`: Upload and process PDF files
  - Supports multiple file uploads
  - Optional translation to target language
  - Optional personalization (reading level, interests, age group)
- `POST /feedback`: Submit feedback for summaries
  - Supports "helpful", "unclear", and "inaccurate" feedback types
  - Refines summaries based on user feedback for unclear/inaccurate ratings
- `POST /translate`: Translate text to a supported language

