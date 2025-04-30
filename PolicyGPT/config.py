import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Upload folder configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Azure OpenAI Configuration
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "api_version": "2024-02-15-preview",
    "azure_endpoint": os.getenv("OPENAI_API_BASE")
}

# Azure Translator Configuration
TRANSLATOR_CONFIG = {
    "subscription_key": os.getenv("AZURE_TRANSLATOR_KEY"),
    "endpoint": os.getenv("AZURE_TRANSLATOR_ENDPOINT"),
    "location": os.getenv("AZURE_TRANSLATOR_REGION")
}

# Default prompts for different document types
DEFAULT_PROMPTS = {
    "general": "Provide a clear, concise summary of the main points.",
    "policy": "Analyze this policy document and highlight key coverage details, terms, conditions, and important exclusions.",
    "technical": "Break down the technical content into main concepts and explain them clearly.",
    "legal": "Analyze this legal document and highlight key legal terms, obligations, and important clauses.",
    "financial": "Summarize the financial information, highlighting key figures, trends, and important financial terms."
}

# Supported languages dictionary
SUPPORTED_LANGUAGES = {
    "en": "English",
    # Indian languages
    "hi": "Hindi",
    "bn": "Bengali",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
    "or": "Odia",
    # Other languages
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "ru": "Russian"
}