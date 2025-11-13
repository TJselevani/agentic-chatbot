# Logging configuration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", None),  # None means console only
    "max_bytes": int(os.getenv("LOG_MAX_BYTES", 10485760)),  # 10MB
    "backup_count": int(os.getenv("LOG_BACKUP_COUNT", 3)),
}