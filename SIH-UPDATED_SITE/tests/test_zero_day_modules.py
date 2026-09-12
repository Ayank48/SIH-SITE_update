"""
Unit tests for TEAM ZERODAY Innovation Modules: Court, DNA, Blind Test, and Graph.
"""
import numpy as np
from cv_engine.zero_day.court import LunarCorrespondenceCourt
from cv_engine.zero_day.dna import LunarCorrespondenceDNA
from cv_engine.zero_day.blind_test import BlindLunarTestEngine
from cv_engine.zero_day.graph import LunarCorrespondenceGraph
from cv_engine.correspondence.coarse_to_fine import CandidateCorrespondence


def test_court_verdict_outlier_rejection():
    court = LunarCorrespondenceCourt(max_residual_tol_px=4.0)
    # Synthetic matches: 5 good inliers, 1 severe outlier
    matches = [
        CandidateCorrespondence(0, 0, (100.0, 100.0), (120.0, 110.0), 50.0, 0.5),
        CandidateCorrespondence(1, 1, (150.0, 100.0), (170.0, 110.0), 55.0, 0.55),
        CandidateCorrespondence(2, 2, (100.0, 150.0), (120.0, 160.0), 48.0, 0.48),
        CandidateCorrespondence(3, 3, (150.0, 150.0), (170.0, 160.0), 52.0, 0.52),
        CandidateCorrespondence(4, 4, (125.0, 125.0), (145.0, 135.0), 51.0, 0.51),
        # Severe outlier
        CandidateCorrespondence(5, 5, (200.0, 200.0), (50.0, 450.0), 120.0, 0.95),
    ]

    # Rigid translation: dx=20, dy=10
    H = np.array([
        [1.0, 0.0, 20.0],
        [0.0, 1.0, 10.0],
        [0.0, 0.0, 1.0]
    ])

    inlier_mask = np.array([True, True, True, True, True, False])
    img_dummy = np.full((300, 300), 0.5, dtype=np.float32)

    verdicts = court.adjudicate(matches, img_dummy, img_dummy, H, inlier_mask)
    assert len(verdicts) == 6
    assert verdicts[5].verdict == "REJECT"
    assert verdicts[0].verdict in ["ACCEPT", "UNCERTAIN"]


def test_dna_determinism():
    H = np.eye(3, dtype=np.float64)
    src_pts = np.array([[10, 10], [50, 50], [90, 90]], dtype=np.float32)
    ref_pts = np.array([[10, 10], [50, 50], [90, 90]], dtype=np.float32)
    res = np.array([0.1, 0.2, 0.15], dtype=np.float32)
    dummy = np.full((100, 100), 0.5, dtype=np.float32)
    mask = np.ones((100, 100), dtype=bool)

    dna1 = LunarCorrespondenceDNA.generate_dna(H, src_pts, ref_pts, res, dummy, dummy, dummy, mask)
    dna2 = LunarCorrespondenceDNA.generate_dna(H, src_pts, ref_pts, res, dummy, dummy, dummy, mask)

    assert dna1.canonical_hash == dna2.canonical_hash
    assert dna1.certificate_id == dna2.certificate_id
    assert len(dna1.dna_vector) == 8


def test_blind_test_audit_grading():
    audit = BlindLunarTestEngine.audit_and_reveal(
        estimated_scale=0.252,
        estimated_rot=12.1,
        confidence=0.72,
        true_src_sensor="OHRC",
        true_ref_sensor="TMC2",
        true_src_gsd=0.25,
        true_ref_gsd=1.0  # ratio = 0.25
    )
    assert audit.scale_error_percentage < 2.0
    assert "LOW_SCALE_ERROR" in audit.blind_accuracy_grade
    assert audit.blind_confidence == 0.72


def test_correspondence_graph_topology():
    # Grid of points
    src = np.array([
        [100, 100], [200, 100], [300, 100],
        [100, 200], [200, 200], [300, 200],
        [100, 300], [200, 300], [300, 300]
    ], dtype=np.float32)
    # Reference translated by 15, 15
    ref = src + 15.0

    graph = LunarCorrespondenceGraph.build_graph(src, ref)
    assert len(graph.nodes) == 9
    assert len(graph.edges) > 0
    assert graph.topological_inversion_count == 0
    assert graph.structural_integrity_score > 0.8
