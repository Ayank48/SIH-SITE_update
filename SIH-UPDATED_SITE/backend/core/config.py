"""
Backend Configuration for Lunar Correspondence Platform
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
SESSIONS_DIR = DATA_DIR / "sessions"
OUTPUTS_DIR = BASE_DIR / "outputs"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
    "https://sih-site-update.vercel.app"
]
