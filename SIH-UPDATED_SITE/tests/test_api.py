"""
API Integration Test Suite
Verifies FastAPI endpoints: health, sample loading, and pipeline execution.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.anyio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "online"
        assert data["team"] == "TEAM ZERODAY"


@pytest.mark.anyio
async def test_sample_loading_and_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Load sample
        load_res = await ac.post("/api/ingest/load-sample", data={"sample_id": "synthetic_development_pair"})
        assert load_res.status_code == 200
        load_data = load_res.json()
        session_id = load_data["session_id"]
        assert session_id is not None

        # 2. Run pipeline
        run_res = await ac.post("/api/pipeline/run", json={
            "session_id": session_id,
            "preprocessing_mode": "clahe",
            "detector_type": "sift",
            "descriptor_type": "sift",
            "max_features": 1200,
            "ratio_threshold": 0.85,
            "ransac_threshold_px": 5.0,
            "preferred_model": "auto",
            "blind_mode": True,
            "source_sensor": "OHRC",
            "reference_sensor": "TMC2",
            "source_gsd": 0.25,
            "reference_gsd": 5.0
        })

        assert run_res.status_code == 200
        data = run_res.json()
        assert data["success"] is True
        assert data["metrics"]["inlier_count"] >= 4
        assert data["metrics"]["rmse_px"] < 3.5
        assert len(data["matches"]) > 0
        assert data["dna"]["canonical_hash"].startswith("DNA-")
        assert len(data["court_verdicts"]) > 0
        assert len(data["graph_topology"]["nodes"]) > 0
        assert "true_sensor_source" not in data["blind_audit"]
        reveal_res = await ac.post("/api/pipeline/reveal-blind", json={"session_id": session_id})
        assert reveal_res.status_code == 200
        assert reveal_res.json()["true_sensor_source"] == "OHRC"
        assert "match_id" in data["graph_topology"]["nodes"][0]


@pytest.mark.anyio
async def test_unknown_sample_is_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/ingest/load-sample", data={"sample_id": "pair_2_extreme"})
        assert res.status_code == 404


@pytest.mark.anyio
async def test_invalid_upload_is_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post(
            "/api/ingest/upload",
            files={"file": ("../../unsafe.txt", b"not an image", "text/plain")},
            data={"role": "source", "sensor": "OHRC"},
        )
        assert res.status_code == 400
