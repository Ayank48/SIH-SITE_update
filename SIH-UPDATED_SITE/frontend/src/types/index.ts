export interface ImageInfo {
  width: number;
  height: number;
  channels: number;
  bit_depth: number;
  sensor_name: string;
  nominal_gsd_m: number;
  preview_base64: string;
}

export interface IngestionUploadResponse {
  session_id: string;
  role: "source" | "reference";
  file_name: string;
  info: ImageInfo;
}

export interface SamplePairInfo {
  sample_id: string;
  title: string;
  description: string;
  source_sensor: string;
  ref_sensor: string;
  source_gsd: number;
  ref_gsd: number;
  sun_angle_delta: string;
}

export interface MatchPoint {
  id: number;
  src_x: number;
  src_y: number;
  ref_x: number;
  ref_y: number;
  distance: number;
  ratio: number;
  is_inlier: boolean;
  verdict: "ACCEPT" | "UNCERTAIN" | "REJECT";
  confidence: number;
}

export interface MetricsSummary {
  rmse_px: number;
  mean_error_px: number;
  median_error_px: number;
  std_error_px: number;
  max_error_px: number;
  min_error_px: number;
  inlier_count: number;
  tentative_count: number;
  inlier_ratio: number;
  spatial_entropy: number;
  grid_coverage: number;
  nmi: number;
  ssim: number;
}

export interface LunarCourtVerdict {
  match_id: number;
  src_pt: [number, number];
  ref_pt: [number, number];
  verdict: "ACCEPT" | "UNCERTAIN" | "REJECT";
  confidence_score: number;
  evidence_photometric: number;
  evidence_local_geometry: number;
  evidence_context_ratio: number;
  evidence_global_residual: number;
  transfer_residual_px: number;
  decision_rationale: string;
}

export interface LunarDNA {
  canonical_hash: string;
  dna_vector: number[];
  scale_factor: number;
  rotation_deg: number;
  matrix_condition_log10: number;
  spatial_entropy: number;
  mean_residual_px: number;
  residual_variance: number;
  residual_skewness: number;
  mutual_information: number;
  certificate_id: string;
}

export interface BlindAudit {
  blind_estimated_scale: number;
  blind_estimated_rotation_deg: number;
  blind_confidence?: number;
  true_sensor_source?: string;
  true_sensor_reference?: string;
  true_scale_ratio?: number;
  scale_error_percentage?: number;
  blind_accuracy_grade: string;
  audit_notes: string;
}

export interface GraphNode {
  id: number;
  match_id: number;
  src_x: number;
  src_y: number;
  ref_x: number;
  ref_y: number;
}

export interface GraphEdge {
  source_node: number;
  target_node: number;
  src_length_px: number;
  ref_length_px: number;
  length_ratio: number;
  strain_index: number;
  is_topologically_sound: boolean;
}

export interface GraphTopology {
  nodes: GraphNode[];
  edges: GraphEdge[];
  mean_strain: number;
  topological_inversion_count: number;
  structural_integrity_score: number;
}

export interface PipelineResponse {
  session_id: string;
  success: boolean;
  status_message: string;
  model_type: string;
  transformation_matrix: number[][];
  condition_number: number;
  source_preview: string;
  reference_preview: string;
  preprocessed_source: string;
  preprocessed_reference: string;
  warped_source: string;
  diff_heatmap: string;
  checkerboard: string;
  false_color: string;
  matches: MatchPoint[];
  metrics: MetricsSummary;
  court_verdicts: LunarCourtVerdict[];
  court_summary: {
    ACCEPT: number;
    UNCERTAIN: number;
    REJECT: number;
  };
  dna: LunarDNA;
  blind_audit?: BlindAudit;
  graph_topology: GraphTopology;
}

