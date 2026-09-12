"""
TEAM ZERODAY Module 2: Lunar Correspondence DNA
Derives an authentic, deterministic mathematical fingerprint of the registration relationship.
Based on geometric moments, conditioning, spatial dispersion entropy, and residual distribution.
"""
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import numpy as np
from cv_engine.metrics.spatial_distribution import SpatialDistributionMetrics
from cv_engine.metrics.cross_modal import CrossModalMetrics


@dataclass
class LunarCorrespondenceDNAResult:
    canonical_hash: str
    dna_vector: List[float]  # 8-dimensional feature vector
    scale_factor: float
    rotation_deg: float
    matrix_condition_log10: float
    spatial_entropy: float
    mean_residual_px: float
    residual_variance: float
    residual_skewness: float
    mutual_information: float
    certificate_id: str


class LunarCorrespondenceDNA:
    """Scientific fingerprint generator for lunar image correspondences."""

    @staticmethod
    def generate_dna(
        H_3x3: np.ndarray,
        inlier_src_pts: np.ndarray,
        inlier_ref_pts: np.ndarray,
        residuals: np.ndarray,
        img_src: np.ndarray,
        img_ref: np.ndarray,
        warped_src: np.ndarray,
        overlap_mask: np.ndarray
    ) -> LunarCorrespondenceDNAResult:
        """
        Derives an 8-dimensional mathematical vector and canonical hash
        strictly from physical registration properties.
        """
        # 1. Scale factor from Jacobian determinant
        det_H = float(np.linalg.det(H_3x3[:2, :2]))
        scale_factor = float(np.sqrt(abs(det_H))) if abs(det_H) > 1e-9 else 1.0

        # 2. Rotation angle in degrees
        rot_rad = float(np.arctan2(H_3x3[1, 0], H_3x3[0, 0]))
        rot_deg = float(np.degrees(rot_rad))

        # 3. Matrix Condition Number log10
        try:
            _, s, _ = np.linalg.svd(H_3x3)
            cond = float(s[0] / (s[-1] + 1e-12))
            cond_log = float(np.log10(max(1.0, cond)))
        except Exception:
            cond_log = 5.0

        # 4. Spatial Dispersion Entropy
        h, w = img_ref.shape[:2]
        spatial_entropy, _ = SpatialDistributionMetrics.calculate_distribution_index(
            inlier_ref_pts, img_w=w, img_h=h
        )

        # 5. Residual Moments (Mean, Variance, Skewness)
        if len(residuals) > 0:
            mean_res = float(np.mean(residuals))
            var_res = float(np.var(residuals))
            std_res = float(np.std(residuals))
            skew_res = float(np.mean(((residuals - mean_res) / (std_res + 1e-6)) ** 3))
        else:
            mean_res, var_res, skew_res = 0.0, 0.0, 0.0

        # 6. Normalized Mutual Information
        nmi = CrossModalMetrics.calculate_nmi(img_ref, warped_src, overlap_mask)

        # Build 8-D normalized DNA vector
        # [scale/5.0, (rot+180)/360, cond_log/6.0, spatial_entropy, mean_res/10.0, var_res/10.0, (skew+3)/6.0, nmi]
        dna_vector = [
            float(np.clip(scale_factor / 5.0, 0.0, 1.0)),
            float(np.clip((rot_deg + 180.0) / 360.0, 0.0, 1.0)),
            float(np.clip(cond_log / 6.0, 0.0, 1.0)),
            float(np.clip(spatial_entropy, 0.0, 1.0)),
            float(np.clip(mean_res / 10.0, 0.0, 1.0)),
            float(np.clip(var_res / 10.0, 0.0, 1.0)),
            float(np.clip((skew_res + 3.0) / 6.0, 0.0, 1.0)),
            float(np.clip(nmi, 0.0, 1.0))
        ]

        # Generate deterministic canonical SHA-256 fingerprint from the physical vector
        raw_repr = "|".join([f"{v:.5f}" for v in dna_vector])
        sha = hashlib.sha256(raw_repr.encode("utf-8")).hexdigest()
        canonical_hash = f"DNA-{sha[:4].upper()}-{sha[4:8].upper()}-{sha[8:12].upper()}-{sha[12:16].upper()}"
        certificate_id = f"CH2-CERT-{sha[16:24].upper()}"

        return LunarCorrespondenceDNAResult(
            canonical_hash=canonical_hash,
            dna_vector=[round(x, 4) for x in dna_vector],
            scale_factor=round(scale_factor, 4),
            rotation_deg=round(rot_deg, 2),
            matrix_condition_log10=round(cond_log, 3),
            spatial_entropy=round(spatial_entropy, 4),
            mean_residual_px=round(mean_res, 3),
            residual_variance=round(var_res, 3),
            residual_skewness=round(skew_res, 3),
            mutual_information=round(nmi, 4),
            certificate_id=certificate_id
        )
