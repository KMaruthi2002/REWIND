# REWIND - AI Forensic Reconstruction

> **Upload a photo of damage. Watch AI reverse-engineer exactly what happened.**

REWIND analyzes photos of physical damage and reconstructs the event that caused it using Meta AI's multimodal models and real-time physics simulation. See cracked glass, a toppled shelf, or water damage -- and REWIND shows you the force, angle, speed, and sequence of events, animated over the original photo.

Built for the **Meta Global AI Hackathon 2026** by Team Parallax.

---

## How It Works

REWIND runs a 5-stage AI pipeline, streaming results in real time:

| Stage | Model | What It Does |
|-------|-------|-------------|
| 1. Segment | **SAM 3.1** | Identifies and isolates damage regions in the photo |
| 2. Analyze | **Muse Spark 1.3** | Multimodal physics analysis -- estimates forces, velocities, materials |
| 3. Reason | **Muse Wonder** | Deep causal chain reasoning -- why did this happen? |
| 4. Simulate | Physics Engine | Generates frame-by-frame reconstruction animation |
| 5. Visualize | **Muse Image** | Creates AI-generated "before the damage" reconstruction |

Every stage streams progress via SSE, so you watch the analysis unfold live.

## Demo

**No API key needed to try it.** REWIND ships with a full demo mode that returns realistic pre-built analysis with simulated delays, so you can experience the complete flow immediately.

```bash
git clone https://github.com/KMaruthi2002/REWIND.git
cd REWIND
pip3 install -r requirements.txt
python3 app.py
# Open http://localhost:8000
```

Upload any damage photo and hit RECONSTRUCT. The app auto-detects your missing API key and runs the full pipeline with simulated Meta AI responses.

## What Makes This Different

**Forensic reconstruction from a single photo is novel.** Existing damage analysis tools classify damage type or estimate severity. REWIND goes further -- it reverse-engineers the entire event:

- **Impact analysis**: A cracked windshield becomes "28g steel projectile at 30 m/s, 35-degree angle, Hertzian contact fracture with 11 radial cracks"
- **Collapse reconstruction**: A fallen bookshelf becomes "seismic P-wave at 0.3g triggered cascading failure, 2.1s from initial displacement to ground contact"
- **Fluid trace analysis**: Water damage becomes "4.2 L/min flow rate from 1.8m elevation, capillary front advanced 34cm over 45 minutes"

The physics simulation plays back as a canvas overlay on top of your original photo -- force vectors, trajectories, and deformation in real time.

## Architecture

```
rewind/
  app.py                          # Entry point (uvicorn, port 8000)
  src/
    api/server.py                 # FastAPI + SSE streaming pipeline
    pipeline/
      meta_client.py              # Meta Model API client (Spark, SAM, Wonder, Image)
      reconstruction.py           # Orchestrates the 5-stage pipeline
      demo_data.py                # Realistic mock responses for demo mode
    visualization/
      physics_sim.py              # Impact, tipping, and fluid simulators
    utils/
      config.py                   # API key + demo mode detection
  static/
    js/app.js                     # Frontend controller with SSE parsing
    js/renderer.js                # Canvas overlay renderer for physics animations
    css/main.css                  # Dark theme UI
  templates/
    index.html                    # Single-page app
```

## Three Reconstruction Types

### Impact
Cracks, dents, shattered glass. Estimates projectile mass, velocity, angle of impact, and material properties. Simulates the moment of impact with force vectors and fracture propagation.

### Tipping / Collapse
Fallen furniture, structural failures. Calculates center of mass, tipping threshold, angular acceleration, and cascade timing. Animates the full collapse sequence.

### Fluid Trace
Water damage, spills, stains. Models flow rate, source elevation, viscosity, and capillary dynamics. Visualizes fluid front progression over time.

## Meta AI Integration

REWIND uses four Meta AI models through the Meta Model API:

- **SAM 3.1** (`sam-3.1`): Zero-shot segmentation of arbitrary damage regions
- **Muse Spark 1.3** (`muse-spark-1.3`): Multimodal image analysis for physics parameter extraction
- **Muse Wonder** (`muse-wonder`): Extended reasoning for deep causal chains and confidence assessment
- **Muse Image** (`muse-image`): Generates "before the damage" reconstruction images

## Running with a Real API Key

```bash
export META_MODEL_API_KEY=your_key_here
python app.py
```

The app auto-detects the key and switches from demo mode to live Meta AI calls. The same SSE pipeline streams real model responses.

## Tech Stack

- **Backend**: Python, FastAPI, uvicorn
- **Frontend**: Vanilla JS, Canvas API, SSE
- **AI**: Meta Model API (SAM 3.1, Muse Spark, Muse Wonder, Muse Image)
- **Physics**: Custom simulation engines for impact, tipping, and fluid dynamics

## Team Parallax

- **Maruthi Kunchala** -- Indie Track

## License

MIT
