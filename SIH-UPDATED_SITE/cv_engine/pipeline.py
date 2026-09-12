"""
Unified End-to-End Lunar Correspondence Pipeline
Orchestrates preprocessing, matching, MAGSAC++ estimation, warping, and ZERO-DAY verification.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import cv2

from cv_engine.preprocessing.normalizer import LunarNormalizer
from cv_engine.preprocessing.illumination import LunarIlluminationNormalizer
from cv_engine.preprocessing.scale_pyramid import ScalePyramidHarmonizer
from cv_engine.correspondence.detectors import LunarFeatureDetector
from cv_engine.correspondence.descriptors import LunarDescriptorExtractor
from cv_engine.correspondence.coarse_to_fine import CoarseToFineMatcher, CandidateCorrespondence
from cv_engine.geometry.estimator import RobustGeometricEstimator, EstimationResult
from cv_engine.registration.warper import LunarImageWarper
from cv_engine.registration.blending import LunarRegistrationBlender
from cv_engine.metrics.rmse import LunarMetricsCalculator, RegistrationMetrics
from cv_engine.metrics.spatial_distribution import SpatialDistributionMetrics
from cv_engine.metrics.cross_modal import CrossModalMetrics
from cv_engine.zero_day.court import LunarCorrespondenceCourt, MatchVerdict
from cv_engine.zero_day.dna import LunarCorrespondenceDNA, LunarCorrespondenceDNAResult
from cv_engine.zero_day.blind_test import BlindLunarTestEngine, BlindTestAuditResult
from cv_engine.zero_day.graph import LunarCorrespondenceGraph, LunarGraphRepresentation


@dataclass
class PipelineExecutionResult:
    # Status
    success: bool
    status_message: str

    # Images
    preprocessed_src: np.ndarray
    preprocessed_ref: np.ndarray
    warped_src: np.ndarray
    overlap_mask: np.ndarray
    diff_heatmap: np.ndarray
    checkerboard: np.ndarray
    false_color: np.ndarray

    # Matching & Geometry
    all_matches: List[CandidateCorrespondence]
    inlier_mask: np.ndarray
    transformation_matrix: np.ndarray
    model_type: str
    condition_number: float

    # Authentic Metrics
    metrics: RegistrationMetrics
    spatial_entropy: float
    grid_coverage: float
    nmi: float
    ssim: float

    # ZERO-DAY Modules
    court_verdicts: List[MatchVerdict]
    court_summary: Dict[str, int]
    dna: LunarCorrespondenceDNAResult
    blind_audit: Optional[BlindTestAuditResult]
    graph_topology: LunarGraphRepresentation


class LunarCorrespondencePipeline:
    """The complete scientific pipeline for SIH26166."""

    def __init__(
        self,
        preprocessing_mode: str = "clahe",  # "clahe", "phase_congruency", "retinex"
        detector_type: str = "sift",        # "sift", "orb", "akaze"
        descriptor_type: str = "sift",      # "sift", "cfog"
        max_features: int = 1500,
        ratio_threshold: float = 0.80,
        ransac_threshold_px: float = 5.0,
        preferred_model: str = "auto"
    ):
        self.preprocessing_mode = preprocessing_mode.lower()
        self.detector_type = detector_type
        self.descriptor_type = descriptor_type
        self.max_features = max_features
        self.ratio_threshold = ratio_threshold
        self.ransac_thresh = ransac_threshold_px
        self.preferred_model = preferred_model

    def execute(
        self,
        img_src: np.ndarray,
        img_ref: np.ndarray,
        src_gsd: float = 1.0,
        ref_gsd: float = 1.0,
        blind_mode: bool = False,
        src_sensor_name: str = "OHRC",
        ref_sensor_name: str = "TMC2"
    ) -> PipelineExecutionResult:
        """
        Executes end-to-end correspondence and registration pipeline on float32 [0, 1] images.
        """
        # 1. Normalization & Preprocessing
        norm_src = LunarNormalizer.percentile_stretch(img_src)
        norm_ref = LunarNormalizer.percentile_stretch(img_ref)

        if self.preprocessing_mode == "phase_congruency":
            prep_src = LunarIlluminationNormalizer.compute_phase_congruency(norm_src)
            prep_ref = LunarIlluminationNormalizer.compute_phase_congruency(norm_ref)
        elif self.preprocessing_mode == "retinex":
            prep_src = LunarIlluminationNormalizer.multiscale_retinex(norm_src)
            prep_ref = LunarIlluminationNormalizer.multiscale_retinex(norm_ref)
        else:
            prep_src = LunarIlluminationNormalizer.apply_clahe(norm_src)
            prep_ref = LunarIlluminationNormalizer.apply_clahe(norm_ref)

        # 2. Scale Harmonization
        scale_applied = 1.0
        if not blind_mode and src_gsd > 0 and ref_gsd > 0 and not np.isclose(src_gsd, ref_gsd, atol=0.05):
            harm_src, harm_ref, scale_applied = ScalePyramidHarmonizer.harmonize_by_gsd(
                prep_src, prep_ref, src_gsd, ref_gsd
            )
        else:
            harm_src, harm_ref = prep_src, prep_ref

        # 3. Keypoint detection and explicitly selected descriptor extraction
        if self.descriptor_type in {"orb", "akaze"} and self.detector_type != self.descriptor_type:
            raise ValueError(
                f"{self.descriptor_type.upper()} descriptors require the matching "
                f"{self.descriptor_type.upper()} detector in this pipeline"
            )
        detector = LunarFeatureDetector(
            method=self.detector_type,
            max_features=self.max_features,
            use_anms=True
        )
        src_8u = LunarNormalizer.standardize_8u(harm_src)
        ref_8u = LunarNormalizer.standardize_8u(harm_ref)

        if self.detector_type == self.descriptor_type and self.descriptor_type in {"sift", "orb", "akaze"}:
            kps_src, desc_src = detector.detect_and_compute(src_8u)
            kps_ref, desc_ref = detector.detect_and_compute(ref_8u)
        else:
            kps_src = detector.detect_keypoints(src_8u)
            kps_ref = detector.detect_keypoints(ref_8u)
            descriptor = LunarDescriptorExtractor(method=self.descriptor_type)
            kps_src, desc_src = descriptor.compute(src_8u, kps_src)
            kps_ref, desc_ref = descriptor.compute(ref_8u, kps_ref)

        # 4. Bidirectional Lowe-ratio matching
        matcher = CoarseToFineMatcher(ratio_threshold=self.ratio_threshold, cross_check=True)
        raw_matches = matcher.match(kps_src, desc_src, kps_ref, desc_ref)

        # If scale was harmonized, remap source correspondence coordinates back to original native frame
        matches: List[CandidateCorrespondence] = []
        inv_scale = (1.0 / scale_applied) if scale_applied != 1.0 else 1.0
        for m in raw_matches:
            native_src_pt = (m.src_pt[0] * inv_scale, m.src_pt[1] * inv_scale)
            matches.append(CandidateCorrespondence(
                source_idx=m.source_idx,
                ref_idx=m.ref_idx,
                src_pt=native_src_pt,
                ref_pt=m.ref_pt,
                descriptor_distance=m.descriptor_distance,
                ratio=m.ratio
            ))

        # 5. Robust USAC-MAGSAC++ Geometric Estimation
        h_ref, w_ref = img_ref.shape[:2]
        estimator = RobustGeometricEstimator(
            ransac_reproj_threshold=self.ransac_thresh,
            preferred_model=self.preferred_model
        )
        est_res = estimator.estimate(matches, img_width=w_ref, img_height=h_ref)

        # 6. Image Warping & Registered Products
        if est_res.is_valid:
            warped_src, overlap_mask = LunarImageWarper.warp_source_to_reference(
                norm_src, (h_ref, w_ref), est_res.matrix_3x3
            )
            diff_heatmap = LunarRegistrationBlender.create_difference_map(norm_ref, warped_src, overlap_mask)
            checkerboard = LunarRegistrationBlender.create_checkerboard(norm_ref, warped_src)
            false_color = LunarRegistrationBlender.create_false_color_composite(norm_ref, warped_src, overlap_mask)
        else:
            warped_src = np.zeros_like(norm_ref)
            overlap_mask = np.zeros_like(norm_ref, dtype=bool)
            diff_heatmap = np.zeros((h_ref, w_ref, 3), dtype=np.uint8)
            checkerboard = np.zeros((h_ref, w_ref), dtype=np.uint8)
            false_color = np.zeros((h_ref, w_ref, 3), dtype=np.uint8)

        # 7. Authentic Metrics Computation
        metrics = LunarMetricsCalculator.calculate_transfer_metrics(
            est_res.transfer_errors, est_res.inlier_mask
        )

        inlier_ref_pts = np.array([m.ref_pt for i, m in enumerate(matches) if est_res.inlier_mask[i]]) if est_res.inlier_count > 0 else np.empty((0, 2))
        inlier_src_pts = np.array([m.src_pt for i, m in enumerate(matches) if est_res.inlier_mask[i]]) if est_res.inlier_count > 0 else np.empty((0, 2))

        spatial_entropy, grid_cov = SpatialDistributionMetrics.calculate_distribution_index(
            inlier_ref_pts, img_w=w_ref, img_h=h_ref
        )
        nmi = CrossModalMetrics.calculate_nmi(norm_ref, warped_src, overlap_mask)
        ssim_val = CrossModalMetrics.calculate_ssim(norm_ref, warped_src, overlap_mask)

        # 8. ZERO-DAY Module 1: Lunar Correspondence Court
        court = LunarCorrespondenceCourt(max_residual_tol_px=self.ransac_thresh)
        court_verdicts = court.adjudicate(
            matches, norm_src, norm_ref, est_res.matrix_3x3, est_res.inlier_mask
        )
        court_summary = {
            "ACCEPT": sum(1 for v in court_verdicts if v.verdict == "ACCEPT"),
            "UNCERTAIN": sum(1 for v in court_verdicts if v.verdict == "UNCERTAIN"),
            "REJECT": sum(1 for v in court_verdicts if v.verdict == "REJECT")
        }

        # 9. ZERO-DAY Module 2: Lunar Correspondence DNA
        dna = LunarCorrespondenceDNA.generate_dna(
            est_res.matrix_3x3,
            inlier_src_pts,
            inlier_ref_pts,
            est_res.transfer_errors[est_res.inlier_mask] if est_res.inlier_count > 0 else np.empty(0),
            norm_src,
            norm_ref,
            warped_src,
            overlap_mask
        )

        # 10. ZERO-DAY Module 3: Blind Lunar Test Audit
        blind_audit = None
        if blind_mode:
            blind_est = BlindLunarTestEngine.run_blind_estimation(norm_src, norm_ref)
            blind_audit = BlindLunarTestEngine.audit_and_reveal(
                estimated_scale=blind_est["estimated_scale"],
                estimated_rot=blind_est["estimated_rotation_deg"],
                confidence=blind_est["confidence"],
                true_src_sensor=src_sensor_name,
                true_ref_sensor=ref_sensor_name,
                true_src_gsd=src_gsd,
                true_ref_gsd=ref_gsd
            )

        # 11. ZERO-DAY Module 4: Lunar Correspondence Graph
        inlier_match_ids = np.array(
            [i for i, is_inlier in enumerate(est_res.inlier_mask) if is_inlier],
            dtype=np.int32,
        )
        graph_topo = LunarCorrespondenceGraph.build_graph(
            inlier_src_pts,
            inlier_ref_pts,
            match_ids=inlier_match_ids,
        )

        return PipelineExecutionResult(
            success=est_res.is_valid,
            status_message=est_res.status_message,
            preprocessed_src=prep_src,
            preprocessed_ref=prep_ref,
            warped_src=warped_src,
            overlap_mask=overlap_mask,
            diff_heatmap=diff_heatmap,
            checkerboard=checkerboard,
            false_color=false_color,
            all_matches=matches,
            inlier_mask=est_res.inlier_mask,
            transformation_matrix=est_res.matrix_3x3,
            model_type=est_res.model_type,
            condition_number=est_res.condition_number,
            metrics=metrics,
            spatial_entropy=spatial_entropy,
            grid_coverage=grid_cov,
            nmi=nmi,
            ssim=ssim_val,
            court_verdicts=court_verdicts,
            court_summary=court_summary,
            dna=dna,
            blind_audit=blind_audit,
            graph_topology=graph_topo
        )
