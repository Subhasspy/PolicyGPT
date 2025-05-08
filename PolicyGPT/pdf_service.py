from fastapi import HTTPException
from PyPDF2 import PdfReader
import logging
from io import BytesIO
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession
import re
import tiktoken

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)  # Limit concurrent PDF processing

# Initialize tokenizer for GPT models
tokenizer = tiktoken.get_encoding("cl100k_base")  # This works for most GPT models

# Maximum tokens per chunk (leaving room for the prompt and completion)
MAX_CHUNK_TOKENS = 6000  # Adjust based on your model's context window

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

def chunk_text_by_tokens(text, max_tokens=MAX_CHUNK_TOKENS):
    """
    Split text into chunks that don't exceed max_tokens
    Returns a list of text chunks
    """
    if not text:
        return []

    # Get token count
    tokens = tokenizer.encode(text)
    token_count = len(tokens)

    # If text is small enough, return it as is
    if token_count <= max_tokens:
        return [text]

    # Otherwise, split into chunks
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0

    # Split by paragraphs first (better context preservation)
    paragraphs = text.split('\n\n')

    for paragraph in paragraphs:
        paragraph_tokens = tokenizer.encode(paragraph)
        paragraph_token_count = len(paragraph_tokens)

        # If a single paragraph is too large, split it by sentences
        if paragraph_token_count > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sentence_tokens = tokenizer.encode(sentence)
                sentence_token_count = len(sentence_tokens)

                # If adding this sentence would exceed the limit, start a new chunk
                if current_chunk_tokens + sentence_token_count > max_tokens:
                    if current_chunk:  # Only append if there's content
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_chunk_tokens = sentence_token_count
                else:
                    current_chunk.append(sentence)
                    current_chunk_tokens += sentence_token_count
        else:
            # If adding this paragraph would exceed the limit, start a new chunk
            if current_chunk_tokens + paragraph_token_count > max_tokens:
                if current_chunk:  # Only append if there's content
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_chunk_tokens = paragraph_token_count
            else:
                current_chunk.append(paragraph)
                current_chunk_tokens += paragraph_token_count

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

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