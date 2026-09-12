"""
Coarse-to-Fine Hierarchical Matcher with Mutual Cross-Check and Ratio Testing
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import cv2


@dataclass
class CandidateCorrespondence:
    source_idx: int
    ref_idx: int
    src_pt: Tuple[float, float]  # (x, y)
    ref_pt: Tuple[float, float]  # (x, y)
    descriptor_distance: float
    ratio: float


class CoarseToFineMatcher:
    """Matches lunar features using two-way cross validation and Lowe ratio testing."""

    def __init__(self, ratio_threshold: float = 0.75, cross_check: bool = True):
        self.ratio_threshold = ratio_threshold
        self.cross_check = cross_check

    def match(
        self,
        kps_src: List[cv2.KeyPoint],
        desc_src: np.ndarray,
        kps_ref: List[cv2.KeyPoint],
        desc_ref: np.ndarray
    ) -> List[CandidateCorrespondence]:
        """
        Executes bidirectional ratio-tested matching between source and reference.
        """
        if len(kps_src) == 0 or len(kps_ref) == 0 or desc_src.shape[0] == 0 or desc_ref.shape[0] == 0:
            return []

        # FLANN or BFMatcher depending on descriptor dimension
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        # Forward match (Source -> Ref): k=2 for ratio test
        matches_fwd = bf.knnMatch(desc_src, desc_ref, k=2)
        good_fwd = {}
        for m in matches_fwd:
            if len(m) == 2 and m[0].distance < self.ratio_threshold * m[1].distance:
                ratio = m[0].distance / (m[1].distance + 1e-7)
                good_fwd[m[0].queryIdx] = (m[0].trainIdx, m[0].distance, ratio)

        if not self.cross_check:
            # Single direction
            results = []
            for src_idx, (ref_idx, dist, ratio) in good_fwd.items():
                results.append(CandidateCorrespondence(
                    source_idx=src_idx,
                    ref_idx=ref_idx,
                    src_pt=kps_src[src_idx].pt,
                    ref_pt=kps_ref[ref_idx].pt,
                    descriptor_distance=float(dist),
                    ratio=float(ratio)
                ))
            return results

        # Backward match (Ref -> Source) for mutual consistency check
        matches_bwd = bf.knnMatch(desc_ref, desc_src, k=2)
        good_bwd = {}
        for m in matches_bwd:
            if len(m) == 2 and m[0].distance < self.ratio_threshold * m[1].distance:
                good_bwd[m[0].queryIdx] = m[0].trainIdx

        # Cross-validation intersection: i -> j and j -> i
        verified_matches = []
        for src_idx, (ref_idx, dist, ratio) in good_fwd.items():
            if ref_idx in good_bwd and good_bwd[ref_idx] == src_idx:
                verified_matches.append(CandidateCorrespondence(
                    source_idx=src_idx,
                    ref_idx=ref_idx,
                    src_pt=kps_src[src_idx].pt,
                    ref_pt=kps_ref[ref_idx].pt,
                    descriptor_distance=float(dist),
                    ratio=float(ratio)
                ))

        return verified_matches
