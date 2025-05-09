from fastapi import HTTPException
from openai import AzureOpenAI
import logging
import os
from config import OPENAI_CONFIG, STANDARD_PROMPT, PERSONALIZED_PROMPTS, INTEREST_FOCUSED_PROMPTS
import asyncio
from functools import lru_cache
import hashlib
from typing import Optional, Dict, Any, List
import tiktoken
from pdf_service import chunk_text_by_tokens

# Initialize tokenizer for GPT models (same as in pdf_service.py)
tokenizer = tiktoken.get_encoding("cl100k_base")

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

    Args:
        text: The text to summarize
        custom_prompt: Optional custom prompt to use instead of the standard prompt
    """
    try:
        # Check cache first
        cache_key = _cache_key(text, custom_prompt)
        if cache_key in summary_cache:
            return summary_cache[cache_key]

        # Use custom prompt if provided, otherwise use standard prompt
        system_prompt = custom_prompt if custom_prompt else STANDARD_PROMPT

        # Determine if this is a personalized request by checking for specific markers
        is_personalized = custom_prompt and "### IMPORTANT: This user is specifically interested in:" in custom_prompt

        # Adjust parameters based on whether this is a personalized request
        max_tokens = 1500 if is_personalized else 1000  # Allow more tokens for personalized summaries
        temperature = 0.5 if is_personalized else 0.7   # Lower temperature for more focused responses

        # Check if text needs to be chunked (accounting for prompt tokens too)
        # We'll use a conservative estimate for prompt tokens
        estimated_prompt_tokens = 500  # Adjust based on your typical prompt size
        chunks = chunk_text_by_tokens(text, max_tokens=6000 - estimated_prompt_tokens)

        # If we have multiple chunks, process them recursively
        if len(chunks) > 1:
            logger.info(f"Document is large, splitting into {len(chunks)} chunks for processing")

            # First, summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                chunk_prompt = f"{system_prompt}\n\nThis is part {i+1} of {len(chunks)} of a larger document. Focus on extracting the key information from this section."

                # Use semaphore to limit concurrent API calls
                async with api_semaphore:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL_NAME"),
                            messages=[
                                {"role": "system", "content": chunk_prompt},
                                {"role": "user", "content": f"Here's the document section to analyze:\n\n{chunk}"}
                            ],
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                    )

                    chunk_summary = response.choices[0].message.content
                    chunk_summaries.append(chunk_summary)

            # Then, combine the summaries
            combined_chunks = "\n\n".join([f"Section {i+1} Summary:\n{summary}" for i, summary in enumerate(chunk_summaries)])

            # Create a final summary from the combined chunk summaries
            final_prompt = f"{system_prompt}\n\nBelow are summaries of different sections of a document. Create a cohesive, complete summary that integrates all the information."

            # Use semaphore to limit concurrent API calls
            async with api_semaphore:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL_NAME"),
                        messages=[
                            {"role": "system", "content": final_prompt},
                            {"role": "user", "content": f"Here are the section summaries to integrate:\n\n{combined_chunks}"}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                )

                summary = response.choices[0].message.content
                # Cache the result
                summary_cache[cache_key] = summary
                return summary
        else:
            # For single chunks, process normally
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
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                )

                summary = response.choices[0].message.content
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

FEEDBACK_PROMPTS = {
    "unclear": """You are an expert at improving document summaries. The previous summary was marked as unclear.
Focus on:
- Clearer structure and organization
- Simpler language when possible
- Better transitions between ideas
- Highlighting key points more effectively
Please improve the summary while maintaining accuracy.""",

    "inaccurate": """You are an expert at improving document summaries. The previous summary was marked as inaccurate.
Focus on:
- Fact-checking against the original text
- Correcting any misrepresentations
- Ensuring numerical data is accurate
- Maintaining proper context
Please provide a more accurate summary.""",

    "needs_improvement": """You are an expert at improving document summaries.
Taking into account the user's specific feedback, please improve the summary by:
- Addressing the mentioned concerns
- Maintaining the strong points of the original
- Ensuring clarity and accuracy
Please provide an enhanced summary that better meets the user's needs."""
}

async def refine_summary_with_feedback(text: str, original_summary: str, feedback_type: str, feedback_text: str = None) -> str:
    """Refine the summary based on user feedback using Azure OpenAI"""
    try:
        feedback_prompts = {
            "unclear": "The previous summary was unclear. Please provide a clearer, better structured summary that is easier to understand.",
            "inaccurate": "The previous summary contained inaccuracies. Please provide a more accurate summary strictly based on the document content.",
        }

        # Create a more detailed system prompt
        system_prompt = "You are an expert insurance document summarizer tasked with improving a summary based on user feedback."
        system_prompt += f"\n\nThe user indicated that the summary was {feedback_type}."

        if feedback_text:
            system_prompt += f"\n\nSpecific feedback from the user: \"{feedback_text}\""
        else:
            system_prompt += f"\n\nGeneral guidance: {feedback_prompts.get(feedback_type)}"

        system_prompt += "\n\nPlease provide a revised summary that addresses these concerns while maintaining accuracy and clarity."

        # Check if text needs to be chunked (accounting for prompt tokens and original summary)
        estimated_prompt_tokens = 500 + len(tokenizer.encode(original_summary))
        chunks = chunk_text_by_tokens(text, max_tokens=6000 - estimated_prompt_tokens)

        # If we have multiple chunks, process them differently
        if len(chunks) > 1:
            logger.info(f"Document for refinement is large, using a different approach with {len(chunks)} chunks")

            # For refinement of large documents, we'll use the original summary as a base
            # and focus on improving it based on the feedback, rather than re-summarizing from scratch

            # Use semaphore to limit concurrent API calls
            async with api_semaphore:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL_NAME"),
                        messages=[
                            {"role": "system", "content": system_prompt + "\n\nThe original document is very large, so focus on improving the existing summary based on the feedback without requiring the full document text."},
                            {"role": "user", "content": f"Original summary to improve:\n\n{original_summary}\n\nPlease provide an improved summary that addresses the feedback."}
                        ],
                        max_tokens=1500,  # Allow more tokens for refinement
                        temperature=0.7
                    )
                )

                refined_summary = response.choices[0].message.content
                logger.info(f"Generated refined summary for feedback type: {feedback_type} (large document approach)")
                return refined_summary
        else:
            # For smaller documents, use the original approach
            # Use semaphore to limit concurrent API calls
            async with api_semaphore:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL_NAME"),
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Original document:\n\n{text}\n\nOriginal summary:\n\n{original_summary}\n\nPlease provide an improved summary that addresses the feedback."}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                )

                refined_summary = response.choices[0].message.content
                logger.info(f"Generated refined summary for feedback type: {feedback_type}")
                return refined_summary

    except Exception as e:
        logger.error(f"Error refining summary with Azure OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refine summary: {str(e)}")

async def generate_personalized_summary(
    text: str,
    reading_level: Optional[str] = None,
    interests: Optional[List[str]] = None,
    age_group: Optional[str] = None
) -> str:
    """
    Generate a personalized summary based on provided personalization parameters

    Args:
        text: The text to summarize
        reading_level: Optional reading level (basic, intermediate, advanced)
        interests: Optional list of interests
        age_group: Optional age group
    """
    try:
        # If no personalization parameters provided, return standard summary
        if not any([reading_level, interests]):
            return await summarize_text(text)

        # Create a personalized prompt based on the reading level
        base_prompt = PERSONALIZED_PROMPTS.get(
            reading_level if reading_level else "intermediate",
            PERSONALIZED_PROMPTS["intermediate"]
        )

        # Build a more focused prompt for user interests
        interest_sections = []
        interest_names = []

        if interests:
            for interest in interests:
                if interest in INTEREST_FOCUSED_PROMPTS:
                    interest_sections.append(INTEREST_FOCUSED_PROMPTS[interest])
                    # Convert snake_case to readable format
                    interest_names.append(interest.replace('_', ' ').title())

        # Combine all prompts with stronger emphasis on interests
        combined_prompt = base_prompt

        # Add a personalized introduction based on interests
        if interest_names:
            combined_prompt += f"\n\n### IMPORTANT: This user is specifically interested in: {', '.join(interest_names)}."
            combined_prompt += "\nYou MUST prioritize these topics in your summary and provide detailed information about them."
            combined_prompt += "\nMake sure each of these interest areas is addressed with its own section in the summary."

            # Add the specific instructions for each interest
            if interest_sections:
                combined_prompt += "\n\n### For each interest area, follow these specific instructions:\n" + "\n".join(interest_sections)

        # Add age group context if provided
        if age_group:
            combined_prompt += f"\n\n### This summary is for someone in the {age_group} age group. Adjust your explanation accordingly."

        # Add final instruction to ensure personalization
        combined_prompt += "\n\n### FINAL INSTRUCTION: Review your summary before submitting to ensure you've adequately addressed ALL the user's specified interests. If any interest area isn't thoroughly covered, expand that section."

        # Add instruction for large documents
        combined_prompt += "\n\n### If the document is large and has been split into sections, make sure to create a cohesive summary that covers all important aspects from all sections."

        # Generate the personalized summary using the enhanced summarize_text function
        # which now handles large documents automatically
        return await summarize_text(text, combined_prompt)

    except Exception as e:
        logger.error(f"Error generating personalized summary: {e}")
        # Fallback to standard summary
        return await summarize_text(text)