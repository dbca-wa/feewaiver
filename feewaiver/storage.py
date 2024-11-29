import os
import logging
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

class PrivateMediaStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.PRIVATE_MEDIA_ROOT
        kwargs['base_url'] = settings.PRIVATE_MEDIA_URL
        super().__init__(*args, **kwargs)

    def _save(self, name, content):
        # Ensure the directory exists
        directory = os.path.dirname(self.path(name))
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        else:
            logger.info(f"Directory already exists: {directory}")
        
        saved_path = super()._save(name, content)
        logger.info(f"Saved file: {saved_path}")
        return saved_path

    def url(self, name):
        return super().url(name)