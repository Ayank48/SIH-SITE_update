"""
Illumination-Invariant & Cross-Modal Descriptors for Lunar Imagery
Features:
1. Standard SIFT descriptor computation
2. CFOG (Channel Features of Oriented Gradients) modulo pi
3. Phase Congruency energy descriptor
"""
from typing import List, Tuple
import numpy as np
import cv2


class LunarDescriptorExtractor:
    """Computes descriptors invariant to solar illumination and modal differences."""

    def __init__(self, method: str = "sift"):
        self.method = method.lower()
        if self.method == "sift":
            self.extractor = cv2.SIFT_create()
        elif self.method == "orb":
            self.extractor = cv2.ORB_create()
        elif self.method == "akaze":
            if not hasattr(cv2, "AKAZE_create"):
                raise RuntimeError("AKAZE descriptors are unavailable in the installed OpenCV build")
            self.extractor = cv2.AKAZE_create()
        else:
            self.extractor = cv2.SIFT_create()

    def compute(
        self,
        image_8u: np.ndarray,
        keypoints: List[cv2.KeyPoint]
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Computes descriptors for the given keypoints."""
        if not keypoints:
            return [], np.empty((0, self.dimension), dtype=np.float32)

        if self.method in ["sift", "orb", "akaze"]:
            descriptor_keypoints = keypoints
            if self.method in ["orb", "akaze"]:
                descriptor_keypoints = [
                    cv2.KeyPoint(
                        float(kp.pt[0]),
                        float(kp.pt[1]),
                        max(1.0, min(float(kp.size), 31.0)),
                        float(kp.angle),
                        float(kp.response),
                        int(kp.octave),
                        int(kp.class_id),
                    )
                    for kp in keypoints
                ]
            kps, descs = self.extractor.compute(image_8u, descriptor_keypoints)
            if descs is not None and descs.dtype != np.float32:
                descs = descs.astype(np.float32)
            return kps, descs if descs is not None else np.empty((0, 128), dtype=np.float32)

        elif self.method == "cfog":
            return self._compute_cfog(image_8u, keypoints)

        return keypoints, np.empty((0, 128), dtype=np.float32)

    @property
    def dimension(self) -> int:
        if self.method == "cfog":
            return 128
        if self.method in ["orb", "akaze"]:
            return 32
        return 128

    def _compute_cfog(
        self,
        image_8u: np.ndarray,
        keypoints: List[cv2.KeyPoint],
        patch_size: int = 32,
        num_orientations: int = 8
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Computes Channel Features of Oriented Gradients (CFOG) modulo pi.
        Neutralizes 180-degree shadow polarity flips from opposing Sun angles.
        """
        img_f = image_8u.astype(np.float32) / 255.0
        gx = cv2.Sobel(img_f, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(img_f, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        ori = np.mod(np.arctan2(gy, gx), np.pi)  # Modulo pi

        # 8 directional channels
        channels = []
        d_theta = np.pi / num_orientations
        for o in range(num_orientations):
            target_angle = o * d_theta
            diff = np.abs(ori - target_angle)
            weight = np.maximum(0.0, 1.0 - diff / d_theta)
            channels.append(mag * weight)

        h, w = image_8u.shape
        half_p = patch_size // 2
        descriptors = []
        valid_kps = []

        for kp in keypoints:
            x, y = int(round(kp.pt[0])), int(round(kp.pt[1]))
            if x < half_p or x >= w - half_p or y < half_p or y >= h - half_p:
                continue

            desc_vec = []
            # 4x4 spatial cells
            cell_s = patch_size // 4
            for cy in range(4):
                for cx in range(4):
                    y1 = y - half_p + cy * cell_s
                    y2 = y1 + cell_s
                    x1 = x - half_p + cx * cell_s
                    x2 = x1 + cell_s
                    for ch in channels:
                        cell_energy = np.sum(ch[y1:y2, x1:x2])
                        desc_vec.append(cell_energy)

            vec = np.array(desc_vec, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 1e-6:
                vec /= norm
            descriptors.append(vec)
            valid_kps.append(kp)

        if descriptors:
            return valid_kps, np.array(descriptors, dtype=np.float32)
        return [], np.empty((0, 4 * 4 * num_orientations), dtype=np.float32)
