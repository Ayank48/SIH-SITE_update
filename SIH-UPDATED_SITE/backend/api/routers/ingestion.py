"""
Image Ingestion & Benchmark Sample Loader Router
"""
import shutil
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from cv_engine.ingestion.loader import LunarImageLoader, SENSOR_REGISTRY
from backend.core.session_manager import SessionManager
from backend.core.config import SAMPLES_DIR
from backend.api.schemas import IngestionUploadResponse, ImageInfo, SamplePairInfo

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/upload", response_model=IngestionUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    role: str = Form(..., description="source or reference"),
    sensor: str = Form("OHRC", description="Sensor identifier"),
    session_id: str = Form(None)
):
    if role not in ["source", "reference"]:
        raise HTTPException(status_code=400, detail="Role must be 'source' or 'reference'")

    if not session_id:
        session_id = SessionManager.create_session()

    session_dir = SessionManager.get_session_dir(session_id)
    suffix = Path(file.filename or "upload").suffix.lower()
    dest_path = session_dir / f"{role}_{uuid.uuid4().hex}{suffix}"

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load with scientific loader
    try:
        img_f32, meta = LunarImageLoader.load_image(dest_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {exc}")

    sensor_profile = LunarImageLoader.get_sensor_profile(sensor)

    # Save standardized preview
    SessionManager.save_image_array(session_id, f"{role}_clean.png", img_f32)
    preview_b64 = SessionManager.array_to_base64_jpeg(img_f32)

    # Update session state
    SessionManager.update_state(session_id, {
        f"{role}_uploaded": True,
        f"{role}_path": str(dest_path),
        f"{role}_sensor": sensor_profile.sensor_id,
        f"{role}_gsd": sensor_profile.nominal_gsd_m,
        f"{role}_dims": [meta["width"], meta["height"]]
    })

    return IngestionUploadResponse(
        session_id=session_id,
        role=role,
        file_name=file.filename,
        info=ImageInfo(
            width=meta["width"],
            height=meta["height"],
            channels=meta["original_channels"],
            bit_depth=meta["original_bit_depth"],
            sensor_name=sensor_profile.name,
            nominal_gsd_m=sensor_profile.nominal_gsd_m,
            preview_base64=preview_b64
        )
    )


@router.get("/samples", response_model=List[SamplePairInfo])
async def list_sample_pairs():
    """Returns the available synthetic development benchmark."""
    return [
        SamplePairInfo(
            sample_id="synthetic_development_pair",
            title="Synthetic Benchmark: Development Pair",
            description="Procedurally generated crater terrain for development and regression testing; not authentic Chandrayaan-2 imagery.",
            source_sensor="OHRC",
            ref_sensor="TMC2",
            source_gsd=0.25,
            ref_gsd=5.0,
            sun_angle_delta="Synthetic 60 deg illumination shift"
        ),
    ]


@router.post("/load-sample")
async def load_sample_pair(sample_id: str = Form("synthetic_development_pair")):
    """Copies the explicitly selected synthetic development pair into a session."""
    if sample_id != "synthetic_development_pair":
        raise HTTPException(status_code=404, detail="Synthetic benchmark sample is unavailable")
    session_id = SessionManager.create_session()
    session_dir = SessionManager.get_session_dir(session_id)

    src_sample = SAMPLES_DIR / "lunar_source_ohrc_sim.png"
    ref_sample = SAMPLES_DIR / "lunar_reference_tmc_sim.png"

    if not src_sample.exists() or not ref_sample.exists():
        from data.generator import LunarLandscapeSynthesizer
        LunarLandscapeSynthesizer.create_lunar_test_pair(SAMPLES_DIR)

    dest_src = session_dir / "source_sample.png"
    dest_ref = session_dir / "reference_sample.png"

    shutil.copy(src_sample, dest_src)
    shutil.copy(ref_sample, dest_ref)

    src_img, meta_s = LunarImageLoader.load_image(dest_src)
    ref_img, meta_r = LunarImageLoader.load_image(dest_ref)

    SessionManager.update_state(session_id, {
        "source_uploaded": True,
        "reference_uploaded": True,
        "source_path": str(dest_src),
        "reference_path": str(dest_ref),
        "source_sensor": "OHRC",
        "reference_sensor": "TMC2",
        "source_gsd": 0.25,
        "reference_gsd": 5.0
    })

    return {
        "session_id": session_id,
        "source_preview": SessionManager.array_to_base64_jpeg(src_img),
        "reference_preview": SessionManager.array_to_base64_jpeg(ref_img),
        "source_info": {
            "width": meta_s["width"],
            "height": meta_s["height"],
            "sensor": "Chandrayaan-2 OHRC (0.25m)"
        },
        "reference_info": {
            "width": meta_r["width"],
            "height": meta_r["height"],
            "sensor": "Chandrayaan-2 TMC-2 (5.0m)"
        }
    }
