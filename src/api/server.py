"""FastAPI server for REWIND - forensic reconstruction from damage photos."""

import os
import json
import uuid
import time
import asyncio
import traceback
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.utils.config import Config
from src.pipeline.meta_client import MetaClient
from src.pipeline.reconstruction import ReconstructionEngine, DamageType
from src.visualization.physics_sim import get_simulator
from src.pipeline.demo_data import (
    DEMO_SEGMENTS,
    DEMO_ANALYSIS,
    DEMO_REASONING,
    DEMO_SIM_PARAMS,
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="REWIND",
    description="AI Forensic Reconstruction - Reverse-engineer what happened from damage photos",
    version="1.0.0",
)

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main REWIND interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "demo_mode": Config.is_demo_mode(),
    })


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in Config.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(Config.ALLOWED_IMAGE_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > Config.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {Config.MAX_UPLOAD_SIZE // (1024*1024)}MB",
        )

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{ext}"
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "path": str(file_path),
        "size": len(contents),
    }


@app.post("/api/reconstruct")
async def reconstruct(
    file_id: str = Form(...),
    damage_type: str = Form("auto"),
    deep_reasoning: bool = Form(False),
):
    """Run the full REWIND reconstruction pipeline via SSE streaming."""

    # Find the uploaded file
    matches = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    image_path = str(matches[0])

    # Parse damage type
    try:
        dtype = DamageType(damage_type)
    except ValueError:
        dtype = DamageType.AUTO

    demo_mode = Config.is_demo_mode()

    if demo_mode:
        return StreamingResponse(
            _demo_event_stream(image_path, dtype, deep_reasoning),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        return StreamingResponse(
            _live_event_stream(image_path, dtype, deep_reasoning),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )


async def _demo_event_stream(image_path: str, dtype: DamageType, deep_reasoning: bool):
    """Stream demo reconstruction with realistic delays to simulate API calls."""
    start_time = time.time()

    # Resolve damage type for demo data lookup
    demo_type = dtype.value if dtype != DamageType.AUTO else "impact"
    if demo_type not in DEMO_SEGMENTS:
        demo_type = "impact"

    # ── Stage 1: Segmentation ──
    yield _sse_event("stage", {
        "stage": "segmentation",
        "status": "running",
        "message": "Segmenting damage regions with SAM 3.1...",
    })
    await asyncio.sleep(1.2)  # Simulate API latency

    segments = DEMO_SEGMENTS.get(demo_type, DEMO_SEGMENTS["impact"])
    yield _sse_event("stage", {
        "stage": "segmentation",
        "status": "complete",
        "data": {"segments": segments, "count": len(segments)},
        "message": f"Found {len(segments)} damage regions",
    })

    # ── Stage 2: Physics Analysis ──
    yield _sse_event("stage", {
        "stage": "analysis",
        "status": "running",
        "message": "Analyzing damage physics with Muse Spark...",
    })
    await asyncio.sleep(2.0)  # Simulate heavier analysis call

    analysis = DEMO_ANALYSIS.get(demo_type, DEMO_ANALYSIS["impact"])
    yield _sse_event("stage", {
        "stage": "analysis",
        "status": "complete",
        "data": analysis,
        "message": "Physics analysis complete",
    })

    # ── Stage 3: Deep Reasoning (optional) ──
    if deep_reasoning:
        yield _sse_event("stage", {
            "stage": "deep_reasoning",
            "status": "running",
            "message": "Deep causal reasoning with Muse Wonder...",
        })
        await asyncio.sleep(3.0)  # Muse Wonder takes longer

        reasoning = DEMO_REASONING.get(demo_type, DEMO_REASONING["impact"])
        yield _sse_event("stage", {
            "stage": "deep_reasoning",
            "status": "complete",
            "data": {"refined_analysis": reasoning},
            "message": "Deep reasoning complete",
        })

    # ── Stage 4: Physics Simulation ──
    yield _sse_event("stage", {
        "stage": "simulation",
        "status": "running",
        "message": "Generating physics reconstruction...",
    })
    await asyncio.sleep(0.5)

    sim_params = DEMO_SIM_PARAMS.get(demo_type, DEMO_SIM_PARAMS["impact"])
    simulator = get_simulator(demo_type)
    sim_frames = simulator.simulate(sim_params)

    yield _sse_event("stage", {
        "stage": "simulation",
        "status": "complete",
        "data": {"frames": sim_frames, "frame_count": len(sim_frames)},
        "message": f"Generated {len(sim_frames)} animation frames",
    })

    # ── Stage 5: Reconstruction Image ──
    yield _sse_event("stage", {
        "stage": "visualization",
        "status": "running",
        "message": "Generating reconstruction image with Muse Image...",
    })
    await asyncio.sleep(1.5)

    # In demo mode, use a placeholder data URI (a dark gradient with "DEMO" text)
    # The real mode will use Muse Image to generate this
    yield _sse_event("stage", {
        "stage": "visualization",
        "status": "complete",
        "data": {"image_url": None, "demo_note": "Reconstruction image requires Muse Image API key"},
        "message": "Visualization stage complete (demo mode)",
    })

    # ── Final Result ──
    elapsed = time.time() - start_time
    yield _sse_event("complete", {
        "analysis": analysis,
        "segments": segments,
        "simulation_frames": sim_frames,
        "processing_time_ms": int(elapsed * 1000),
        "damage_type": demo_type,
        "demo_mode": True,
    })


async def _live_event_stream(image_path: str, dtype: DamageType, deep_reasoning: bool):
    """Stream live reconstruction using real Meta AI API calls."""
    engine = ReconstructionEngine()
    start_time = time.time()

    try:
        # Stage 1: Segmentation
        yield _sse_event("stage", {"stage": "segmentation", "status": "running", "message": "Segmenting damage regions with SAM 3.1..."})

        try:
            seg_prompts = engine._get_segmentation_prompts(dtype)
            all_segments = []
            for prompt in seg_prompts:
                seg_result = await engine.client.segment_damage(image_path, prompt)
                all_segments.extend(seg_result.get("segments", []))

            yield _sse_event("stage", {
                "stage": "segmentation",
                "status": "complete",
                "data": {"segments": all_segments, "count": len(all_segments)},
                "message": f"Found {len(all_segments)} damage regions",
            })
        except Exception as e:
            yield _sse_event("stage", {
                "stage": "segmentation",
                "status": "error",
                "message": f"Segmentation error: {str(e)}",
            })
            all_segments = []

        # Stage 2: Physics Analysis
        yield _sse_event("stage", {"stage": "analysis", "status": "running", "message": "Analyzing damage physics with Muse Spark..."})

        try:
            analysis = await engine.client.analyze_damage(
                image_path,
                damage_type=dtype.value if dtype != DamageType.AUTO else "auto",
            )

            yield _sse_event("stage", {
                "stage": "analysis",
                "status": "complete",
                "data": analysis,
                "message": "Physics analysis complete",
            })
        except Exception as e:
            yield _sse_event("stage", {
                "stage": "analysis",
                "status": "error",
                "message": f"Analysis error: {str(e)}",
            })
            analysis = {}

        # Stage 3: Deep Reasoning (optional)
        if deep_reasoning and analysis.get("reconstruction", {}).get("narrative"):
            yield _sse_event("stage", {"stage": "deep_reasoning", "status": "running", "message": "Deep causal reasoning with Muse Wonder..."})

            try:
                context = json.dumps({
                    "damage_description": analysis.get("damage_description", ""),
                    "physics_analysis": analysis.get("physics_analysis", {}),
                    "initial_reconstruction": analysis.get("reconstruction", {}).get("narrative", ""),
                    "parameters": analysis.get("parameters", {}),
                }, indent=2)

                deep_result = await engine.client.deep_reason(
                    context=context,
                    question="Refine this forensic reconstruction. Identify inconsistencies, suggest alternative scenarios, and provide more precise parameter estimates.",
                )

                yield _sse_event("stage", {
                    "stage": "deep_reasoning",
                    "status": "complete",
                    "data": {"refined_analysis": deep_result},
                    "message": "Deep reasoning complete",
                })
            except Exception as e:
                yield _sse_event("stage", {
                    "stage": "deep_reasoning",
                    "status": "error",
                    "message": f"Deep reasoning error: {str(e)}",
                })

        # Stage 4: Physics Simulation
        yield _sse_event("stage", {"stage": "simulation", "status": "running", "message": "Generating physics reconstruction..."})

        try:
            detected_type = analysis.get("damage_type", dtype.value if dtype != DamageType.AUTO else "impact")
            sim_params = analysis.get("parameters", {}).get("estimated_values", {})

            simulator = get_simulator(detected_type)
            sim_frames = simulator.simulate(sim_params)

            yield _sse_event("stage", {
                "stage": "simulation",
                "status": "complete",
                "data": {"frames": sim_frames, "frame_count": len(sim_frames)},
                "message": f"Generated {len(sim_frames)} animation frames",
            })
        except Exception as e:
            yield _sse_event("stage", {
                "stage": "simulation",
                "status": "error",
                "message": f"Simulation error: {str(e)}",
            })
            sim_frames = []

        # Stage 5: Reconstruction Image
        yield _sse_event("stage", {"stage": "visualization", "status": "running", "message": "Generating reconstruction image with Muse Image..."})

        reconstruction_image = None
        try:
            if analysis.get("reconstruction", {}).get("narrative"):
                viz_prompt = _build_viz_prompt(analysis, detected_type)
                reconstruction_image = await engine.client.generate_reconstruction_image(viz_prompt)

            yield _sse_event("stage", {
                "stage": "visualization",
                "status": "complete",
                "data": {"image_url": reconstruction_image},
                "message": "Reconstruction visualization generated",
            })
        except Exception as e:
            yield _sse_event("stage", {
                "stage": "visualization",
                "status": "error",
                "message": f"Visualization error: {str(e)}",
            })

        # Final result
        elapsed = time.time() - start_time
        yield _sse_event("complete", {
            "analysis": analysis,
            "segments": all_segments,
            "simulation_frames": sim_frames,
            "reconstruction_image": reconstruction_image,
            "processing_time_ms": int(elapsed * 1000),
            "damage_type": detected_type,
        })

    except Exception as e:
        yield _sse_event("error", {
            "message": f"Pipeline error: {str(e)}",
            "traceback": traceback.format_exc(),
        })
    finally:
        await engine.close()


@app.post("/api/simulate")
async def simulate_physics(
    damage_type: str = Form("impact"),
    params: str = Form("{}"),
):
    """Run a standalone physics simulation."""
    try:
        sim_params = json.loads(params)
    except json.JSONDecodeError:
        sim_params = {}

    simulator = get_simulator(damage_type)
    frames = simulator.simulate(sim_params)

    return {"frames": frames, "frame_count": len(frames), "damage_type": damage_type}


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "meta_api_configured": not Config.is_demo_mode(),
        "demo_mode": Config.is_demo_mode(),
        "version": "1.0.0",
    }


def _sse_event(event_type: str, data: dict) -> str:
    """Format a server-sent event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _build_viz_prompt(analysis: dict, damage_type: str) -> str:
    """Build a Muse Image prompt from analysis results."""
    desc = analysis.get("damage_description", "damage scene")[:200]
    narrative = analysis.get("reconstruction", {}).get("narrative", "")[:200]
    hints = analysis.get("visualization_hints", {})
    vectors = hints.get("vectors", [])
    trajectories = hints.get("trajectories", [])

    parts = [
        f"Technical forensic reconstruction diagram of a {damage_type} event.",
        f"Scene: {desc}",
        f"Reconstruction: {narrative}",
    ]
    if vectors:
        parts.append(f"Force vectors: {', '.join(str(v) for v in vectors[:3])}")
    if trajectories:
        parts.append(f"Trajectories: {', '.join(str(t) for t in trajectories[:3])}")

    parts.append("Style: dark background, neon-colored physics overlays, clean engineering diagram with measurements and annotations.")
    return " ".join(parts)
