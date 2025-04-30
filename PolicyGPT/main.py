from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import aiofiles
from typing import List, Optional
import asyncio
from config import UPLOAD_FOLDER, SUPPORTED_LANGUAGES, DEFAULT_PROMPTS
from pdf_service import extract_text_from_pdf
from translator_service import translate_text, cleanup
from openai_service import summarize_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Multiple PDF Processing API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    await cleanup()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Server is running"}

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    # Group languages by region for better organization
    grouped_languages = {
        "Indian Languages": {k: v for k, v in SUPPORTED_LANGUAGES.items() 
                           if k in ["hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa", "ur", "or"]},
        "Other Languages": {k: v for k, v in SUPPORTED_LANGUAGES.items() 
                          if k not in ["hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa", "ur", "or"]}
    }
    
    return JSONResponse(
        status_code=200,
        content={
            "supported_languages": SUPPORTED_LANGUAGES,
            "grouped_languages": grouped_languages,
            "examples": {
                "Tamil Translation": "Use target_language=ta",
                "Hindi Translation": "Use target_language=hi",
                "Telugu Translation": "Use target_language=te"
            }
        }
    )

@app.get("/document-types")
async def get_document_types():
    """Get available document types and their default prompts"""
    return JSONResponse(
        status_code=200,
        content={
            "available_document_types": list(DEFAULT_PROMPTS.keys()),
            "default_prompts": DEFAULT_PROMPTS
        }
    )

async def process_single_file(
    file: UploadFile, 
    target_language: Optional[str],
    document_type: str,
    custom_prompt: Optional[str]
):
    """Process a single PDF file with custom prompt"""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Extract text from PDF and get summary concurrently
        extracted_data = await extract_text_from_pdf(file_path)
        
        # Get summary using OpenAI
        summary = await summarize_text(
            extracted_data["text"],
            document_type=document_type,
            custom_prompt=custom_prompt
        )

        # Initialize response
        result = {
            "filename": file.filename,
            "summaries": {
                "original": summary
            }
        }

        # Add translated summary if target language is provided
        if target_language and target_language != "en":
            try:
                translated = await translate_text(summary, target_language)
                result["summaries"][target_language] = translated
            except Exception as e:
                logger.error(f"Translation failed but continuing with original summary: {e}")

        return result

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        return {"filename": file.filename, "error": str(e)}
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {e}")

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    target_language: Optional[str] = Query(
        default=None,
        description="Optional target language code for translation"
    ),
    document_type: str = Form(
        default="general",
        description="Type of document to process"
    ),
    custom_prompt: Optional[str] = Form(
        default=None,
        description="Custom prompt to override default prompts"
    )
):
    """Upload and process multiple PDF files concurrently"""
    try:
        tasks = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            
            task = process_single_file(
                file, 
                target_language,
                document_type,
                custom_prompt
            )
            tasks.append(task)

        # Process all files concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = []
        failed = []

        for file, result in zip(files, results):
            if isinstance(result, Exception):
                failed.append({
                    "filename": file.filename,
                    "error": str(result)
                })
            elif "error" in result:
                failed.append(result)
            else:
                successful.append(result)

        return JSONResponse(
            status_code=200,
            content={
                "successful_files": successful,
                "failed_files": failed
            }
        )
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
