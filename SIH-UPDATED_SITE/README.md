# SIH26166: Multi-Modal, Sun Angle & Scale Invariant Lunar Image Correspondence Platform
**TEAM ZERODAY | Indian Space Research Organisation (ISRO) | Space Technology**

---

## Mission & Problem Statement
* **Theme**: Space Technology
* **Problem Statement ID**: `SIH26166`
* **Organization**: Indian Space Research Organisation (ISRO)
* **Title**: *"Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)"*

This software platform provides an end-to-end classical computer-vision prototype for planetary image registration. It accepts user-provided lunar imagery and processes it through normalization, correspondence detection, robust geometric estimation, warping, and runtime evaluation.

The bundled development pair is procedurally synthesized crater terrain for regression testing. It is not authentic Chandrayaan-2 imagery and must not be used as mission-data validation. Uploaded OHRC, TMC-2, IIRS, or other compatible imagery follows the same processing path.

RMSE, inlier statistics, mutual information, SSIM, grid-distribution entropy, graph measures, and DNA signatures are computed from each runtime result. They are not guarantees of scientific accuracy; real mission validation requires independently sourced imagery and ground truth.

---

## System Architecture

```text
zeroday_lunar_cv/
├── backend/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── ingestion.py       # Upload, metadata, sample benchmark pairs
│   │   │   └── pipeline.py        # Complete execution coordinator & results
│   │   └── schemas.py             # Typed Pydantic contracts
│   ├── core/
│   │   ├── config.py              # Environment paths & CORS
│   │   └── session_manager.py     # Ephemeral file-backed session manager
│   └── main.py                    # FastAPI server entrypoint
├── cv_engine/
│   ├── ingestion/
│   │   └── loader.py              # 16-bit GeoTIFF/TIFF/PNG multi-band loader
│   ├── preprocessing/
│   │   ├── illumination.py        # Phase Congruency, Retinex, CLAHE, Symmetric Gradients
│   │   ├── normalizer.py          # Radiometric percentile dynamic range normalization
│   │   └── scale_pyramid.py       # GSD harmonization & Fourier-Mellin log-polar correlation
│   ├── correspondence/
│   │   ├── anms.py                # Adaptive Non-Maximal Suppression (Uniform Dispersion)
│   │   ├── detectors.py           # Scale-space interest point extractors
│   │   ├── descriptors.py         # Symmetric CFOG (mod pi) & SIFT
│   │   └── coarse_to_fine.py      # Bidirectional Lowe ratio matching
│   ├── geometry/
│   │   ├── conditioning.py        # Hartley-Zisserman coordinate-normalized SVD condition check
│   │   ├── estimator.py           # Robust USAC-MAGSAC++ & RANSAC model estimation
│   │   └── subpixel.py            # Local 2D quadratic peak refinement
│   ├── registration/
│   │   ├── warper.py              # Sub-pixel bicubic warping
│   │   └── blending.py            # Difference heatmap, checkerboard, false-color composite
│   ├── metrics/
│   │   ├── rmse.py                # True Euclidean transfer RMSE & MAD
│   │   ├── spatial_distribution.py# Fixed-grid entropy & coverage
│   │   └── cross_modal.py         # Normalized Mutual Information & SSIM
│   └── zero_day/                  # The 4 Special Innovation Modules
│       ├── court.py               # Lunar Correspondence Court (Multi-Evidence Trial)
│       ├── dna.py                 # Lunar Correspondence DNA (Physical 8-D Fingerprint)
│       ├── blind_test.py          # Blind Lunar Test Engine (Sensor-Agnostic Audit)
│       └── graph.py               # Lunar Correspondence Graph (Delaunay Structural Topology)
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx           # Mission Control Dashboard
│   │   ├── components/
│   │   │   ├── Header.tsx         # Space telemetry title bar
│   │   │   ├── panels/            # Ingestion, Controls, Telemetry, ZeroDay Suite
│   │   │   └── visualizers/       # Dual Viewport, Registration Curtain, Topology Graph
│   │   ├── lib/api.ts             # API client
│   │   └── types/index.ts         # TypeScript schema definitions
├── data/
│   ├── samples/                   # Synthetic development pair for regression testing
│   └── generator.py               # Fractal DEM & Lommel-Seeliger shading synthesizer
└── tests/
    ├── test_cv_engine.py          # Computer vision unit & integration tests
    ├── test_zero_day_modules.py   # Court, DNA, Blind Test, and Graph tests
    └── test_api.py                # FastAPI endpoint integration tests
```

---

## The Four TEAM ZERODAY Innovation Modules

### 1. Lunar Correspondence Court
* Candidate correspondences stand trial before a judicial multi-evidence arbitration engine.
* Evaluates 4 independent pieces of evidence:
  1. **Photometric / Spectral**: Local patch Zero-Mean Normalized Cross-Correlation (ZNCC).
  2. **Local Affine Consistency**: Preserved relative coordinates across 5-nearest neighbors.
  3. **Context Distance Ratio**: Angular and scale consistency with surrounding lunar points.
  4. **Global Consensus Residual**: Physical reprojection transfer error under the consensus model.
* Verdicts: `ACCEPT`, `UNCERTAIN`, `REJECT` with decision rationales.

### 2. Lunar Correspondence DNA
* Generates an 8-dimensional normalized mathematical vector derived from runtime transformation properties:
  $[s, \theta, \log_{10}(\kappa), S_{\text{grid}}, \mu_{\text{res}}, \sigma^2_{\text{res}}, \gamma_{\text{skew}}, NMI]$.
* Computes a deterministic SHA-256 canonical hash (e.g. `DNA-8B1F-402A-D910-E714`) and verifiable certificate ID (`CH2-CERT-XXXX`).
* Downloadable JSON verification certificate for mission archives.

### 3. Blind Lunar Test
* Evaluates algorithm objectivity by stripping all sensor metadata, GSD labels, and solar angles.
* The system estimates scale ratio and rotation using Fourier-Mellin log-polar phase correlation without sensor metadata.
* Post-execution audit compares the estimate with supplied sensor/GSD metadata when available. This is an analysis aid, not independent mission ground truth.

### 4. Lunar Correspondence Graph
* Constructs a Delaunay triangulation topological graph over corresponding lunar keypoints.
* Evaluates triangular edge strain and orientation inversions as structural diagnostics. Interpretation as physical relief deformation requires external validation.

---

## Quickstart Guide

### Prerequisites
* **Python 3.10+** (tested on Python 3.13)
* **Node.js 18+** (tested on Node.js v24)

### Running the System
You can start both backend and frontend with a single command:

**On Windows (PowerShell):**
```powershell
.\run_platform.ps1
```

**Or On Windows (Command Prompt):**
```bat
run_platform.bat
```

### Running Components Individually:

**1. Start the FastAPI Backend:**
```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --app-dir . --host 127.0.0.1 --port 8000
```
* Interactive API Documentation (Swagger): `http://127.0.0.1:8000/docs`
* Health Endpoint: `http://127.0.0.1:8000/api/health`

**2. Start the Next.js Frontend:**
```powershell
cd frontend
npm run dev
```
* Open your browser at: `http://localhost:3000`

---

### Running the Automated Test Suite

To verify the runtime pipeline and verification modules:

```powershell
$env:PYTHONPATH = "."
python -m pytest -v tests/
```
Output:
```text
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_sample_loading_and_pipeline PASSED
tests/test_cv_engine.py::test_image_loader PASSED
tests/test_cv_engine.py::test_illumination_normalizer PASSED
tests/test_cv_engine.py::test_detector_with_anms PASSED
tests/test_cv_engine.py::test_end_to_end_pipeline PASSED
tests/test_zero_day_modules.py::test_court_verdict_outlier_rejection PASSED
tests/test_zero_day_modules.py::test_dna_determinism PASSED
tests/test_zero_day_modules.py::test_blind_test_audit_grading PASSED
tests/test_zero_day_modules.py::test_correspondence_graph_topology PASSED
============================= 20 passed =============================
```

Blind runs return only runtime estimation evidence initially. Sensor/GSD comparison metadata is stored server-side and is returned only by the session-scoped `POST /api/pipeline/reveal-blind` endpoint after evaluation.

The Court panel exposes computed evidence for each match. The Delaunay graph uses runtime inlier points, preserves their match IDs, and renders paired source/reference structures. Fewer than four inliers are reported as insufficient evidence for graph construction.
