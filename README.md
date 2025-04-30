# PolicyGPT

PolicyGPT is a full-stack application that helps users analyze and translate PDF documents, particularly focusing on policy documents, using Azure OpenAI and Azure Translator services. The application provides automated summarization and multi-language translation capabilities.

## Features

- PDF document upload and processing
- Automated document summarization using Azure OpenAI
- Multi-language translation support for summaries
- Support for various document types (policy, technical, legal, financial)
- Real-time progress tracking
- Concurrent file processing
- Responsive web interface

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
- `GET /document-types`: Get available document types and their prompts
- `POST /upload`: Upload and process PDF files
  - Supports multiple file uploads
  - Optional translation to target language
  - Custom document type selection
  - Custom prompt override

## Project Structure

```
PolicyGPT/
├── frontend/               # Angular frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── document-upload/
│   │   └── ...
│   └── ...
└── PolicyGPT/             # Python backend application
    ├── main.py            # FastAPI application
    ├── config.py          # Configuration settings
    ├── openai_service.py  # Azure OpenAI integration
    ├── pdf_service.py     # PDF processing service
    ├── translator_service.py # Azure Translator integration
    └── requirements.txt    # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.