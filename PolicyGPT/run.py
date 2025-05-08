import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting PDF Processing API server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8002,  # Changed port again to avoid conflict
        log_level="info",
        reload=False  # Disable reload for production use
    )