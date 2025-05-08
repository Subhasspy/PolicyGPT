# PolicyGPT Architecture

## System Architecture Diagram

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Angular Frontend|     |  FastAPI Backend |     |  Azure Services  |
|                  |     |                  |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| - Document Upload|     | - PDF Processing |     | - Azure OpenAI   |
| - Personalization|     | - Summarization  |     |   (GPT Models)   |
| - Translation    |     | - Translation    |     | - Azure          |
| - Feedback UI    |     | - Feedback       |     |   Translator     |
|                  |     |   Processing     |     |                  |
+------------------+     +------------------+     +------------------+
```

## Data Flow Diagram

```
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| User uploads|---->| PDF text    |---->| Text sent to|---->| Summary     |
| PDF file(s) |     | extracted   |     | Azure OpenAI|     | generated   |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
                                                                  |
                                                                  v
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| User views  |<----| Results     |<----| Translation |<----| Personalized|
| results     |     | displayed   |     | (optional)  |     | if requested|
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
       |
       v
+-------------+     +-------------+     +-------------+
|             |     |             |     |             |
| User submits|---->| Feedback    |---->| Summary     |
| feedback    |     | processed   |     | refined     |
|             |     |             |     | (if needed) |
+-------------+     +-------------+     +-------------+
```

## Component Diagram

### Frontend Components

```
+------------------+
|                  |
| DocumentUpload   |
| Component        |
|                  |
+--------+---------+
         |
         v
+------------------+     +------------------+
|                  |     |                  |
| UploadService    |<--->| FeedbackDialog   |
|                  |     | Component        |
+--------+---------+     +------------------+
         |
         v
+------------------+     +------------------+
|                  |     |                  |
| SkeletonLoader   |     | Markdown         |
| Component        |     | Rendering        |
|                  |     |                  |
+------------------+     +------------------+
```

### Backend Services

```
+------------------+
|                  |
| FastAPI App      |
|                  |
+--------+---------+
         |
         v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| PDF Service      |     | OpenAI Service   |     | Translator      |
|                  |     |                  |     | Service          |
+------------------+     +------------------+     +------------------+
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Text Extraction  |     | Summarization    |     | Translation      |
| from PDFs        |     | Personalization  |     | to multiple      |
| Document Chunking|     | Feedback         |     | languages        |
| for large docs   |     | Large Doc Handler|     |                  |
+------------------+     +------------------+     +------------------+
```

## Sequence Diagram for Document Processing

```
User          Frontend        Backend         OpenAI API      Translator API
 |               |               |                |                |
 |--Upload PDF-->|               |                |                |
 |               |--Send Files-->|                |                |
 |               |               |--Extract Text->|                |
 |               |               |                |                |
 |               |               |--Request------>|                |
 |               |               |  Summary       |                |
 |               |               |<--Summary------|                |
 |               |               |                |                |
 |               |               |--Request------------------>|    |
 |               |               |  Translation (optional)    |    |
 |               |               |<--Translation--------------|    |
 |               |<--Results-----|                |                |
 |<--Display-----|               |                |                |
 |  Results      |               |                |                |
 |               |               |                |                |
 |--Submit------>|               |                |                |
 |  Feedback     |--Send-------->|                |                |
 |               |  Feedback     |                |                |
 |               |               |--Refine------->|                |
 |               |               |  Summary       |                |
 |               |               |  (if needed)   |                |
 |               |               |<--Refined------|                |
 |               |               |  Summary       |                |
 |               |<--Updated-----|                |                |
 |<--Display-----|  Results      |                |                |
 |  Updated      |               |                |                |
 |  Results      |               |                |                |
```

## Key Components and Responsibilities

### Frontend
- **Document Upload Component**: Handles file selection, drag-and-drop, and personalization options
- **Feedback Dialog Component**: Collects detailed feedback for unclear/inaccurate summaries
- **Skeleton Loader Component**: Provides loading state visualization
- **Upload Service**: Manages HTTP requests to the backend API

### Backend
- **PDF Service**: Extracts text from uploaded PDF files, handles document chunking for large documents
- **OpenAI Service**: Generates summaries, personalizes content, refines based on feedback, and handles large documents with recursive summarization
- **Translator Service**: Translates summaries to requested languages

### External Services
- **Azure OpenAI**: Provides AI models for text summarization and refinement
- **Azure Translator**: Provides translation capabilities for multiple languages
