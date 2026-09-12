"""
Sub-Pixel Image Warper for Lunar Registration
"""
from typing import Tuple
import numpy as np
import cv2


class LunarImageWarper:
    @staticmethod
    def warp_source_to_reference(
        source_img: np.ndarray,
        reference_shape: Tuple[int, int],  # (height, width)
        H_3x3: np.ndarray,
        interpolation: str = "bicubic"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Warps source image onto reference coordinate frame.
        Returns: (warped_image, overlap_mask)
        """
        ref_h, ref_w = reference_shape[:2]

        interp_flag = cv2.INTER_CUBIC if interpolation.lower() == "bicubic" else cv2.INTER_LANCZOS4

        warped = cv2.warpPerspective(
            source_img,
            H_3x3,
            (ref_w, ref_h),
            flags=interp_flag + cv2.WARP_FILL_OUTLIERS,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )

        # Generate binary mask of warped valid region
        ones_src = np.ones_like(source_img, dtype=np.uint8)
        mask = cv2.warpPerspective(
            ones_src,
            H_3x3,
            (ref_w, ref_h),
            flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )

        return warped.astype(np.float32), mask.astype(bool)
