"""
Pipeline Execution Router: Runs Correspondence, Registration, and ZERO-DAY Modules
"""
from pathlib import Path
from typing import List
import numpy as np
from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    PipelineExecuteRequest,
    PipelineResponse,
    MatchPointSchema,
    MetricsSummarySchema,
    LunarCourtVerdictSchema,
    LunarDNASchema,
    BlindAuditSchema,
    BlindRevealRequest,
    GraphNodeSchema,
    GraphEdgeSchema,
    GraphTopologySchema
)
from backend.core.session_manager import SessionManager
from cv_engine.ingestion.loader import LunarImageLoader
from cv_engine.pipeline import LunarCorrespondencePipeline

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


@router.post("/reveal-blind", response_model=BlindAuditSchema)
async def reveal_blind(req: BlindRevealRequest):
    state = SessionManager.get_state(req.session_id)
    reveal = state.get("blind_audit_reveal")
    if not reveal:
        raise HTTPException(status_code=404, detail="No completed blind evaluation is available for this session")
    return BlindAuditSchema(**reveal)


@router.post("/run", response_model=PipelineResponse, response_model_exclude_none=True)
async def run_pipeline(req: PipelineExecuteRequest):
    state = SessionManager.get_state(req.session_id)
    if not state.get("source_uploaded") or not state.get("reference_uploaded"):
        raise HTTPException(
            status_code=400,
            detail="Both Source and Reference images must be uploaded before running correspondence."
        )

    src_path = Path(state["source_path"])
    ref_path = Path(state["reference_path"])

    if not src_path.exists() or not ref_path.exists():
        raise HTTPException(status_code=404, detail="Image files not found in session storage.")

    # Load images
    src_img, _ = LunarImageLoader.load_image(src_path)
    ref_img, _ = LunarImageLoader.load_image(ref_path)

    pipeline = LunarCorrespondencePipeline(
        preprocessing_mode=req.preprocessing_mode,
        detector_type=req.detector_type,
        descriptor_type=req.descriptor_type,
        max_features=req.max_features,
        ratio_threshold=req.ratio_threshold,
        ransac_threshold_px=req.ransac_threshold_px,
        preferred_model=req.preferred_model
    )

    try:
        result = pipeline.execute(
            img_src=src_img,
            img_ref=ref_img,
            src_gsd=req.source_gsd,
            ref_gsd=req.reference_gsd,
            blind_mode=req.blind_mode,
            src_sensor_name=req.source_sensor,
            ref_sensor_name=req.reference_sensor
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"CV Engine processing error: {exc}")

    if not result.success:
        raise HTTPException(status_code=422, detail=result.status_message)

    # Build match points schema
    match_schemas: List[MatchPointSchema] = []
    verdict_schemas: List[LunarCourtVerdictSchema] = []

    for i, m in enumerate(result.all_matches):
        is_inlier = bool(result.inlier_mask[i]) if i < len(result.inlier_mask) else False
        v = result.court_verdicts[i] if i < len(result.court_verdicts) else None

        match_schemas.append(MatchPointSchema(
            id=i,
            src_x=round(float(m.src_pt[0]), 2),
            src_y=round(float(m.src_pt[1]), 2),
            ref_x=round(float(m.ref_pt[0]), 2),
            ref_y=round(float(m.ref_pt[1]), 2),
            distance=round(float(m.descriptor_distance), 2),
            ratio=round(float(m.ratio), 3),
            is_inlier=is_inlier,
            verdict=v.verdict if v else "UNCERTAIN",
            confidence=v.confidence_score if v else 0.5
        ))

        if v:
            verdict_schemas.append(LunarCourtVerdictSchema(
                match_id=v.match_id,
                src_pt=v.src_pt,
                ref_pt=v.ref_pt,
                verdict=v.verdict,
                confidence_score=v.confidence_score,
                evidence_photometric=v.evidence_photometric,
                evidence_local_geometry=v.evidence_local_geometry,
                evidence_context_ratio=v.evidence_context_ratio,
                evidence_global_residual=v.evidence_global_residual,
                transfer_residual_px=v.transfer_residual_px,
                decision_rationale=v.decision_rationale
            ))

    # Graph schema
    graph_nodes = [
        GraphNodeSchema(id=n.id, match_id=n.match_id, src_x=n.src_x, src_y=n.src_y, ref_x=n.ref_x, ref_y=n.ref_y)
        for n in result.graph_topology.nodes
    ]
    graph_edges = [
        GraphEdgeSchema(
            source_node=e.source_node,
            target_node=e.target_node,
            src_length_px=e.src_length_px,
            ref_length_px=e.ref_length_px,
            length_ratio=e.length_ratio,
            strain_index=e.strain_index,
            is_topologically_sound=e.is_topologically_sound
        )
        for e in result.graph_topology.edges
    ]

    # Blind audit schema
    blind_audit_schema = None
    if result.blind_audit:
        blind_audit_schema = BlindAuditSchema(
            blind_estimated_scale=result.blind_audit.blind_estimated_scale,
            blind_estimated_rotation_deg=result.blind_audit.blind_estimated_rotation_deg,
            blind_confidence=result.blind_audit.blind_confidence,
            true_sensor_source=result.blind_audit.true_sensor_source,
            true_sensor_reference=result.blind_audit.true_sensor_reference,
            true_scale_ratio=result.blind_audit.true_scale_ratio,
            scale_error_percentage=result.blind_audit.scale_error_percentage,
            blind_accuracy_grade=result.blind_audit.blind_accuracy_grade,
            audit_notes=result.blind_audit.audit_notes
        )

    # Encode images to base64
    src_preview = SessionManager.array_to_base64_jpeg(src_img)
    ref_preview = SessionManager.array_to_base64_jpeg(ref_img)
    prep_src_b64 = SessionManager.array_to_base64_jpeg(result.preprocessed_src)
    prep_ref_b64 = SessionManager.array_to_base64_jpeg(result.preprocessed_ref)
    warped_b64 = SessionManager.array_to_base64_jpeg(result.warped_src)
    diff_b64 = SessionManager.array_to_base64_jpeg(result.diff_heatmap)
    checker_b64 = SessionManager.array_to_base64_jpeg(result.checkerboard)
    false_col_b64 = SessionManager.array_to_base64_jpeg(result.false_color)

    # Save registered image to session disk
    SessionManager.save_image_array(req.session_id, "registered_warped.png", result.warped_src)

    # Update state
    SessionManager.update_state(req.session_id, {
        "pipeline_executed": True,
        "model_type": result.model_type,
        "inlier_count": result.metrics.inlier_count,
        "rmse_px": result.metrics.rmse_px,
        "dna_hash": result.dna.canonical_hash
    })

    if result.blind_audit:
        SessionManager.update_state(req.session_id, {
            "blind_audit_reveal": {
                "blind_estimated_scale": result.blind_audit.blind_estimated_scale,
                "blind_estimated_rotation_deg": result.blind_audit.blind_estimated_rotation_deg,
                "blind_confidence": result.blind_audit.blind_confidence,
                "true_sensor_source": result.blind_audit.true_sensor_source,
                "true_sensor_reference": result.blind_audit.true_sensor_reference,
                "true_scale_ratio": result.blind_audit.true_scale_ratio,
                "scale_error_percentage": result.blind_audit.scale_error_percentage,
                "blind_accuracy_grade": result.blind_audit.blind_accuracy_grade,
                "audit_notes": result.blind_audit.audit_notes,
            }
        })

    response_blind_audit = None
    if result.blind_audit:
        response_blind_audit = BlindAuditSchema(
            blind_estimated_scale=result.blind_audit.blind_estimated_scale,
            blind_estimated_rotation_deg=result.blind_audit.blind_estimated_rotation_deg,
            blind_confidence=result.blind_audit.blind_confidence,
            blind_accuracy_grade="Metadata hidden until reveal",
            audit_notes="Blind estimation completed. Sensor metadata and revealed comparison remain hidden until requested.",
        )

    return PipelineResponse(
        session_id=req.session_id,
        success=result.success,
        status_message=result.status_message,
        model_type=result.model_type,
        transformation_matrix=[[round(float(val), 6) for val in row] for row in result.transformation_matrix],
        condition_number=round(result.condition_number, 2),
        source_preview=src_preview,
        reference_preview=ref_preview,
        preprocessed_source=prep_src_b64,
        preprocessed_reference=prep_ref_b64,
        warped_source=warped_b64,
        diff_heatmap=diff_b64,
        checkerboard=checker_b64,
        false_color=false_col_b64,
        matches=match_schemas,
        metrics=MetricsSummarySchema(
            rmse_px=round(result.metrics.rmse_px, 3),
            mean_error_px=round(result.metrics.mean_error_px, 3),
            median_error_px=round(result.metrics.median_error_px, 3),
            std_error_px=round(result.metrics.std_error_px, 3),
            max_error_px=round(result.metrics.max_error_px, 3),
            min_error_px=round(result.metrics.min_error_px, 3),
            inlier_count=result.metrics.inlier_count,
            tentative_count=result.metrics.tentative_count,
            inlier_ratio=round(result.metrics.inlier_ratio, 4),
            spatial_entropy=round(result.spatial_entropy, 4),
            grid_coverage=round(result.grid_coverage, 4),
            nmi=round(result.nmi, 4),
            ssim=round(result.ssim, 4)
        ),
        court_verdicts=verdict_schemas,
        court_summary=result.court_summary,
        dna=LunarDNASchema(
            canonical_hash=result.dna.canonical_hash,
            dna_vector=result.dna.dna_vector,
            scale_factor=result.dna.scale_factor,
            rotation_deg=result.dna.rotation_deg,
            matrix_condition_log10=result.dna.matrix_condition_log10,
            spatial_entropy=result.dna.spatial_entropy,
            mean_residual_px=result.dna.mean_residual_px,
            residual_variance=result.dna.residual_variance,
            residual_skewness=result.dna.residual_skewness,
            mutual_information=result.dna.mutual_information,
            certificate_id=result.dna.certificate_id
        ),
        blind_audit=response_blind_audit,
        graph_topology=GraphTopologySchema(
            nodes=graph_nodes,
            edges=graph_edges,
            mean_strain=result.graph_topology.mean_strain,
            topological_inversion_count=result.graph_topology.topological_inversion_count,
            structural_integrity_score=result.graph_topology.structural_integrity_score
        )
    )
