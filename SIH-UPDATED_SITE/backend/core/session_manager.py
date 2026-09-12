"""
Session Manager for Ephemeral Processing & Result Storage
"""
import base64
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

from backend.core.config import SESSIONS_DIR


class SessionManager:
    @staticmethod
    def create_session() -> str:
        session_id = str(uuid.uuid4())
        session_dir = SESSIONS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        # Initialize session state
        state = {
            "session_id": session_id,
            "source_uploaded": False,
            "reference_uploaded": False,
            "pipeline_executed": False,
            "source_sensor": "OHRC",
            "reference_sensor": "TMC2",
            "source_gsd": 0.25,
            "reference_gsd": 5.0
        }
        with open(session_dir / "state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return session_id

    @staticmethod
    def get_session_dir(session_id: str) -> Path:
        session_dir = SESSIONS_DIR / session_id
        if not session_dir.exists():
            session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    @classmethod
    def get_state(cls, session_id: str) -> Dict[str, Any]:
        s_dir = cls.get_session_dir(session_id)
        state_file = s_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"session_id": session_id}

    @classmethod
    def update_state(cls, session_id: str, updates: Dict[str, Any]):
        s_dir = cls.get_session_dir(session_id)
        current = cls.get_state(session_id)
        current.update(updates)
        with open(s_dir / "state.json", "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, default=str)

    @classmethod
    def save_image_array(cls, session_id: str, filename: str, img: np.ndarray) -> Path:
        s_dir = cls.get_session_dir(session_id)
        out_path = s_dir / filename
        if img.dtype in [np.float32, np.float64]:
            img_to_save = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img_to_save = img
        cv2.imwrite(str(out_path), img_to_save)
        return out_path

    @staticmethod
    def array_to_base64_jpeg(img: np.ndarray, quality: int = 88) -> str:
        if img.dtype in [np.float32, np.float64]:
            img_8u = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img_8u = img

        success, encoded = cv2.imencode(".jpg", img_8u, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not success:
            return ""
        b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    @staticmethod
    def array_to_base64_png(img: np.ndarray) -> str:
        if img.dtype in [np.float32, np.float64]:
            img_8u = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img_8u = img

        success, encoded = cv2.imencode(".png", img_8u)
        if not success:
            return ""
        b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
