"""
Radiometric dynamic range normalizer for scientific lunar imagery.
"""
import numpy as np


class LunarNormalizer:
    @staticmethod
    def percentile_stretch(image: np.ndarray, lower_pct: float = 1.0, upper_pct: float = 99.0) -> np.ndarray:
        """Robust percentile clipping to suppress extreme specular glints and deep shadow voids."""
        clean = np.nan_to_num(image, nan=0.0, posinf=1.0, neginf=0.0)
        p_low, p_high = np.percentile(clean, (lower_pct, upper_pct))
        if p_high > p_low:
            stretched = np.clip((clean - p_low) / (p_high - p_low), 0.0, 1.0)
        else:
            stretched = clean
        return stretched.astype(np.float32)

    @staticmethod
    def standardize_8u(image: np.ndarray) -> np.ndarray:
        """Converts float32 [0.0, 1.0] to uint8 [0, 255] for standard OpenCV keypoint routines."""
        return np.clip(image * 255.0, 0, 255).astype(np.uint8)
