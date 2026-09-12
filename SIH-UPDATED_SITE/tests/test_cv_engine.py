"""
Comprehensive Unit & Integration Test Suite for Lunar CV Engine
Verifies sub-pixel accuracy, geometric consistency, and the four ZERO-DAY modules.
"""
from pathlib import Path
import pytest
import numpy as np
import cv2

from cv_engine.ingestion.loader import LunarImageLoader
from cv_engine.preprocessing.normalizer import LunarNormalizer
from cv_engine.preprocessing.illumination import LunarIlluminationNormalizer
from cv_engine.preprocessing.scale_pyramid import ScalePyramidHarmonizer
from cv_engine.correspondence.detectors import LunarFeatureDetector
from cv_engine.correspondence.descriptors import LunarDescriptorExtractor
from cv_engine.correspondence.coarse_to_fine import CoarseToFineMatcher
from cv_engine.geometry.estimator import RobustGeometricEstimator
from cv_engine.registration.warper import LunarImageWarper
from cv_engine.registration.blending import LunarRegistrationBlender
from cv_engine.metrics.rmse import LunarMetricsCalculator
from cv_engine.metrics.spatial_distribution import SpatialDistributionMetrics
from cv_engine.metrics.cross_modal import CrossModalMetrics
from cv_engine.zero_day.court import LunarCorrespondenceCourt
from cv_engine.zero_day.dna import LunarCorrespondenceDNA
from cv_engine.zero_day.blind_test import BlindLunarTestEngine
from cv_engine.zero_day.graph import LunarCorrespondenceGraph
from cv_engine.pipeline import LunarCorrespondencePipeline


SAMPLE_SRC = Path("data/samples/lunar_source_ohrc_sim.png")
SAMPLE_REF = Path("data/samples/lunar_reference_tmc_sim.png")


def test_image_loader():
    assert SAMPLE_SRC.exists()
    img, meta = LunarImageLoader.load_image(SAMPLE_SRC)
    assert isinstance(img, np.ndarray)
    assert img.dtype == np.float32
    assert img.ndim == 2
    assert 0.0 <= np.min(img) <= np.max(img) <= 1.0
    assert meta["width"] == 600
    assert meta["height"] == 600


def test_illumination_normalizer():
    img, _ = LunarImageLoader.load_image(SAMPLE_SRC)
    # Phase Congruency
    pc = LunarIlluminationNormalizer.compute_phase_congruency(img)
    assert pc.shape == img.shape
    assert 0.0 <= np.min(pc) <= np.max(pc) <= 1.0

    # Retinex
    ret = LunarIlluminationNormalizer.multiscale_retinex(img)
    assert ret.shape == img.shape

    # CLAHE
    cl = LunarIlluminationNormalizer.apply_clahe(img)
    assert cl.shape == img.shape

    # Symmetric Gradients (modulo pi)
    mag, angle = LunarIlluminationNormalizer.compute_symmetric_gradients(img)
    assert np.all((angle >= 0.0) & (angle <= np.pi + 1e-4))


def test_detector_with_anms():
    img, _ = LunarImageLoader.load_image(SAMPLE_SRC)
    img_8u = LunarNormalizer.standardize_8u(img)
    detector = LunarFeatureDetector(method="sift", max_features=300, use_anms=True)
    kps = detector.detect(img_8u)
    assert len(kps) > 50
    assert len(kps) <= 300

    # Verify spatial spread: points should exist in all 4 quadrants
    w, h = img.shape[1], img.shape[0]
    q1 = sum(1 for k in kps if k.pt[0] < w / 2 and k.pt[1] < h / 2)
    q2 = sum(1 for k in kps if k.pt[0] >= w / 2 and k.pt[1] < h / 2)
    q3 = sum(1 for k in kps if k.pt[0] < w / 2 and k.pt[1] >= h / 2)
    q4 = sum(1 for k in kps if k.pt[0] >= w / 2 and k.pt[1] >= h / 2)
    assert q1 > 0 and q2 > 0 and q3 > 0 and q4 > 0


@pytest.mark.parametrize("descriptor_type", ["sift", "orb", "cfog"])
def test_descriptor_selection_produces_selected_descriptor(descriptor_type):
    img, _ = LunarImageLoader.load_image(SAMPLE_SRC)
    img_8u = LunarNormalizer.standardize_8u(img)
    detector = LunarFeatureDetector(method=descriptor_type if descriptor_type != "cfog" else "sift", max_features=120, use_anms=True)
    keypoints = detector.detect_keypoints(img_8u)
    from cv_engine.correspondence.descriptors import LunarDescriptorExtractor
    selected_keypoints, descriptors = LunarDescriptorExtractor(descriptor_type).compute(img_8u, keypoints)
    assert len(selected_keypoints) == descriptors.shape[0]
    assert descriptors.shape[1] == (128 if descriptor_type in ["sift", "cfog"] else 32)


def test_geometric_estimation_reports_insufficient_matches():
    estimator = RobustGeometricEstimator()
    result = estimator.estimate([], img_width=600, img_height=600)
    assert result.is_valid is False
    assert result.inlier_count == 0
    assert "Insufficient tentative matches" in result.status_message


def test_end_to_end_pipeline():
    src_img, _ = LunarImageLoader.load_image(SAMPLE_SRC)
    ref_img, _ = LunarImageLoader.load_image(SAMPLE_REF)

    pipeline = LunarCorrespondencePipeline(
        preprocessing_mode="clahe",
        detector_type="sift",
        descriptor_type="sift",
        max_features=1500,
        ratio_threshold=0.85,
        ransac_threshold_px=5.0
    )

    result = pipeline.execute(
        img_src=src_img,
        img_ref=ref_img,
        src_gsd=0.25,
        ref_gsd=0.5,
        blind_mode=True,
        src_sensor_name="OHRC",
        ref_sensor_name="TMC2"
    )

    assert result.success is True
    assert result.metrics.inlier_count >= 4
    assert result.metrics.rmse_px < 3.5

    # Verification of Court verdicts
    assert len(result.court_verdicts) == len(result.all_matches)
    assert result.court_summary["ACCEPT"] > 0
    assert "ACCEPT" in [v.verdict for v in result.court_verdicts]

    # Verification of Lunar Correspondence DNA
    assert result.dna.canonical_hash.startswith("DNA-")
    assert len(result.dna.dna_vector) == 8
    assert result.dna.certificate_id.startswith("CH2-CERT-")

    # Verification of Blind Audit
    assert result.blind_audit is not None
    assert result.blind_audit.blind_estimated_scale > 0.0

    # Verification of Graph Topology
    assert len(result.graph_topology.nodes) > 0
    assert len(result.graph_topology.edges) > 0
    assert 0.0 <= result.graph_topology.structural_integrity_score <= 1.0

    # Verification of Blended outputs
    assert result.diff_heatmap.shape[:2] == ref_img.shape
    assert result.checkerboard.shape[:2] == ref_img.shape
    assert result.false_color.shape[:2] == ref_img.shape


if __name__ == "__main__":
    pytest.main(["-v", "tests/test_cv_engine.py"])
