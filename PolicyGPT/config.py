import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Standard prompt for document summarization
STANDARD_PROMPT = "Analyze this document and provide a clear, comprehensive summary that highlights the main points, key findings, and important details. Structure the summary in a well-organized format using markdown."

# Personalized prompts based on reading level
PERSONALIZED_PROMPTS = {
    "basic": """You are an insurance expert creating a PERSONALIZED summary for someone with BASIC insurance knowledge.

Analyze this document and provide a clear, simple summary that:
- Uses straightforward language and avoids jargon completely
- Explains ALL insurance terms in simple, everyday words
- Focuses on the most important coverage details and exclusions
- Highlights practical implications for the policyholder with real-world examples
- Uses short sentences and paragraphs (no more than 2-3 sentences per paragraph)
- Includes bullet points for key information
- Defines any technical terms that must be included
- Uses analogies or comparisons to explain complex concepts

Your summary should be well-organized with clear headings and subheadings in markdown format.
Remember that the reader has minimal insurance knowledge, so make everything as accessible as possible.""",

    "intermediate": """You are an insurance expert creating a PERSONALIZED summary for someone with INTERMEDIATE insurance knowledge.

Analyze this document and provide a comprehensive summary that:
- Balances technical accuracy with accessibility
- Uses proper insurance terminology but explains more complex or uncommon terms
- Covers important details about coverage, exclusions, and conditions
- Highlights practical implications and considerations with relevant examples
- Organizes information in a logical flow with clear transitions
- Uses a mix of paragraphs and bullet points for readability
- Provides context for why certain provisions exist when helpful
- Includes enough detail for informed decision-making

Your summary should be well-organized with clear headings and subheadings in markdown format.
Remember that the reader has moderate insurance knowledge but will benefit from some explanations of more complex concepts.""",

    "advanced": """You are an insurance expert creating a PERSONALIZED summary for someone with ADVANCED insurance knowledge.

Analyze this document and provide a detailed, technical summary that:
- Uses proper insurance terminology and industry-standard language throughout
- Provides in-depth analysis of coverage details, exclusions, and conditions
- Includes nuanced interpretations of policy provisions and their implications
- References relevant insurance principles or regulations when applicable
- Maintains a professional, technical tone appropriate for industry professionals
- Organizes information in a sophisticated structure with logical progression
- Highlights unusual or noteworthy provisions that differ from standard policies
- Includes technical details that would be relevant for comprehensive understanding

Your summary should be well-organized with clear headings and subheadings in markdown format.
Remember that the reader has extensive insurance knowledge and expects a technically precise and comprehensive analysis."""
}

# Interest-focused prompts
INTEREST_FOCUSED_PROMPTS = {
    "coverage_details": "For COVERAGE DETAILS: Create a dedicated section that thoroughly explains what is covered under the policy. List all covered items, situations, and conditions. Use bullet points or tables to clearly present coverage limits, deductibles, and special provisions. Highlight any unique or exceptional coverage features.",

    "cost_savings": "For COST SAVINGS: Create a dedicated section that identifies all possible ways to save money with this policy. Include information about discounts, loyalty programs, bundling options, and premium reduction strategies. Explain how deductible choices affect premiums. Highlight any special offers or time-limited savings opportunities mentioned in the document.",

    "claim_process": "For CLAIM PROCESS: Create a dedicated section that provides a step-by-step explanation of how to file a claim. Include required documentation, reporting timeframes, contact information, and what to expect during the claims review process. Explain how claim payments are calculated and delivered. Note any special claim requirements or exceptions.",

    "policy_exclusions": "For POLICY EXCLUSIONS: Create a dedicated section that clearly lists and explains ALL exclusions and limitations in the policy. Group similar exclusions together and explain the rationale behind key exclusions when possible. Highlight particularly important or commonly misunderstood exclusions. Explain any conditions where excluded items might become covered.",

    "legal_requirements": "For LEGAL REQUIREMENTS: Create a dedicated section that outlines all legal and regulatory aspects of the policy. Include information about required disclosures, state-specific regulations, compliance requirements, and any legal obligations of the policyholder. Explain the legal framework governing the policy and any statutory provisions that affect coverage.",

    "benefits_comparison": "For BENEFITS COMPARISON: Create a dedicated section that compares the benefits of this policy to industry standards or other common policies in this category. Highlight where this policy exceeds typical coverage and note any areas where coverage might be less comprehensive than alternatives. If the document mentions specific comparisons to competitors, include this information.",

    "risk_assessment": "For RISK ASSESSMENT: Create a dedicated section that explains how risks are evaluated and managed under this policy. Include information about risk factors that affect coverage or premiums, risk mitigation strategies recommended or required by the insurer, and how the policy addresses different levels of risk. Explain any risk-based classifications or categories mentioned in the document.",

    "premium_calculation": "For PREMIUM CALCULATION: Create a dedicated section that details all factors that influence how premiums are calculated. Include information about rating factors, premium adjustment mechanisms, and how changes in circumstances might affect future premiums. Explain any premium review processes, guaranteed rates, or circumstances that could trigger premium increases."
}

# Insurance type prompts removed as per requirements

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
