"""
Sub-Pixel Quadratic & Cross-Correlation Refinement for Keypoint Correspondences
"""
import numpy as np
import cv2


class SubPixelRefiner:
    @staticmethod
    def refine_match_locations(
        img_src: np.ndarray,
        img_ref: np.ndarray,
        src_pt: np.ndarray,
        ref_pt: np.ndarray,
        patch_radius: int = 7
    ) -> np.ndarray:
        """
        Refines ref_pt with sub-pixel 2D quadratic peak fitting on normalized cross-correlation.
        """
        h_s, w_s = img_src.shape[:2]
        h_r, w_r = img_ref.shape[:2]

        sx, sy = int(round(src_pt[0])), int(round(src_pt[1]))
        rx, ry = int(round(ref_pt[0])), int(round(ref_pt[1]))

        # Boundary check
        r = patch_radius
        search_r = r + 3
        if (sx - r < 0 or sx + r >= w_s or sy - r < 0 or sy + r >= h_s or
            rx - search_r < 0 or rx + search_r >= w_r or ry - search_r < 0 or ry + search_r >= h_r):
            return ref_pt

        patch_src = img_src[sy - r:sy + r + 1, sx - r:sx + r + 1].astype(np.float32)
        search_ref = img_ref[ry - search_r:ry + search_r + 1, rx - search_r:rx + search_r + 1].astype(np.float32)

        res = cv2.matchTemplate(search_ref, patch_src, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Sub-pixel peak fitting around max_loc
        mx, my = max_loc
        if 0 < mx < res.shape[1] - 1 and 0 < my < res.shape[0] - 1:
            dx = (res[my, mx + 1] - res[my, mx - 1]) / (2.0 * (2.0 * res[my, mx] - res[my, mx + 1] - res[my, mx - 1] + 1e-6))
            dy = (res[my + 1, mx] - res[my - 1, mx]) / (2.0 * (2.0 * res[my, mx] - res[my + 1, mx] - res[my - 1, mx] + 1e-6))
            sub_x = rx - search_r + r + mx + float(np.clip(dx, -0.5, 0.5))
            sub_y = ry - search_r + r + my + float(np.clip(dy, -0.5, 0.5))
            return np.array([sub_x, sub_y], dtype=np.float32)

        return ref_pt
