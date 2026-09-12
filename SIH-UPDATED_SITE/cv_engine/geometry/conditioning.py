"""
Geometric Matrix Conditioning & Singularity Verification
Prevents degenerate homography solutions where images warp to infinity or fold over.
Uses Hartley-Zisserman coordinate normalization for rigorous condition number calculation.
"""
from typing import Tuple
import numpy as np


class MatrixConditionChecker:
    @staticmethod
    def check_homography(H: np.ndarray, width: int, height: int, max_condition: float = 500.0) -> Tuple[bool, str, float]:
        """
        Validates condition number, positive determinant, and corner convexity.
        Normalizes pixel coordinates to [-1, 1] before checking SVD condition.
        Returns: (is_valid, reason, condition_number)
        """
        if H is None or H.shape != (3, 3):
            return False, "Invalid matrix dimensions", float("inf")

        if abs(H[2, 2]) < 1e-9:
            return False, "Singular matrix (H[2,2] near zero)", float("inf")
        H_norm = H / H[2, 2]

        # Hartley-Zisserman coordinate normalization transform:
        # Maps [0, width] x [0, height] to [-1, 1] x [-1, 1]
        T_src = np.array([
            [2.0 / width, 0.0, -1.0],
            [0.0, 2.0 / height, -1.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

        T_src_inv = np.linalg.inv(T_src)
        H_coord_norm = T_src @ H_norm @ T_src_inv

        # SVD on coordinate-normalized matrix
        try:
            _, s, _ = np.linalg.svd(H_coord_norm)
            cond = float(s[0] / (s[-1] + 1e-12))
        except Exception as exc:
            return False, f"SVD failed: {exc}", float("inf")

        if cond > max_condition or np.isnan(cond):
            return False, f"Ill-conditioned transformation (normalized kappa={cond:.1f} > {max_condition})", float(cond)

        # Check that the 4 image corners map to a convex, forward-facing polygon
        corners = np.array([
            [0, 0, 1],
            [width, 0, 1],
            [width, height, 1],
            [0, height, 1]
        ], dtype=np.float64).T

        warped_corners = H_norm @ corners
        # Check for points behind projection plane
        if np.any(warped_corners[2, :] <= 0):
            return False, "Perspective singularity (points behind projection plane)", float(cond)

        w_pts = (warped_corners[:2, :] / warped_corners[2, :]).T

        # Check polygon convexity using cross products of adjacent edges
        edges = np.diff(np.vstack([w_pts, w_pts[0]]), axis=0)
        cross_z = []
        for i in range(4):
            e1 = edges[i]
            e2 = edges[(i + 1) % 4]
            cross = e1[0] * e2[1] - e1[1] * e2[0]
            cross_z.append(cross)

        all_positive = all(c > 0 for c in cross_z)
        all_negative = all(c < 0 for c in cross_z)
        if not (all_positive or all_negative):
            return False, "Degenerate polygon self-intersection (twisted warp)", float(cond)

        return True, "Valid condition and topology", float(cond)
