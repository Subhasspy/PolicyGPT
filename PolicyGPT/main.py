from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List, Optional
import asyncio
from config import SUPPORTED_LANGUAGES
from pdf_service import extract_text_from_pdf
from translator_service import translate_text, cleanup
from openai_service import summarize_text, refine_summary_with_feedback
from storage_service import storage_service
import json
from datetime import datetime

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

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    await cleanup()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    return {"supported_languages": SUPPORTED_LANGUAGES}

async def process_single_file(
    file: UploadFile, 
    target_language: Optional[str],
    custom_prompt: Optional[str]
):
    """Process a single PDF file"""
    try:
        # Extract text from PDF
        pdf_text = await extract_text_from_pdf(file)
        
        # Generate summary using standard prompt
        summary = await summarize_text(pdf_text, custom_prompt)
        
        result = {
            "filename": file.filename,
            "summaries": {
                "original": summary
            }
        }
        
        # Translate if target language is specified
        if target_language and target_language in SUPPORTED_LANGUAGES:
            translated_summary = await translate_text(summary, target_language)
            result["summaries"][target_language] = translated_summary
        
        return result
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        return {
            "filename": file.filename,
            "error": str(e)
        }

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...), 
    target_language: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None)
):
    """Process multiple PDF files"""
    try:
        results = []
        for file in files:
            try:
                if not file.filename.lower().endswith('.pdf'):
                    results.append({
                        "filename": file.filename,
                        "error": "Only PDF files are supported"
                    })
                    continue

                # Get the text content and store it for potential refinement
                file_content = await extract_text_from_pdf(file)
                
                # Generate summary
                summary = await summarize_text(file_content, custom_prompt)
                
                result = {
                    "filename": file.filename,
                    "summaries": {
                        "original": summary
                    },
                    "originalText": file_content  # Store original text for refinement
                }
                
                # Translate if target language is specified
                if target_language and target_language in SUPPORTED_LANGUAGES:
                    translated_summary = await translate_text(summary, target_language)
                    result["summaries"][target_language] = translated_summary
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "total_files_processed": len(files)
            }
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/feedback")
async def submit_feedback(
    summary_id: str = Form(...),
    feedback_type: str = Form(...),
    feedback_text: Optional[str] = Form(None),
    original_text: Optional[str] = Form(None),
    original_summary: Optional[str] = Form(None)
):
    """Submit feedback for a summary and get refined version if needed"""
    try:
        feedback = {
            "summary_id": summary_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Received feedback: {json.dumps(feedback, indent=2)}")

        # Only refine if we have the original text and feedback type is unclear or inaccurate
        if original_text and feedback_type in ["unclear", "inaccurate"]:
            refined_summary = await refine_summary_with_feedback(
                original_text, 
                original_summary, 
                feedback_type, 
                feedback_text
            )
            return {
                "status": "success", 
                "message": "Summary has been refined based on your feedback",
                "summaries": {
                    "original": refined_summary  # Override original with refined
                }
            }
        
        return {
            "status": "success", 
            "message": "Feedback submitted successfully"
        }

    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_text_endpoint(
    text: str = Form(...),
    target_language: str = Form(...)
):
    """Translate text to the target language"""
    try:
        if target_language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Language {target_language} is not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )
            
        translated_text = await translate_text(text, target_language)
        return {"translated_text": translated_text}
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
