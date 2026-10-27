"""Core reconstruction engine - orchestrates the full REWIND pipeline."""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.pipeline.meta_client import MetaClient


class DamageType(str, Enum):
    IMPACT = "impact"
    TIPPING = "tipping"
    FLUID = "fluid"
    STRUCTURAL = "structural"
    AUTO = "auto"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReconstructionResult:
    """Complete result of a REWIND reconstruction analysis."""

    # Input
    image_path: str
    damage_type: DamageType

    # Analysis
    damage_description: str = ""
    physics_analysis: dict = field(default_factory=dict)
    reconstruction_narrative: str = ""
    timeline: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM

    # Segmentation
    segments: list = field(default_factory=list)

    # Visualization
    visualization_hints: dict = field(default_factory=dict)
    reconstruction_image_url: Optional[str] = None

    # Metadata
    processing_time_ms: int = 0
    pipeline_stages: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "image_path": self.image_path,
            "damage_type": self.damage_type.value,
            "damage_description": self.damage_description,
            "physics_analysis": self.physics_analysis,
            "reconstruction": {
                "narrative": self.reconstruction_narrative,
                "timeline": self.timeline,
                "confidence": self.confidence.value,
            },
            "parameters": self.parameters,
            "segments": self.segments,
            "visualization": self.visualization_hints,
            "reconstruction_image_url": self.reconstruction_image_url,
            "processing_time_ms": self.processing_time_ms,
            "pipeline_stages": self.pipeline_stages,
        }


class ReconstructionEngine:
    """Orchestrates the full REWIND pipeline:
    1. Segment damage with SAM 3.1
    2. Analyze physics with Muse Spark
    3. Deep reason with Muse Wonder (for complex cases)
    4. Generate visualization with Muse Image
    """

    def __init__(self):
        self.client = MetaClient()

    async def reconstruct(
        self,
        image_path: str,
        damage_type: DamageType = DamageType.AUTO,
        include_deep_reasoning: bool = False,
        generate_image: bool = True,
    ) -> ReconstructionResult:
        """Run the full reconstruction pipeline on an image."""
        start_time = time.time()
        result = ReconstructionResult(image_path=image_path, damage_type=damage_type)

        # Stage 1: Segment damage regions with SAM 3.1
        result.pipeline_stages.append({"stage": "segmentation", "status": "running"})
        try:
            seg_prompts = self._get_segmentation_prompts(damage_type)
            all_segments = []
            for prompt in seg_prompts:
                seg_result = await self.client.segment_damage(image_path, prompt)
                all_segments.extend(seg_result.get("segments", []))
            result.segments = all_segments
            result.pipeline_stages[-1]["status"] = "complete"
            result.pipeline_stages[-1]["segment_count"] = len(all_segments)
        except Exception as e:
            result.pipeline_stages[-1]["status"] = "error"
            result.pipeline_stages[-1]["error"] = str(e)

        # Stage 2: Analyze damage physics with Muse Spark
        result.pipeline_stages.append({"stage": "analysis", "status": "running"})
        try:
            analysis = await self.client.analyze_damage(
                image_path,
                damage_type=damage_type.value if damage_type != DamageType.AUTO else "auto",
            )

            result.damage_description = analysis.get("damage_description", "")
            result.physics_analysis = analysis.get("physics_analysis", {})
            result.reconstruction_narrative = analysis.get("reconstruction", {}).get("narrative", "")
            result.timeline = analysis.get("reconstruction", {}).get("timeline", [])
            result.parameters = analysis.get("parameters", {})
            result.visualization_hints = analysis.get("visualization_hints", {})

            confidence_str = analysis.get("reconstruction", {}).get("confidence", "medium")
            try:
                result.confidence = ConfidenceLevel(confidence_str)
            except ValueError:
                result.confidence = ConfidenceLevel.MEDIUM

            # Auto-detect damage type if needed
            if damage_type == DamageType.AUTO:
                detected_type = analysis.get("damage_type", "impact")
                try:
                    result.damage_type = DamageType(detected_type)
                except ValueError:
                    result.damage_type = DamageType.IMPACT

            result.pipeline_stages[-1]["status"] = "complete"
        except Exception as e:
            result.pipeline_stages[-1]["status"] = "error"
            result.pipeline_stages[-1]["error"] = str(e)

        # Stage 3: Deep reasoning with Muse Wonder (optional, for complex cases)
        if include_deep_reasoning and result.reconstruction_narrative:
            result.pipeline_stages.append({"stage": "deep_reasoning", "status": "running"})
            try:
                context = json.dumps({
                    "damage_description": result.damage_description,
                    "physics_analysis": result.physics_analysis,
                    "initial_reconstruction": result.reconstruction_narrative,
                    "parameters": result.parameters,
                }, indent=2)

                deep_analysis = await self.client.deep_reason(
                    context=context,
                    question="Refine this forensic reconstruction. Identify any inconsistencies in the physics, suggest alternative scenarios, and provide more precise parameter estimates. What is the most likely sequence of events?"
                )

                # Append deep reasoning to the narrative
                result.reconstruction_narrative += f"\n\n--- Deep Analysis ---\n{deep_analysis}"
                result.pipeline_stages[-1]["status"] = "complete"
            except Exception as e:
                result.pipeline_stages[-1]["status"] = "error"
                result.pipeline_stages[-1]["error"] = str(e)

        # Stage 4: Generate reconstruction visualization with Muse Image
        if generate_image and result.reconstruction_narrative:
            result.pipeline_stages.append({"stage": "visualization", "status": "running"})
            try:
                viz_description = self._build_visualization_prompt(result)
                image_url = await self.client.generate_reconstruction_image(viz_description)
                result.reconstruction_image_url = image_url
                result.pipeline_stages[-1]["status"] = "complete"
            except Exception as e:
                result.pipeline_stages[-1]["status"] = "error"
                result.pipeline_stages[-1]["error"] = str(e)

        result.processing_time_ms = int((time.time() - start_time) * 1000)
        return result

    def _get_segmentation_prompts(self, damage_type: DamageType) -> list[str]:
        """Get SAM segmentation prompts based on damage type."""
        base_prompts = ["damage", "crack", "dent", "stain", "broken"]

        type_prompts = {
            DamageType.IMPACT: ["crack", "fracture", "dent", "impact mark", "shattered glass"],
            DamageType.TIPPING: ["fallen object", "tilted furniture", "debris", "displaced object"],
            DamageType.FLUID: ["water stain", "water damage", "puddle", "wet area", "discoloration"],
            DamageType.STRUCTURAL: ["crack", "fracture", "deformation", "buckled surface"],
        }

        if damage_type in type_prompts:
            return type_prompts[damage_type]
        return base_prompts

    def _build_visualization_prompt(self, result: ReconstructionResult) -> str:
        """Build a prompt for Muse Image to generate reconstruction visualization."""
        hints = result.visualization_hints
        vectors = hints.get("vectors", [])
        trajectories = hints.get("trajectories", [])
        annotations = hints.get("annotations", [])

        prompt_parts = [
            f"Forensic reconstruction of {result.damage_type.value} event.",
            f"Scene: {result.damage_description[:200]}",
        ]

        if vectors:
            prompt_parts.append(f"Show force vectors: {', '.join(vectors[:3])}")
        if trajectories:
            prompt_parts.append(f"Show trajectories: {', '.join(trajectories[:3])}")
        if annotations:
            prompt_parts.append(f"Annotate: {', '.join(annotations[:3])}")

        params = result.parameters.get("estimated_values", {})
        if params:
            param_strs = [f"{k}: {v}" for k, v in list(params.items())[:5]]
            prompt_parts.append(f"Parameters: {', '.join(param_strs)}")

        return " ".join(prompt_parts)

    async def close(self):
        await self.client.close()
