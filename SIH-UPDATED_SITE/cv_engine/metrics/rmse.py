"""Runtime transfer-error and registration metrics."""
from dataclasses import dataclass
from typing import Dict, Any
import numpy as np


@dataclass
class RegistrationMetrics:
    rmse_px: float
    mean_error_px: float
    median_error_px: float
    std_error_px: float
    max_error_px: float
    min_error_px: float
    inlier_count: int
    tentative_count: int
    inlier_ratio: float


class LunarMetricsCalculator:
    @staticmethod
    def calculate_transfer_metrics(
        transfer_errors: np.ndarray,
        inlier_mask: np.ndarray
    ) -> RegistrationMetrics:
        """
        Calculates authentic root mean square error (RMSE) and residual distribution
        over verified inlier correspondences.
        """
        n_total = len(transfer_errors)
        if n_total == 0:
            return RegistrationMetrics(
                rmse_px=0.0,
                mean_error_px=0.0,
                median_error_px=0.0,
                std_error_px=0.0,
                max_error_px=0.0,
                min_error_px=0.0,
                inlier_count=0,
                tentative_count=0,
                inlier_ratio=0.0
            )

        inlier_errors = transfer_errors[inlier_mask]
        n_inliers = len(inlier_errors)

        if n_inliers == 0:
            return RegistrationMetrics(
                rmse_px=float(np.sqrt(np.mean(transfer_errors ** 2))),
                mean_error_px=float(np.mean(transfer_errors)),
                median_error_px=float(np.median(transfer_errors)),
                std_error_px=float(np.std(transfer_errors)),
                max_error_px=float(np.max(transfer_errors)),
                min_error_px=float(np.min(transfer_errors)),
                inlier_count=0,
                tentative_count=n_total,
                inlier_ratio=0.0
            )

        rmse = float(np.sqrt(np.mean(inlier_errors ** 2)))
        mean_err = float(np.mean(inlier_errors))
        median_err = float(np.median(inlier_errors))
        std_err = float(np.std(inlier_errors))
        max_err = float(np.max(inlier_errors))
        min_err = float(np.min(inlier_errors))
        inlier_ratio = float(n_inliers / n_total)

        return RegistrationMetrics(
            rmse_px=rmse,
            mean_error_px=mean_err,
            median_error_px=median_err,
            std_error_px=std_err,
            max_error_px=max_err,
            min_error_px=min_err,
            inlier_count=n_inliers,
            tentative_count=n_total,
            inlier_ratio=inlier_ratio
        )
