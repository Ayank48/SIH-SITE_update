"""
Pydantic Schemas for Lunar Correspondence Platform API
"""
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class ImageInfo(BaseModel):
    width: int
    height: int
    channels: int
    bit_depth: int
    sensor_name: str
    nominal_gsd_m: float
    preview_base64: str


class IngestionUploadResponse(BaseModel):
    session_id: str
    role: str  # "source" or "reference"
    file_name: str
    info: ImageInfo


class SamplePairInfo(BaseModel):
    sample_id: str
    title: str
    description: str
    source_sensor: str
    ref_sensor: str
    source_gsd: float
    ref_gsd: float
    sun_angle_delta: str


class PipelineExecuteRequest(BaseModel):
    session_id: str
    preprocessing_mode: str = Field(default="clahe", description="clahe, phase_congruency, retinex")
    detector_type: str = Field(default="sift", description="sift, orb, akaze")
    descriptor_type: str = Field(default="sift", description="sift, cfog")
    max_features: int = Field(default=1500, ge=100, le=5000)
    ratio_threshold: float = Field(default=0.82, ge=0.5, le=0.98)
    ransac_threshold_px: float = Field(default=5.0, ge=1.0, le=20.0)
    preferred_model: str = Field(default="auto", description="auto, homography, affine")
    blind_mode: bool = Field(default=False)
    source_sensor: str = "OHRC"
    reference_sensor: str = "TMC2"
    source_gsd: float = 0.25
    reference_gsd: float = 5.0


class MatchPointSchema(BaseModel):
    id: int
    src_x: float
    src_y: float
    ref_x: float
    ref_y: float
    distance: float
    ratio: float
    is_inlier: bool
    verdict: str  # ACCEPT, UNCERTAIN, REJECT
    confidence: float


class MetricsSummarySchema(BaseModel):
    rmse_px: float
    mean_error_px: float
    median_error_px: float
    std_error_px: float
    max_error_px: float
    min_error_px: float
    inlier_count: int
    tentative_count: int
    inlier_ratio: float
    spatial_entropy: float
    grid_coverage: float
    nmi: float
    ssim: float


class LunarCourtVerdictSchema(BaseModel):
    match_id: int
    src_pt: Tuple[float, float]
    ref_pt: Tuple[float, float]
    verdict: str
    confidence_score: float
    evidence_photometric: float
    evidence_local_geometry: float
    evidence_context_ratio: float
    evidence_global_residual: float
    transfer_residual_px: float
    decision_rationale: str


class LunarDNASchema(BaseModel):
    canonical_hash: str
    dna_vector: List[float]
    scale_factor: float
    rotation_deg: float
    matrix_condition_log10: float
    spatial_entropy: float
    mean_residual_px: float
    residual_variance: float
    residual_skewness: float
    mutual_information: float
    certificate_id: str


class BlindAuditSchema(BaseModel):
    blind_estimated_scale: float
    blind_estimated_rotation_deg: float
    blind_confidence: Optional[float] = None
    true_sensor_source: Optional[str] = None
    true_sensor_reference: Optional[str] = None
    true_scale_ratio: Optional[float] = None
    scale_error_percentage: Optional[float] = None
    blind_accuracy_grade: str
    audit_notes: str


class BlindRevealRequest(BaseModel):
    session_id: str


class GraphNodeSchema(BaseModel):
    id: int
    match_id: int
    src_x: float
    src_y: float
    ref_x: float
    ref_y: float


class GraphEdgeSchema(BaseModel):
    source_node: int
    target_node: int
    src_length_px: float
    ref_length_px: float
    length_ratio: float
    strain_index: float
    is_topologically_sound: bool


class GraphTopologySchema(BaseModel):
    nodes: List[GraphNodeSchema]
    edges: List[GraphEdgeSchema]
    mean_strain: float
    topological_inversion_count: int
    structural_integrity_score: float


class PipelineResponse(BaseModel):
    session_id: str
    success: bool
    status_message: str
    model_type: str
    transformation_matrix: List[List[float]]
    condition_number: float

    # Base64 Rendered Images
    source_preview: str
    reference_preview: str
    preprocessed_source: str
    preprocessed_reference: str
    warped_source: str
    diff_heatmap: str
    checkerboard: str
    false_color: str

    # Keypoint Correspondences
    matches: List[MatchPointSchema]

    # Metrics
    metrics: MetricsSummarySchema

    # ZERO-DAY Innovations
    court_verdicts: List[LunarCourtVerdictSchema]
    court_summary: Dict[str, int]
    dna: LunarDNASchema
    blind_audit: Optional[BlindAuditSchema]
    graph_topology: GraphTopologySchema

