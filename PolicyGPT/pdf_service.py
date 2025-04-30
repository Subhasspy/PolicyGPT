from fastapi import HTTPException
from PyPDF2 import PdfReader
import logging
import aiofiles
from io import BytesIO
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)  # Limit concurrent PDF processing

@lru_cache(maxsize=100)
def _extract_text_from_buffer(content: bytes) -> str:
    """Extract text from PDF bytes with caching"""
    try:
        buffer = BytesIO(content)
        reader = PdfReader(buffer)
        text = []
        
        for page in reader.pages:
            text.append(page.extract_text())
                
        return "\n".join(text)
    except Exception as e:
        logger.error(f"Error in PDF text extraction: {e}")
        raise

async def extract_text_from_pdf(file_path: str) -> dict:
    """Extract text from a PDF file asynchronously"""
    try:
        async with aiofiles.open(file_path, mode='rb') as file:
            content = await file.read()
            
            # Run CPU-intensive PDF processing in thread pool
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                executor,
                _extract_text_from_buffer,
                content
            )
            
            return {"text": text}
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from PDF: {str(e)}"
        )