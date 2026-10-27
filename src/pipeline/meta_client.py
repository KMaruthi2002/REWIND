"""Client for Meta Model API - Muse Spark, SAM 3.1, and Muse Image."""

import base64
import json
import httpx
from pathlib import Path
from typing import Optional

from src.utils.config import Config


class MetaClient:
    """Unified client for Meta Model API endpoints."""

    def __init__(self):
        self.api_key = Config.META_API_KEY
        self.base_url = Config.META_API_BASE
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def _encode_image(self, image_path: str) -> str:
        """Encode an image file to base64 data URL."""
        path = Path(image_path)
        suffix = path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime = mime_map.get(suffix, "image/jpeg")
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{data}"

    async def analyze_damage(self, image_path: str, damage_type: str = "auto") -> dict:
        """
        Use Muse Spark to analyze damage in an image and reason about what caused it.

        Returns a structured analysis including:
        - damage_description: what the damage looks like
        - physics_analysis: the physics behind the damage
        - reconstruction: what likely happened
        - parameters: estimated physical parameters (angle, force, velocity, etc.)
        """
        image_url = self._encode_image(image_path)

        type_context = ""
        if damage_type == "impact":
            type_context = "Focus on impact analysis: fracture patterns, impact angle, velocity, force vectors, and impactor characteristics."
        elif damage_type == "tipping":
            type_context = "Focus on tipping/collapse analysis: center of mass, base of support, failure sequence, and destabilizing forces."
        elif damage_type == "fluid":
            type_context = "Focus on fluid trace analysis: flow patterns, source location, flow rate, duration, and path reconstruction."

        prompt = f"""You are REWIND, an AI forensic reconstruction system. Analyze this image of damage and reverse-engineer what happened using physics.

{type_context}

Provide your analysis as a JSON object with these fields:
{{
    "damage_description": "Detailed description of the visible damage patterns",
    "damage_type": "impact|tipping|fluid|structural|other",
    "physics_analysis": {{
        "mechanism": "The physical mechanism that caused this damage",
        "key_observations": ["List of physics-relevant observations from the image"],
        "equations": ["Relevant physics equations/principles"],
        "constraints": ["Physical constraints derived from the damage pattern"]
    }},
    "reconstruction": {{
        "narrative": "Step-by-step narrative of what happened",
        "timeline": ["Ordered sequence of events"],
        "confidence": "high|medium|low"
    }},
    "parameters": {{
        "estimated_values": {{}},
        "units": {{}},
        "ranges": {{}}
    }},
    "visualization_hints": {{
        "key_points": ["Points of interest to highlight in the visualization"],
        "vectors": ["Force/motion vectors to draw"],
        "trajectories": ["Paths to animate"],
        "annotations": ["Text annotations for the overlay"]
    }}
}}

Be specific with numbers and physics. Use real units and realistic estimates. This is forensic-grade analysis."""

        response = await self.client.post(
            f"{self.base_url}/responses",
            json={
                "model": Config.MUSE_SPARK_MODEL,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_image", "image_url": image_url},
                            {"type": "input_text", "text": prompt},
                        ],
                    }
                ],
                "temperature": 0.3,
            },
        )
        response.raise_for_status()
        result = response.json()

        # Extract the text response
        output_text = ""
        for item in result.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        output_text = content.get("text", "")

        # Parse JSON from the response
        try:
            # Try to extract JSON from the response
            json_start = output_text.find("{")
            json_end = output_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(output_text[json_start:json_end])
            else:
                analysis = {"raw_analysis": output_text, "parse_error": "No JSON found"}
        except json.JSONDecodeError:
            analysis = {"raw_analysis": output_text, "parse_error": "Invalid JSON"}

        return analysis

    async def segment_damage(self, image_path: str, prompt: str = "damage") -> dict:
        """
        Use SAM 3.1 to segment damage regions in an image.

        Returns segmentation masks and bounding boxes for damage areas.
        """
        image_url = self._encode_image(image_path)

        response = await self.client.post(
            f"{self.base_url}/responses",
            json={
                "model": Config.SAM_MODEL,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_image", "image_url": image_url},
                            {"type": "input_text", "text": prompt},
                        ],
                    }
                ],
            },
        )
        response.raise_for_status()
        result = response.json()

        # Parse SAM output (boxes and masks)
        output_text = ""
        for item in result.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        output_text = content.get("text", "")

        return self._parse_sam_output(output_text)

    def _parse_sam_output(self, raw_output: str) -> dict:
        """Parse SAM 3.1 output format into structured segmentation data."""
        segments = []
        # SAM returns bounding boxes and masks in a special token format
        # Parse according to Meta's wire grammar
        lines = raw_output.strip().split("\n")
        for line in lines:
            # Try to extract box coordinates
            if "box" in line.lower() or "[" in line:
                try:
                    # Attempt to parse box coordinates
                    nums = [float(x) for x in line.replace("[", "").replace("]", "").replace(",", " ").split() if self._is_number(x)]
                    if len(nums) >= 4:
                        segments.append({
                            "box": {
                                "x1": nums[0],
                                "y1": nums[1],
                                "x2": nums[2],
                                "y2": nums[3],
                            },
                            "confidence": nums[4] if len(nums) > 4 else 0.9,
                        })
                except (ValueError, IndexError):
                    continue

        return {
            "segments": segments,
            "raw_output": raw_output,
            "count": len(segments),
        }

    @staticmethod
    def _is_number(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    async def generate_reconstruction_image(
        self, description: str, style: str = "technical diagram"
    ) -> Optional[str]:
        """
        Use Muse Image to generate a reconstruction visualization.

        Returns the generated image as a base64 string.
        """
        prompt = f"""Generate a technical forensic reconstruction diagram showing: {description}

Style: {style}, clean technical illustration with force vectors, trajectory lines,
and physics annotations. Use a dark background with bright colored overlays.
Professional forensic engineering quality."""

        try:
            response = await self.client.post(
                f"{self.base_url}/responses",
                json={
                    "model": Config.MUSE_IMAGE_MODEL,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                            ],
                        }
                    ],
                },
            )
            response.raise_for_status()
            result = response.json()

            # Extract generated image
            for item in result.get("output", []):
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_image":
                            return content.get("image_url", "")

            return None
        except Exception as e:
            print(f"Image generation failed: {e}")
            return None

    async def deep_reason(self, context: str, question: str) -> str:
        """
        Use Muse Wonder for deep causal reasoning about complex damage scenarios.
        """
        response = await self.client.post(
            f"{self.base_url}/responses",
            json={
                "model": Config.MUSE_WONDER_MODEL,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"""You are a forensic physics expert. Given this context about observed damage:

{context}

Answer this question with deep causal reasoning:
{question}

Be specific, quantitative, and cite relevant physics principles.""",
                            },
                        ],
                    }
                ],
                "reasoning": {"effort": "high"},
            },
        )
        response.raise_for_status()
        result = response.json()

        output_text = ""
        for item in result.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        output_text = content.get("text", "")

        return output_text

    async def close(self):
        await self.client.aclose()
