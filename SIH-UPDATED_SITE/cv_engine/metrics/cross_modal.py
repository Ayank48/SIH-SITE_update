"""
Cross-Modal & Structural Registration Metrics
Computes Normalized Mutual Information (NMI) and SSIM in the registered overlap area.
"""
from typing import Tuple
import numpy as np
from skimage.metrics import structural_similarity as ssim


class CrossModalMetrics:
    @staticmethod
    def calculate_nmi(
        ref_img: np.ndarray,
        warped_src: np.ndarray,
        overlap_mask: np.ndarray,
        bins: int = 32
    ) -> float:
        """
        Calculates Normalized Mutual Information (NMI) between reference and warped source.
        NMI(X, Y) = 2 * I(X, Y) / (H(X) + H(Y))
        Particularly suited for cross-modal pairs (e.g., TMC optical vs IIRS infrared).
        """
        ref_valid = ref_img[overlap_mask]
        warped_valid = warped_src[overlap_mask]

        if len(ref_valid) < 100:
            return 0.0

        hist_2d, _, _ = np.histogram2d(ref_valid, warped_valid, bins=bins, range=[[0, 1], [0, 1]])
        pxy = hist_2d / float(np.sum(hist_2d))
        px = np.sum(pxy, axis=1)
        py = np.sum(pxy, axis=0)

        px = px[px > 0]
        py = py[py > 0]
        pxy = pxy[pxy > 0]

        hx = -np.sum(px * np.log(px))
        hy = -np.sum(py * np.log(py))
        hxy = -np.sum(pxy * np.log(pxy))

        mi = hx + hy - hxy
        if hx + hy <= 1e-9:
            return 0.0
        nmi = 2.0 * mi / (hx + hy)
        return float(np.clip(nmi, 0.0, 1.0))

    @staticmethod
    def calculate_ssim(
        ref_img: np.ndarray,
        warped_src: np.ndarray,
        overlap_mask: np.ndarray
    ) -> float:
        """
        Computes Structural Similarity Index (SSIM) on the bounding box of the valid overlap.
        """
        if not np.any(overlap_mask):
            return 0.0

        coords = np.argwhere(overlap_mask)
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1

        if (y1 - y0) < 16 or (x1 - x0) < 16:
            return 0.0

        crop_ref = ref_img[y0:y1, x0:x1]
        crop_warped = warped_src[y0:y1, x0:x1]

        val, _ = ssim(
            crop_ref,
            crop_warped,
            data_range=1.0,
            full=True
        )
        return float(np.clip(val, -1.0, 1.0))
