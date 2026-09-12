"""
Spatial Distribution Metrics: Grid Entropy and Coverage
Quantifies whether correspondences span the image or cluster in one spot.
"""
from typing import Tuple
import numpy as np


class SpatialDistributionMetrics:
    @staticmethod
    def calculate_distribution_index(
        points: np.ndarray,  # N x 2 coordinates
        img_w: int,
        img_h: int,
        grid_bins: int = 4
    ) -> Tuple[float, float]:
        """
        Returns: (normalized_grid_entropy, grid_coverage_ratio)
        Both metrics are normalized in [0.0, 1.0].
        """
        n = len(points)
        if n < 4:
            return 0.0, 0.0

        # 1. Grid Coverage Ratio
        # Divides the image into grid_bins x grid_bins cells
        grid = np.zeros((grid_bins, grid_bins), dtype=int)
        cell_w = img_w / grid_bins
        cell_h = img_h / grid_bins

        for pt in points:
            gx = min(grid_bins - 1, max(0, int(pt[0] // cell_w)))
            gy = min(grid_bins - 1, max(0, int(pt[1] // cell_h)))
            grid[gy, gx] += 1

        occupied_cells = np.count_nonzero(grid)
        total_cells = grid_bins * grid_bins
        coverage_ratio = float(occupied_cells / total_cells)

        # 2. Shannon entropy from fixed-grid occupancy frequencies
        counts = grid.ravel()
        probs = counts / np.sum(counts)
        probs = probs[probs > 0]
        # Shannon entropy
        entropy = -np.sum(probs * np.log(probs))
        max_entropy = np.log(total_cells)
        normalized_entropy = float(entropy / max_entropy) if max_entropy > 0 else 0.0

        return normalized_entropy, coverage_ratio
