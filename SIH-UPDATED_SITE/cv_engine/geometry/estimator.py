"""
Robust Transformation Estimation via USAC-MAGSAC++ and RANSAC
Supports Homography and Affine model estimation with automatic condition-based model selection.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import cv2
from cv_engine.correspondence.coarse_to_fine import CandidateCorrespondence
from cv_engine.geometry.conditioning import MatrixConditionChecker


@dataclass
class EstimationResult:
    model_type: str  # "homography" or "affine"
    matrix_3x3: np.ndarray  # Always 3x3 for unified warping
    inlier_mask: np.ndarray  # boolean array (len == len(matches))
    inlier_count: int
    tentative_count: int
    inlier_ratio: float
    transfer_errors: np.ndarray  # array of Euclidean distances in pixels
    condition_number: float
    is_valid: bool
    status_message: str


class RobustGeometricEstimator:
    """Estimates robust geometric transformations between lunar image coordinates."""

    def __init__(
        self,
        ransac_reproj_threshold: float = 4.0,
        max_iterations: int = 5000,
        confidence: float = 0.999,
        preferred_model: str = "auto"  # "auto", "homography", "affine"
    ):
        self.reproj_threshold = ransac_reproj_threshold
        self.max_iters = max_iterations
        self.confidence = confidence
        self.preferred_model = preferred_model.lower()

    def estimate(
        self,
        matches: List[CandidateCorrespondence],
        img_width: int,
        img_height: int
    ) -> EstimationResult:
        """Executes robust geometric estimation and returns mathematical estimation result."""
        n = len(matches)
        if n < 4:
            return EstimationResult(
                model_type="none",
                matrix_3x3=np.eye(3, dtype=np.float64),
                inlier_mask=np.zeros(n, dtype=bool),
                inlier_count=0,
                tentative_count=n,
                inlier_ratio=0.0,
                transfer_errors=np.zeros(n, dtype=np.float32),
                condition_number=1.0,
                is_valid=False,
                status_message=f"Insufficient tentative matches ({n} < 4 required for geometric model)"
            )

        src_pts = np.array([m.src_pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
        ref_pts = np.array([m.ref_pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)

        # 1. Attempt Homography estimation via USAC_MAGSAC
        H_candidate = None
        inliers_H = None
        cond_H = float("inf")
        h_valid = False
        h_msg = ""

        if self.preferred_model in ["auto", "homography"]:
            try:
                H_est, mask_H = cv2.findHomography(
                    src_pts,
                    ref_pts,
                    method=cv2.USAC_MAGSAC,
                    ransacReprojThreshold=self.reproj_threshold,
                    maxIters=self.max_iters,
                    confidence=self.confidence
                )
                if H_est is not None and mask_H is not None:
                    h_valid, h_msg, cond_H = MatrixConditionChecker.check_homography(H_est, img_width, img_height)
                    if h_valid and np.sum(mask_H) >= 4:
                        H_candidate = H_est
                        inliers_H = mask_H.ravel().astype(bool)
                    else:
                        h_valid = False
            except Exception as e:
                h_msg = f"Homography error: {e}"

        # 2. Estimate Affine model via RANSAC
        A_candidate = None
        inliers_A = None
        cond_A = float("inf")
        a_valid = False

        if self.preferred_model in ["auto", "affine"] or not h_valid:
            try:
                A_est, mask_A = cv2.estimateAffine2D(
                    src_pts,
                    ref_pts,
                    method=cv2.RANSAC,
                    ransacReprojThreshold=self.reproj_threshold,
                    maxIters=self.max_iters,
                    confidence=self.confidence
                )
                if A_est is not None and mask_A is not None and np.sum(mask_A) >= 3:
                    det_A = np.linalg.det(A_est[:2, :2])
                    if abs(det_A) > 1e-6:
                        H_from_A = np.eye(3, dtype=np.float64)
                        H_from_A[:2, :] = A_est
                        a_valid, _, cond_A = MatrixConditionChecker.check_homography(H_from_A, img_width, img_height)
                        if a_valid:
                            A_candidate = H_from_A
                            inliers_A = mask_A.ravel().astype(bool)
            except Exception:
                pass

        # 3. Model selection decision
        selected_model = "none"
        selected_matrix = np.eye(3, dtype=np.float64)
        selected_mask = np.zeros(n, dtype=bool)
        selected_cond = 1.0

        if self.preferred_model == "affine" and a_valid:
            selected_model = "affine"
            selected_matrix = A_candidate
            selected_mask = inliers_A
            selected_cond = cond_A
        elif self.preferred_model == "homography" and h_valid:
            selected_model = "homography"
            selected_matrix = H_candidate
            selected_mask = inliers_H
            selected_cond = cond_H
        elif h_valid and inliers_H is not None:
            # Auto prefers homography if condition is stable and inlier count is sufficient
            selected_model = "homography"
            selected_matrix = H_candidate
            selected_mask = inliers_H
            selected_cond = cond_H
        elif a_valid and inliers_A is not None:
            selected_model = "affine"
            selected_matrix = A_candidate
            selected_mask = inliers_A
            selected_cond = cond_A
        else:
            return EstimationResult(
                model_type="none",
                matrix_3x3=np.eye(3, dtype=np.float64),
                inlier_mask=np.zeros(n, dtype=bool),
                inlier_count=0,
                tentative_count=n,
                inlier_ratio=0.0,
                transfer_errors=np.zeros(n, dtype=np.float32),
                condition_number=float("inf"),
                is_valid=False,
                status_message=f"Geometric estimation failed: {h_msg or 'No consensus model found'}"
            )

        # 4. Compute true Euclidean transfer errors for all matches
        src_homo = np.hstack([src_pts.reshape(-1, 2), np.ones((n, 1), dtype=np.float64)]).T
        mapped_homo = selected_matrix @ src_homo
        mapped_pts = (mapped_homo[:2, :] / (mapped_homo[2, :] + 1e-12)).T

        ref_2d = ref_pts.reshape(-1, 2)
        transfer_errors = np.linalg.norm(ref_2d - mapped_pts, axis=1).astype(np.float32)

        inlier_count = int(np.sum(selected_mask))
        inlier_ratio = float(inlier_count / n) if n > 0 else 0.0

        return EstimationResult(
            model_type=selected_model,
            matrix_3x3=selected_matrix,
            inlier_mask=selected_mask,
            inlier_count=inlier_count,
            tentative_count=n,
            inlier_ratio=inlier_ratio,
            transfer_errors=transfer_errors,
            condition_number=float(selected_cond),
            is_valid=True,
            status_message=f"Successfully converged with {selected_model} model (inliers: {inlier_count}/{n})"
        )
