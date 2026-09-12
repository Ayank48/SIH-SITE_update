"""
Lunar Image Ingestion & Metadata Normalizer
Handles 8-bit, 16-bit GeoTIFF, TIFF, PNG, JPEG with scientific radiometric scaling.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import numpy as np
import cv2
from PIL import Image
import tifffile


@dataclass
class LunarSensorProfile:
    name: str
    sensor_id: str
    nominal_gsd_m: float  # Ground Sample Distance in meters per pixel
    spectral_type: str    # "panchromatic", "hyperspectral", "multispectral"
    wavelength_um: str
    description: str


SENSOR_REGISTRY: Dict[str, LunarSensorProfile] = {
    "OHRC": LunarSensorProfile(
        name="Chandrayaan-2 OHRC",
        sensor_id="OHRC",
        nominal_gsd_m=0.25,
        spectral_type="panchromatic",
        wavelength_um="0.45 - 0.90",
        description="Orbiter High Resolution Camera (~0.25 m/pixel ultra-high resolution)"
    ),
    "TMC2": LunarSensorProfile(
        name="Chandrayaan-2 TMC-2",
        sensor_id="TMC2",
        nominal_gsd_m=5.0,
        spectral_type="panchromatic",
        wavelength_um="0.50 - 0.85",
        description="Terrain Mapping Camera-2 (5.0 m/pixel stereo coverage)"
    ),
    "IIRS": LunarSensorProfile(
        name="Chandrayaan-2 IIRS",
        sensor_id="IIRS",
        nominal_gsd_m=80.0,
        spectral_type="hyperspectral",
        wavelength_um="0.80 - 5.00",
        description="Imaging Infrared Spectrometer (~80 m/pixel SWIR mineralogy)"
    ),
    "LRO_NAC": LunarSensorProfile(
        name="LRO Narrow Angle Camera",
        sensor_id="LRO_NAC",
        nominal_gsd_m=0.50,
        spectral_type="panchromatic",
        wavelength_um="0.40 - 0.75",
        description="Lunar Reconnaissance Orbiter NAC reference imagery (~0.5 m/pixel)"
    ),
    "UNKNOWN": LunarSensorProfile(
        name="Generic / Unspecified Sensor",
        sensor_id="UNKNOWN",
        nominal_gsd_m=1.0,
        spectral_type="panchromatic",
        wavelength_um="Visible",
        description="Sensor unassigned or Blind Lunar Test mode"
    ),
}


class LunarImageLoader:
    """Scientific image loader for lunar optical and infrared imagery."""

    @staticmethod
    def load_image(file_path: Path) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Loads an image from file, converts to standardized float32 in range [0.0, 1.0].
        Returns (image_array, metadata_dict).
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        suffix = file_path.suffix.lower()
        raw_image: Optional[np.ndarray] = None
        bit_depth = 8

        if suffix in [".tif", ".tiff", ".geotiff"]:
            try:
                raw_image = tifffile.imread(str(file_path))
            except Exception:
                raw_image = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
        else:
            raw_image = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)

        if raw_image is None:
            # Fallback to PIL
            try:
                with Image.open(file_path) as pil_img:
                    raw_image = np.array(pil_img)
            except Exception as exc:
                raise ValueError(f"Failed to read image file {file_path}: {exc}")

        # Check raw image dimensions and bit depth
        if raw_image.dtype == np.uint16:
            bit_depth = 16
            normalized = raw_image.astype(np.float32) / 65535.0
        elif raw_image.dtype == np.uint8:
            bit_depth = 8
            normalized = raw_image.astype(np.float32) / 255.0
        elif np.issubdtype(raw_image.dtype, np.floating):
            bit_depth = 32
            min_v, max_v = np.min(raw_image), np.max(raw_image)
            if max_v > min_v:
                normalized = (raw_image.astype(np.float32) - min_v) / (max_v - min_v)
            else:
                normalized = np.zeros_like(raw_image, dtype=np.float32)
        else:
            normalized = raw_image.astype(np.float32)
            normalized = (normalized - np.min(normalized)) / (np.ptp(normalized) + 1e-8)

        # Handle multichannel (convert to single-channel grayscale float32 for CV pipeline)
        if normalized.ndim == 3:
            channels = normalized.shape[2]
            if channels >= 3:
                # BGR / RGB to Grayscale
                gray = 0.299 * normalized[:, :, 0] + 0.587 * normalized[:, :, 1] + 0.114 * normalized[:, :, 2]
            else:
                gray = normalized[:, :, 0]
        else:
            channels = 1
            gray = normalized

        h, w = gray.shape[:2]

        metadata = {
            "file_name": file_path.name,
            "width": int(w),
            "height": int(h),
            "original_channels": int(channels),
            "original_bit_depth": int(bit_depth),
            "original_dtype": str(raw_image.dtype),
            "mean_intensity": float(np.mean(gray)),
            "std_intensity": float(np.std(gray)),
            "min_intensity": float(np.min(gray)),
            "max_intensity": float(np.max(gray)),
        }

        return gray, metadata

    @staticmethod
    def get_sensor_profile(sensor_id: str) -> LunarSensorProfile:
        normalized_id = sensor_id.upper().replace("-", "").replace(" ", "")
        for key, profile in SENSOR_REGISTRY.items():
            if key in normalized_id or normalized_id in key:
                return profile
        return SENSOR_REGISTRY["UNKNOWN"]
