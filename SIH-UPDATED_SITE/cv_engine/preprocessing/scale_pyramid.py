"""
Scale-Space Harmonization & Pyramid Builder for Lunar Imagery
Handles extreme scale differences (e.g., OHRC 0.25m vs TMC 5.0m vs IIRS 80m).
"""
from typing import List, Tuple, Optional
import numpy as np
import cv2


class ScalePyramidHarmonizer:
    @staticmethod
    def harmonize_by_gsd(
        source_img: np.ndarray,
        ref_img: np.ndarray,
        src_gsd: float,
        ref_gsd: float
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Harmonizes source and reference images to matching ground sample distance.
        Returns: (harmonized_source, harmonized_ref, applied_source_scale_factor)
        """
        if src_gsd <= 0 or ref_gsd <= 0:
            return source_img, ref_img, 1.0

        # Scale factor needed for source to match reference GSD
        scale_factor = src_gsd / ref_gsd

        if np.isclose(scale_factor, 1.0, atol=0.05):
            return source_img, ref_img, 1.0

        # Downsample the higher-resolution image
        if scale_factor < 1.0:
            # Source has smaller GSD (higher spatial resolution, like OHRC)
            # Downscale source to match reference
            new_w = max(16, int(round(source_img.shape[1] * scale_factor)))
            new_h = max(16, int(round(source_img.shape[0] * scale_factor)))
            downscaled_src = cv2.resize(source_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            return downscaled_src, ref_img, scale_factor
        else:
            # Reference has smaller GSD
            inv_factor = 1.0 / scale_factor
            new_w = max(16, int(round(ref_img.shape[1] * inv_factor)))
            new_h = max(16, int(round(ref_img.shape[0] * inv_factor)))
            downscaled_ref = cv2.resize(ref_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            return source_img, downscaled_ref, 1.0

    @staticmethod
    def build_scale_pyramid(image: np.ndarray, octaves: int = 4, scale_step: float = 1.414) -> List[np.ndarray]:
        """Builds a geometric scale pyramid."""
        pyramid = [image]
        current = image
        for i in range(1, octaves):
            factor = 1.0 / (scale_step ** i)
            new_w = max(16, int(image.shape[1] * factor))
            new_h = max(16, int(image.shape[0] * factor))
            level = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            pyramid.append(level)
        return pyramid

    @staticmethod
    def estimate_global_scale_rotation_fourier(
        img1: np.ndarray,
        img2: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Estimates global scale factor and rotation angle between two images
        using Fourier-Mellin log-polar phase correlation.
        Returns (estimated_scale, estimated_rotation_degrees, correlation_confidence).
        """
        # Ensure square matching window
        size = min(img1.shape[0], img1.shape[1], img2.shape[0], img2.shape[1], 512)
        win1 = cv2.resize(img1, (size, size), interpolation=cv2.INTER_AREA)
        win2 = cv2.resize(img2, (size, size), interpolation=cv2.INTER_AREA)

        # Apply Hanning window
        hann = cv2.createHanningWindow((size, size), cv2.CV_32F)
        win1_w = (win1 * hann).astype(np.float32)
        win2_w = (win2 * hann).astype(np.float32)

        # Compute magnitude spectra
        f1 = np.fft.fftshift(np.abs(np.fft.fft2(win1_w)))
        f2 = np.fft.fftshift(np.abs(np.fft.fft2(win2_w)))

        # High-pass filter spectra to remove DC
        radius = size // 2
        center = (radius, radius)

        # Log-polar transform of spectra
        m = size / np.log(radius)
        lp1 = cv2.warpPolar(f1, (size, size), center, radius, cv2.WARP_POLAR_LOG + cv2.INTER_LINEAR)
        lp2 = cv2.warpPolar(f2, (size, size), center, radius, cv2.WARP_POLAR_LOG + cv2.INTER_LINEAR)

        # Phase correlation on log-polar domain
        try:
            (shift_x, shift_y), response = cv2.phaseCorrelate(lp1, lp2)
            # shift_x maps to log-scale, shift_y maps to rotation angle
            angle_deg = -(shift_y * 360.0 / size)
            if angle_deg > 180:
                angle_deg -= 360
            elif angle_deg < -180:
                angle_deg += 360

            scale = np.exp(shift_x / m)
            # Bound scale to reasonable bounds
            scale = float(np.clip(scale, 0.1, 10.0))
            return scale, float(angle_deg), float(response)
        except Exception:
            return 1.0, 0.0, 0.0
