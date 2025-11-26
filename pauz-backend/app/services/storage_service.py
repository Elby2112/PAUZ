import os
import boto3

from app.models.guided_journal import GuidedJournal

class StorageService:
    def __init__(self):
        self.bucket_name = os.getenv("SMARTBUCKET_NAME")

        self.vultr_access_key = os.getenv("VULTR_ACCESS_KEY")
        self.vultr_secret_key = os.getenv("VULTR_SECRET_KEY")
        self.vultr_region = os.getenv("VULTR_REGION")
        self.vultr_bucket_name = os.getenv("VULTR_BUCKET_NAME")
        
        if self.vultr_access_key and self.vultr_secret_key and self.vultr_region and self.vultr_bucket_name:
            self.s3 = boto3.client('s3',
                                   aws_access_key_id=self.vultr_access_key,
                                   aws_secret_access_key=self.vultr_secret_key,
                                   region_name=self.vultr_region,
                                   endpoint_url=f'https://{self.vultr_region}.vultrobjects.com')
        else:
            self.s3 = None


    def save_guided_journal(self, guided_journal: GuidedJournal):
        """
        Saves a journal to a SmartBucket.
        """
        put_object(bucket_name=self.bucket_name, key=str(guided_journal.id), content=guided_journal.model_dump_json())

    def get_guided_journal(self, guided_journal_id: str) -> GuidedJournal:
        """
        Retrieves a journal from a SmartBucket.
        """
        journal_data = get_object(bucket_name=self.bucket_name, key=guided_journal_id)
        return GuidedJournal.model_validate_json(journal_data)

    def upload_pdf(self, guided_journal_id: str, pdf_bytes: bytes) -> str:
        """
        Uploads a PDF to Vultr Object Storage.
        """
        if not self.s3:
            raise ValueError("Vultr credentials are not configured.")
        file_name = f"guided_journal_{guided_journal_id}.pdf"
        self.s3.put_object(Bucket=self.vultr_bucket_name, Key=file_name, Body=pdf_bytes, ACL='public-read')
        
        url = f"https://{self.vultr_bucket_name}.{self.vultr_region}.vultrobjects.com/{file_name}"
        return url


storage_service = StorageService()