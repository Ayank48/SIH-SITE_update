"""
Lunar Registration Blending & Visual Quality Products
Generates Difference Map, Checkerboard, False Color Composite, and Alpha Overlay.
"""
from typing import Tuple
import numpy as np
import cv2


class LunarRegistrationBlender:
    @staticmethod
    def create_difference_map(
        ref_img: np.ndarray,
        warped_src: np.ndarray,
        overlap_mask: np.ndarray
    ) -> np.ndarray:
        """
        Calculates normalized absolute difference heatmap within the overlap area.
        Returns BGR uint8 heatmap.
        """
        diff = np.abs(ref_img - warped_src)
        diff[~overlap_mask] = 0.0

        diff_8u = np.clip(diff * 255.0, 0, 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(diff_8u, cv2.COLORMAP_INFERNO)
        heatmap[~overlap_mask] = [15, 23, 42]  # Deep slate for non-overlapping
        return heatmap

    @staticmethod
    def create_checkerboard(
        ref_img: np.ndarray,
        warped_src: np.ndarray,
        tiles: int = 8
    ) -> np.ndarray:
        """
        Alternating checkerboard tiles between reference and warped source.
        Allows immediate visual verification of continuous crater edges.
        """
        h, w = ref_img.shape[:2]
        tile_h = h // tiles
        tile_w = w // tiles

        composite = ref_img.copy()
        for i in range(tiles):
            for j in range(tiles):
                if (i + j) % 2 == 1:
                    y1, y2 = i * tile_h, (i + 1) * tile_h if i < tiles - 1 else h
                    x1, x2 = j * tile_w, (j + 1) * tile_w if j < tiles - 1 else w
                    composite[y1:y2, x1:x2] = warped_src[y1:y2, x1:x2]

        return np.clip(composite * 255.0, 0, 255).astype(np.uint8)

    @staticmethod
    def create_false_color_composite(
        ref_img: np.ndarray,
        warped_src: np.ndarray,
        overlap_mask: np.ndarray
    ) -> np.ndarray:
        """
        RGB composite: Red = Warped Source, Green = Reference, Blue = 0.
        Coinciding structures appear in bright yellow. Spatial shifts appear as red/green fringing.
        """
        h, w = ref_img.shape[:2]
        composite = np.zeros((h, w, 3), dtype=np.uint8)

        # Red channel = Warped source
        composite[:, :, 2] = np.clip(warped_src * 255.0, 0, 255).astype(np.uint8)
        # Green channel = Reference
        composite[:, :, 1] = np.clip(ref_img * 255.0, 0, 255).astype(np.uint8)
        # Blue channel = slight fill of reference for contrast
        composite[:, :, 0] = np.clip((ref_img * 0.3) * 255.0, 0, 255).astype(np.uint8)

        return composite
