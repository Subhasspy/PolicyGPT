from fastapi import HTTPException
from PyPDF2 import PdfReader
import logging
from io import BytesIO
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession
import re

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)  # Limit concurrent PDF processing

@lru_cache(maxsize=100)
def _extract_text_from_buffer(content: bytes | str) -> str:
    """Extract text from PDF bytes or string with caching"""
    try:
        if isinstance(content, str):
            buffer = BytesIO(content.encode('utf-8'))
        else:
            buffer = BytesIO(content)
            
        reader = PdfReader(buffer)
        text = []
        
        for page in reader.pages:
            text.append(page.extract_text())
                
        return "\n".join(text)
    except Exception as e:
        logger.error(f"Error in PDF text extraction: {e}")
        raise

async def download_file(url: str) -> bytes:
    """Download file from URL"""
    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

async def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF file"""
    try:
        # Read file content directly from the uploaded file
        content = await file.read()
        
        if not content:
            raise ValueError("Empty file content")
            
        # Run CPU-intensive PDF processing in thread pool
        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(
                executor,
                _extract_text_from_buffer,
                content
            )
            if not text.strip():
                raise ValueError("No text extracted from PDF")
                
            return text
        except Exception as e:
            raise ValueError(f"Failed to process PDF content: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from PDF: {str(e)}"
        )