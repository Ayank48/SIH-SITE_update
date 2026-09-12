"""
Adaptive Non-Maximal Suppression (ANMS) for Uniform Keypoint Dispersion
Guarantees reliable correspondences distributed across the entire lunar surface
rather than clustering on a single high-contrast crater rim.
"""
from typing import List
import numpy as np
import cv2
from scipy.spatial import KDTree


class LunarANMS:
    """
    Implements Brown et al. / Top-N Adaptive Non-Maximal Suppression.
    Ensures spatial distribution index is maximized across lunar terrain.
    """

    @staticmethod
    def filter_keypoints(
        keypoints: List[cv2.KeyPoint],
        max_points: int = 800,
        c_robust: float = 0.9
    ) -> List[cv2.KeyPoint]:
        """
        Suppresses spatially redundant keypoints to retain max_points with uniform coverage.
        """
        if len(keypoints) <= max_points or len(keypoints) == 0:
            return keypoints

        # Sort keypoints by response in descending order
        sorted_kps = sorted(keypoints, key=lambda k: k.response, reverse=True)
        pts = np.array([k.pt for k in sorted_kps], dtype=np.float32)
        responses = np.array([k.response for k in sorted_kps], dtype=np.float32)
        n = len(sorted_kps)

        # Compute suppression radius for each keypoint
        # r_i = min_{j: response_j * c_robust > response_i} ||pt_i - pt_j||
        radii = np.full(n, np.inf, dtype=np.float32)

        # Optimization using spatial partitioning or vectorized distance
        # For n up to 3000, we can use an efficient vectorized chunk search
        for i in range(n):
            # Points with stronger response (since sorted, indices 0..i-1 have response >= response_i)
            # Find subset where response_j * c_robust > response_i
            stronger_indices = np.where(responses[:i] * c_robust > responses[i])[0]
            if len(stronger_indices) > 0:
                diffs = pts[stronger_indices] - pts[i]
                dists = np.sum(diffs ** 2, axis=1)
                radii[i] = np.min(dists)
            else:
                radii[i] = np.inf

        # Select top max_points by radius
        top_indices = np.argsort(-radii)[:max_points]
        return [sorted_kps[idx] for idx in top_indices]
