from fastapi import HTTPException
import logging
import uuid
import aiohttp
from config import TRANSLATOR_CONFIG
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

# Create a session pool
session = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
        )
    return session

@lru_cache(maxsize=1000)
def _cache_key(text: str, target_language: str) -> str:
    """Create a cache key for translation"""
    return hashlib.md5(f"{text}:{target_language}".encode()).hexdigest()

translation_cache = {}

async def translate_text(text: str, target_language: str) -> str:
    """Translate text using Azure Translator with caching"""
    try:
        logger.info(f"Translation requested for language: {target_language}")
        
        # Check cache first
        cache_key = _cache_key(text, target_language)
        if cache_key in translation_cache:
            logger.info("Translation found in cache")
            return translation_cache[cache_key]

        subscription_key = TRANSLATOR_CONFIG["subscription_key"]
        endpoint = TRANSLATOR_CONFIG["endpoint"]
        location = TRANSLATOR_CONFIG["location"]

        if not all([subscription_key, endpoint, location]):
            logger.error("Azure Translator credentials not configured")
            raise ValueError("Azure Translator credentials not configured")

        path = '/translate'
        constructed_url = endpoint + path

        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': target_language
        }

        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
            'text': text
        }]

        logger.info(f"Sending translation request to Azure for language: {target_language}")
        session = await get_session()
        async with session.post(
            constructed_url, 
            params=params, 
            headers=headers, 
            json=body,
            ssl=False,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
            result = await response.json()
            logger.info(f"Received response from Azure: {result}")
            
            if result and len(result) > 0:
                translations = result[0].get('translations', [])
                if translations and len(translations) > 0:
                    translated_text = translations[0].get('text', '')
                    if translated_text:
                        # Cache the result
                        translation_cache[cache_key] = translated_text
                        logger.info("Translation successful and cached")
                        return translated_text
                    else:
                        logger.error("Empty translation received")
                        raise ValueError("Empty translation received from Azure")
            
            logger.error("No translation found in the response")
            raise ValueError("No translation found in the response")

    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to translate text: {str(e)}"
        )

async def cleanup():
    """Cleanup resources"""
    global session
    if session:
        await session.close()
        session = None