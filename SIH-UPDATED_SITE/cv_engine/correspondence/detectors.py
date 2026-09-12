"""
Scale-Invariant Feature Detectors & Descriptors with Sub-Pixel Refinement for Lunar Terrain
"""
from typing import List, Tuple
import numpy as np
import cv2
from cv_engine.correspondence.anms import LunarANMS


class LunarFeatureDetector:
    """Detects repeatable interest points and extracts descriptors across lunar terrain."""

    def __init__(self, method: str = "sift", max_features: int = 1500, use_anms: bool = True):
        self.method = method.lower()
        self.max_features = max_features
        self.use_anms = use_anms

        if self.method == "sift":
            self.detector = cv2.SIFT_create(
                nfeatures=max_features * 2 if use_anms else max_features,
                contrastThreshold=0.012,
                edgeThreshold=12.0,
                sigma=1.4
            )
        elif self.method == "orb":
            self.detector = cv2.ORB_create(
                nfeatures=max_features * 2 if use_anms else max_features,
                scaleFactor=1.2,
                nlevels=8,
                edgeThreshold=15
            )
        elif self.method == "akaze":
            self.detector = cv2.AKAZE_create(
                threshold=0.001
            )
        else:
            self.detector = cv2.SIFT_create(nfeatures=max_features)

    def detect(self, image_8u: np.ndarray) -> List[cv2.KeyPoint]:
        """Convenience method returning detected keypoints."""
        kps, _ = self.detect_and_compute(image_8u)
        return kps

    def detect_keypoints(self, image_8u: np.ndarray) -> List[cv2.KeyPoint]:
        """Detect keypoints without coupling them to the detector's native descriptor."""
        kps = self.detector.detect(image_8u, None)
        if not kps:
            return []
        if self.use_anms and len(kps) > self.max_features:
            return LunarANMS.filter_keypoints(kps, max_points=self.max_features)
        return kps[:self.max_features]

    def detect_and_compute(
        self,
        image_8u: np.ndarray
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Detects keypoints, computes descriptors, and optionally applies ANMS spatial dispersion."""
        kps, descs = self.detector.detectAndCompute(image_8u, None)
        if not kps or descs is None or len(descs) == 0:
            return [], np.empty((0, 128), dtype=np.float32)

        if descs.dtype != np.float32:
            descs = descs.astype(np.float32)

        # Apply ANMS for uniform spatial distribution
        if self.use_anms and len(kps) > self.max_features:
            filtered_kps = LunarANMS.filter_keypoints(kps, max_points=self.max_features)
            # Retain matching descriptor rows
            kp_dict = {id(kp): i for i, kp in enumerate(kps)}
            valid_indices = [kp_dict[id(fkp)] for fkp in filtered_kps if id(fkp) in kp_dict]
            return filtered_kps, descs[valid_indices]

        return kps[:self.max_features], descs[:self.max_features]
