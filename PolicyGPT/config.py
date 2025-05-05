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

# Azure Blob Storage Configuration
AZURE_STORAGE_CONFIG = {
    "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    "container_name": os.getenv("AZURE_STORAGE_CONTAINER_NAME", "temp-uploads"),
    "expiry_hours": int(os.getenv("AZURE_STORAGE_EXPIRY_HOURS", "24"))  # Default 24 hours expiry
}

# Standard prompt for document summarization
STANDARD_PROMPT = "Analyze this document and provide a clear, comprehensive summary that highlights the main points, key findings, and important details. Structure the summary in a well-organized format using markdown."

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