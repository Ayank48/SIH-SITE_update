"""
TEAM ZERODAY Module 3: Blind Lunar Test
Evaluates correspondence objectivity by stripping sensor metadata and evaluating
autonomous scale and orientation estimation against unmasked ground truth.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np
from cv_engine.preprocessing.scale_pyramid import ScalePyramidHarmonizer


@dataclass
class BlindTestAuditResult:
    blind_estimated_scale: float
    blind_estimated_rotation_deg: float
    blind_confidence: Optional[float]
    true_sensor_source: Optional[str]
    true_sensor_reference: Optional[str]
    true_scale_ratio: Optional[float]
    scale_error_percentage: Optional[float]
    blind_accuracy_grade: str
    audit_notes: str


class BlindLunarTestEngine:
    """Manages the blinded evaluation lifecycle to prove algorithmic objectivity."""

    @staticmethod
    def run_blind_estimation(img_src: np.ndarray, img_ref: np.ndarray) -> Dict[str, float]:
        """
        Executes purely data-driven scale and rotation estimation with zero metadata clues.
        """
        est_scale, est_rot, conf = ScalePyramidHarmonizer.estimate_global_scale_rotation_fourier(img_src, img_ref)
        return {
            "estimated_scale": round(float(est_scale), 3),
            "estimated_rotation_deg": round(float(est_rot), 2),
            "confidence": round(float(conf), 4)
        }

    @staticmethod
    def audit_and_reveal(
        estimated_scale: float,
        estimated_rot: float,
        confidence: Optional[float],
        true_src_sensor: str,
        true_ref_sensor: str,
        true_src_gsd: float,
        true_ref_gsd: float
    ) -> BlindTestAuditResult:
        """
        Unmasks ground truth metadata and grades the blind estimation.
        """
        if true_src_gsd > 0 and true_ref_gsd > 0:
            true_ratio = true_src_gsd / true_ref_gsd
            err_pct = abs(estimated_scale - true_ratio) / true_ratio * 100.0
        else:
            true_ratio = 1.0
            err_pct = 0.0

        if err_pct < 5.0:
            grade = "A+ (LOW_SCALE_ERROR)"
        elif err_pct < 15.0:
            grade = "A (LOW_SCALE_ERROR)"
        elif err_pct < 30.0:
            grade = "B (ACCEPTABLE_APPROXIMATION)"
        else:
            grade = "C (HIGH_DISPARITY_REQUIRES_GUIDANCE)"

        notes = (
            f"Blind test evaluated without sensor metadata. "
            f"Ground truth resolved: {true_src_sensor} (GSD={true_src_gsd}m) -> "
            f"{true_ref_sensor} (GSD={true_ref_gsd}m). "
            f"Observed scale error: {err_pct:.2f}%."
        )

        return BlindTestAuditResult(
            blind_estimated_scale=round(estimated_scale, 3),
            blind_estimated_rotation_deg=round(estimated_rot, 2),
            blind_confidence=round(float(confidence), 4) if confidence is not None else None,
            true_sensor_source=true_src_sensor,
            true_sensor_reference=true_ref_sensor,
            true_scale_ratio=round(true_ratio, 3),
            scale_error_percentage=round(err_pct, 2),
            blind_accuracy_grade=grade,
            audit_notes=notes
        )
