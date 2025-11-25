import os
import boto3
# from raindrop_mcp.smartbucket import SmartBucket # Removed import

from app.models.journal import Journal
from botocore.client import Config # Keep this import if used elsewhere, otherwise remove

class StorageService:
    def __init__(self):
        self.bucket_name = os.getenv("SMARTBUCKET_NAME")
        # self.smart_bucket = SmartBucket(self.bucket_name) # Removed instantiation

        self.vultr_access_key = os.getenv("VULTR_ACCESS_KEY")
        self.vultr_secret_key = os.getenv("VULTR_SECRET_KEY")
        self.vultr_region = os.getenv("VULTR_REGION")
        self.vultr_bucket_name = os.getenv("VULTR_BUCKET_NAME")
        
        self.s3 = boto3.client('s3',
                               aws_access_key_id=self.vultr_access_key,
                               aws_secret_access_key=self.vultr_secret_key,
                               region_name=self.vultr_region,
                               endpoint_url=f'https://{self.vultr_region}.vultrobjects.com')


    def save_journal(self, journal: Journal):
        """
        Saves a journal to a SmartBucket.
        (Removed SmartBucket dependency as lm-raindrop does not provide direct object storage)
        """
        # self.smart_bucket.put_object(key=journal.id, content=journal.model_dump_json())
        raise NotImplementedError("SmartBucket direct object storage is not supported in the new API.")

    def get_journal(self, journal_id: str) -> Journal:
        """
        Retrieves a journal from a SmartBucket.
        (Removed SmartBucket dependency as lm-raindrop does not provide direct object storage)
        """
        # journal_data = self.smart_bucket.get_object(key=journal_id)
        # return Journal.parse_raw(journal_data)
        raise NotImplementedError("SmartBucket direct object storage is not supported in the new API.")

    def upload_pdf(self, journal_id: str, pdf_bytes: bytes) -> str:
        """
        Uploads a PDF to Vultr Object Storage.
        """
        file_name = f"journal_{journal_id}.pdf"
        self.s3.put_object(Bucket=self.vultr_bucket_name, Key=file_name, Body=pdf_bytes, ACL='public-read')
        
        url = f"https://{self.vultr_bucket_name}.{self.vultr_region}.vultrobjects.com/{file_name}"
        return url


storage_service = StorageService()