from fastapi import HTTPException
from openai import AzureOpenAI
import logging
import os
from config import OPENAI_CONFIG, DEFAULT_PROMPTS
import asyncio
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=OPENAI_CONFIG["api_key"],
    api_version=OPENAI_CONFIG["api_version"],
    azure_endpoint=OPENAI_CONFIG["azure_endpoint"]
)

# Semaphore to limit concurrent API calls
MAX_CONCURRENT_CALLS = 5
api_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

# Cache for summaries
summary_cache = {}

@lru_cache(maxsize=1000)
def _cache_key(text: str, document_type: str, custom_prompt: str = None) -> str:
    """Create a cache key for summary"""
    key_string = f"{text}:{document_type}:{custom_prompt or ''}"
    return hashlib.md5(key_string.encode()).hexdigest()

async def summarize_text(text: str, document_type: str = "general", custom_prompt: str = None) -> str:
    """
    Summarize text using Azure OpenAI with caching and rate limiting
    """
    try:
        # Check cache first
        cache_key = _cache_key(text, document_type, custom_prompt)
        if cache_key in summary_cache:
            return summary_cache[cache_key]

        # Get the appropriate prompt
        system_prompt = custom_prompt if custom_prompt else DEFAULT_PROMPTS.get(document_type, DEFAULT_PROMPTS["general"])

        # Use semaphore to limit concurrent API calls
        async with api_semaphore:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL_NAME"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Here's the document to analyze:\n\n{text}"}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
            )
            
            summary = response.choices[0].message.content
            # Format summary as markdown
            summary = f"### Summary\n\n{summary}"
            # Cache the result
            summary_cache[cache_key] = summary
            return summary

    except Exception as e:
        logger.error(f"Error summarizing text with Azure OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize text: {str(e)}")

async def summarize_multiple_texts(texts: list[tuple[str, str]], document_type: str = "general", custom_prompt: str = None) -> list[str]:
    """
    Summarize multiple texts concurrently using Azure OpenAI
    """
    try:
        # Create tasks for each text
        tasks = [summarize_text(text, document_type, custom_prompt) for text, _ in texts]
        
        # Process all texts concurrently
        summaries = await asyncio.gather(*tasks)
        
        # Return list of summaries
        return summaries

    except Exception as e:
        logger.error(f"Error processing multiple texts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process texts: {str(e)}")