"""
TEAM ZERODAY Module 1: Lunar Correspondence Court
Adjudicates candidate matches via multi-evidence judicial arbitration:
1. Photometric / Spectral local patch correlation
2. Local affine neighborhood consistency
3. Distance-ratio context preservation
4. Global consensus reprojection residual
Verdicts: ACCEPT, UNCERTAIN, REJECT.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import numpy as np
import cv2
from scipy.spatial import KDTree
from cv_engine.correspondence.coarse_to_fine import CandidateCorrespondence


@dataclass
class MatchVerdict:
    match_id: int
    src_pt: Tuple[float, float]
    ref_pt: Tuple[float, float]
    verdict: str  # "ACCEPT", "UNCERTAIN", "REJECT"
    confidence_score: float  # [0.0, 1.0]
    evidence_photometric: float  # [0.0, 1.0]
    evidence_local_geometry: float  # [0.0, 1.0]
    evidence_context_ratio: float  # [0.0, 1.0]
    evidence_global_residual: float  # [0.0, 1.0]
    transfer_residual_px: float
    decision_rationale: str


class LunarCorrespondenceCourt:
    """Multi-evidence judicial verifier for lunar correspondences."""

    def __init__(
        self,
        accept_threshold: float = 0.68,
        uncertain_threshold: float = 0.40,
        max_residual_tol_px: float = 4.0
    ):
        self.accept_thresh = accept_threshold
        self.uncertain_thresh = uncertain_threshold
        self.max_residual_tol = max_residual_tol_px

    def adjudicate(
        self,
        matches: List[CandidateCorrespondence],
        img_src: np.ndarray,
        img_ref: np.ndarray,
        H_3x3: np.ndarray,
        inlier_mask: np.ndarray,
        patch_radius: int = 8,
        k_neighbors: int = 5
    ) -> List[MatchVerdict]:
        """
        Conducts a multi-evidence trial on every candidate correspondence.
        """
        n = len(matches)
        if n == 0:
            return []

        src_pts = np.array([m.src_pt for m in matches], dtype=np.float32)
        ref_pts = np.array([m.ref_pt for m in matches], dtype=np.float32)

        # Build KD-tree for spatial neighborhood consistency
        k_val = min(k_neighbors + 1, n)
        kd_src = KDTree(src_pts)

        # 1. Global transfer residuals
        src_homo = np.hstack([src_pts, np.ones((n, 1), dtype=np.float32)]).T
        warped_homo = H_3x3 @ src_homo
        warped_pts = (warped_homo[:2, :] / (warped_homo[2, :] + 1e-12)).T
        residuals = np.linalg.norm(ref_pts - warped_pts, axis=1)

        h_s, w_s = img_src.shape[:2]
        h_r, w_r = img_ref.shape[:2]
        pr = patch_radius

        verdicts = []

        for i, match in enumerate(matches):
            sx, sy = int(round(match.src_pt[0])), int(round(match.src_pt[1]))
            rx, ry = int(round(match.ref_pt[0])), int(round(match.ref_pt[1]))
            res_px = float(residuals[i])
            is_ransac_inlier = bool(inlier_mask[i]) if i < len(inlier_mask) else False

            # Evidence 1: Photometric / Patch ZNCC
            ev_photo = 0.5
            if (sx - pr >= 0 and sx + pr < w_s and sy - pr >= 0 and sy + pr < h_s and
                rx - pr >= 0 and rx + pr < w_r and ry - pr >= 0 and ry + pr < h_r):
                p_s = img_src[sy - pr:sy + pr + 1, sx - pr:sx + pr + 1].astype(np.float32)
                p_r = img_ref[ry - pr:ry + pr + 1, rx - pr:rx + pr + 1].astype(np.float32)
                # ZNCC
                p_s_norm = p_s - np.mean(p_s)
                p_r_norm = p_r - np.mean(p_r)
                denom = np.linalg.norm(p_s_norm) * np.linalg.norm(p_r_norm)
                if denom > 1e-6:
                    zncc = float(np.sum(p_s_norm * p_r_norm) / denom)
                    ev_photo = float(np.clip((zncc + 1.0) / 2.0, 0.0, 1.0))

            # Evidence 2 & 3: Neighborhood Local Affine & Distance Ratio
            ev_geom = 0.5
            ev_context = 0.5

            if k_val > 2:
                _, neighbor_idxs = kd_src.query(src_pts[i], k=k_val)
                # Exclude self
                neighbor_idxs = [idx for idx in neighbor_idxs if idx != i]
                if neighbor_idxs:
                    src_dists = np.linalg.norm(src_pts[neighbor_idxs] - src_pts[i], axis=1)
                    ref_dists = np.linalg.norm(ref_pts[neighbor_idxs] - ref_pts[i], axis=1)
                    scale_ratios = ref_dists / (src_dists + 1e-6)
                    # Consistency: standard deviation of scale ratios in neighborhood should be low
                    ratio_std = np.std(scale_ratios)
                    ev_context = float(np.exp(-ratio_std / 1.0))

                    # Orientation delta consistency
                    src_angles = np.arctan2(src_pts[neighbor_idxs, 1] - src_pts[i, 1], src_pts[neighbor_idxs, 0] - src_pts[i, 0])
                    ref_angles = np.arctan2(ref_pts[neighbor_idxs, 1] - ref_pts[i, 1], ref_pts[neighbor_idxs, 0] - ref_pts[i, 0])
                    angle_diffs = np.mod(ref_angles - src_angles + np.pi, 2 * np.pi) - np.pi
                    angle_std = np.std(angle_diffs)
                    ev_geom = float(np.exp(-angle_std / (np.pi / 4)))

            # Evidence 4: Global Transfer Residual Score
            ev_residual = float(np.exp(-res_px / self.max_residual_tol))

            # Weighted evidence aggregation
            w_photo = 0.20
            w_geom = 0.25
            w_context = 0.20
            w_residual = 0.35

            confidence = (
                w_photo * ev_photo +
                w_geom * ev_geom +
                w_context * ev_context +
                w_residual * ev_residual
            )

            # Adjudication Decision
            if confidence >= self.accept_thresh and res_px <= self.max_residual_tol and is_ransac_inlier:
                verdict = "ACCEPT"
                rationale = f"Consensus verified: low transfer error ({res_px:.2f} px) & strong geometric consistency."
            elif confidence < self.uncertain_thresh or res_px > (self.max_residual_tol * 2.5) or not is_ransac_inlier:
                verdict = "REJECT"
                rationale = f"Outlier rejected: high residual ({res_px:.2f} px) or inconsistent neighborhood deformation."
            else:
                verdict = "UNCERTAIN"
                rationale = f"Borderline confidence ({confidence:.2f}): moderate residual ({res_px:.2f} px)."

            verdicts.append(MatchVerdict(
                match_id=i,
                src_pt=tuple(match.src_pt),
                ref_pt=tuple(match.ref_pt),
                verdict=verdict,
                confidence_score=round(confidence, 4),
                evidence_photometric=round(ev_photo, 4),
                evidence_local_geometry=round(ev_geom, 4),
                evidence_context_ratio=round(ev_context, 4),
                evidence_global_residual=round(ev_residual, 4),
                transfer_residual_px=round(res_px, 3),
                decision_rationale=rationale
            ))

        return verdicts
