from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import logging
import os
from config import AZURE_STORAGE_CONFIG
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class AzureStorageService:
    def __init__(self):
        self.connection_string = AZURE_STORAGE_CONFIG["connection_string"]
        self.container_name = AZURE_STORAGE_CONFIG["container_name"]
        self.expiry_hours = AZURE_STORAGE_CONFIG["expiry_hours"]
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            # Ensure container exists
            self._ensure_container_exists()
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            raise HTTPException(status_code=500, detail="Storage service initialization failed")

    def _ensure_container_exists(self):
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize storage container")

    async def upload_file(self, file_content: bytes, file_name: str) -> str:
        """Upload a file to Azure Blob Storage and return its URL with SAS token"""
        try:
            # Create unique blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_name = f"temp_{timestamp}_{file_name}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload file
            blob_client.upload_blob(file_content, overwrite=True)
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=self.expiry_hours)
            )
            
            # Construct URL with SAS token
            blob_url = f"{blob_client.url}?{sas_token}"
            logger.info(f"File uploaded successfully: {blob_name}")
            
            return blob_url

        except Exception as e:
            logger.error(f"Failed to upload file to Azure Storage: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    async def delete_file(self, blob_url: str) -> None:
        """Delete a file from Azure Blob Storage"""
        try:
            # Extract blob name from URL
            blob_name = blob_url.split('/')[-1].split('?')[0]
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Delete blob if exists
            if blob_client.exists():
                blob_client.delete_blob()
                logger.info(f"Deleted blob: {blob_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete file from Azure Storage: {e}")
            # Don't raise exception for deletion failures, just log them

# Initialize storage service
storage_service = AzureStorageService()