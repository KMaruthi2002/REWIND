"""Configuration and environment setup for REWIND."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Meta Model API
    META_API_KEY = os.getenv("META_API_KEY", "")
    META_API_BASE = "https://api.meta.ai/v1"

    # Model IDs
    MUSE_SPARK_MODEL = "muse-spark-1.3"
    SAM_MODEL = "sam-3.1"
    MUSE_IMAGE_MODEL = "muse-image"
    MUSE_WONDER_MODEL = "muse-wonder"

    # App settings
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"}

    @classmethod
    def ensure_dirs(cls):
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
