# REWIND - AI Forensics for Everyday Life

**Show it the damage. It shows you what happened.**

REWIND is an AI-powered forensic reconstruction tool that analyzes photos and videos of damage to reverse-engineer what caused it. Using physics-based reasoning and Meta's AI toolkit, REWIND turns aftermath into animated reconstruction.

## How It Works

1. **Upload** - Take a photo or video of any damage (dent, crack, water stain, toppled object)
2. **Segment** - SAM 3.1 identifies and segments damage patterns with pixel precision
3. **Reason** - Muse Spark analyzes the physics of what could produce the observed damage
4. **Simulate** - A physics engine reconstructs the event and verifies it matches observations
5. **Visualize** - Watch an animated reconstruction of exactly what happened

## Reconstruction Types

- **Impact Analysis** - Cracks, dents, fractures: compute impact angle, velocity, and force
- **Tipping & Collapse** - Furniture, structures: trace the failure sequence and root cause
- **Fluid Trace** - Water damage, spills: follow the flow path back to the source

## Tech Stack

- **Meta Muse Spark** - Visual reasoning and physics analysis
- **Meta SAM 3.1** - Damage region segmentation
- **Meta Muse Wonder** - Deep causal chain reasoning for complex scenarios
- **Meta Muse Image** - Reconstruction visualization generation
- **Python/FastAPI** - Backend API
- **Canvas/WebGL** - Interactive reconstruction visualization

## Built for Meta Global AI Developer Hackathon 2026

Team Parallax | "Push the Frontier" track
