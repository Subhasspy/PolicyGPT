from fastapi import HTTPException
from openai import AzureOpenAI
import logging
import os
from config import OPENAI_CONFIG, STANDARD_PROMPT
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
def _cache_key(text: str, custom_prompt: str = None) -> str:
    """Create a cache key for summary"""
    components = [text]
    if custom_prompt:
        components.append(custom_prompt)
    key_string = "_".join(components)
    return hashlib.md5(key_string.encode()).hexdigest()

async def summarize_text(text: str, custom_prompt: str = None) -> str:
    """
    Summarize text using Azure OpenAI
    """
    try:
        # Check cache first
        cache_key = _cache_key(text, custom_prompt)
        if cache_key in summary_cache:
            return summary_cache[cache_key]

        # Use custom prompt if provided, otherwise use standard prompt
        system_prompt = custom_prompt if custom_prompt else STANDARD_PROMPT

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

async def summarize_multiple_texts(texts: list[tuple[str, str]], custom_prompt: str = None) -> list[str]:
    """
    Summarize multiple texts concurrently using Azure OpenAI
    """
    tasks = []
    for filename, text in texts:
        tasks.append(summarize_text(text, custom_prompt))
    return await asyncio.gather(*tasks)