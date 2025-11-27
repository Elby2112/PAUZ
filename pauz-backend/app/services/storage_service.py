import os
import boto3

from app.models.guided_journal import GuidedJournal

# These imports are for the tools provided by the MCP environment.
# They are not standard library and will be available when run in the correct environment.
from mcp import get_object, put_object, list_objects

class StorageService:
    def __init__(self):
        # Use a dedicated SmartBucket for guided journals
        self.bucket_name = "pauz-guided-journals"

        # Vultr configuration for PDF uploads (remains unchanged)
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

    def _get_journal_key(self, user_id: str, journal_id: str) -> str:
        """Generates the key for a specific journal."""
        return f"user_{user_id}/journal_{journal_id}"

    def _get_user_prefix(self, user_id: str) -> str:
        """Generates the prefix for a user's journals."""
        return f"user_{user_id}/"

    def save_guided_journal(self, guided_journal: GuidedJournal):
        """
        Saves a journal to the SmartBucket using a user-specific key.
        """
        key = self._get_journal_key(guided_journal.user_id, guided_journal.id)
        put_object(bucket_name=self.bucket_name, key=key, content=guided_journal.model_dump_json())

    def get_guided_journal(self, user_id: str, journal_id: str) -> GuidedJournal:
        """
        Retrieves a journal from the SmartBucket using a user-specific key.
        """
        key = self._get_journal_key(user_id, journal_id)
        journal_data = get_object(bucket_name=self.bucket_name, key=key)
        return GuidedJournal.model_validate_json(journal_data)

    def get_user_journal_keys(self, user_id: str) -> list[str]:
        """
        Lists all journal object keys for a specific user.
        """
        prefix = self._get_user_prefix(user_id)
        # Assuming list_objects returns a list of object dictionaries with a 'key' field
        objects = list_objects(bucket_name=self.bucket_name, prefix=prefix)
        return [obj['key'] for obj in objects]

    def upload_pdf(self, guided_journal_id: str, pdf_bytes: bytes) -> str:
        """
        Uploads a PDF to Vultr Object Storage. (Unchanged)
        """
        if not self.s3:
            raise ValueError("Vultr credentials are not configured.")
        file_name = f"guided_journal_{guided_journal_id}.pdf"
        self.s3.put_object(Bucket=self.vultr_bucket_name, Key=file_name, Body=pdf_bytes, ACL='public-read')
        
        url = f"https://{self.vultr_bucket_name}.{self.vultr_region}.vultrobjects.com/{file_name}"
        return url


storage_service = StorageService()