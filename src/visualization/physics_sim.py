"""Physics simulation engine for generating reconstruction animations.

Takes the parameters extracted by Muse Spark and runs forward/reverse
physics simulations to visualize what happened.
"""

import math
import json
import random
from dataclasses import dataclass, field


@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def to_dict(self):
        return {"x": self.x, "y": self.y}


@dataclass
class SimFrame:
    """A single frame of the reconstruction animation."""
    time: float  # seconds
    objects: list = field(default_factory=list)  # list of object states
    annotations: list = field(default_factory=list)  # text annotations
    vectors: list = field(default_factory=list)  # force/velocity vectors
    highlights: list = field(default_factory=list)  # regions to highlight

    def to_dict(self):
        return {
            "time": round(self.time, 3),
            "objects": self.objects,
            "annotations": self.annotations,
            "vectors": self.vectors,
            "highlights": self.highlights,
        }


class ImpactSimulator:
    """Simulates projectile impact events (cracks, dents, glass breaks)."""

    def simulate(self, params: dict, duration: float = 2.0, fps: int = 30) -> list[dict]:
        """Generate animation frames for an impact reconstruction.

        params should include:
        - impact_angle_deg: angle of impact in degrees
        - impact_velocity_mps: velocity at impact in m/s
        - impactor_mass_kg: mass of the impactor
        - impact_point: {x, y} normalized coordinates of impact point
        - surface_type: "glass", "metal", "wood", etc.
        """
        frames = []
        num_frames = int(duration * fps)

        angle_deg = params.get("impact_angle_deg", 45)
        velocity = params.get("impact_velocity_mps", 15)
        mass = params.get("impactor_mass_kg", 0.1)
        impact_point = params.get("impact_point", {"x": 0.5, "y": 0.5})
        surface_type = params.get("surface_type", "glass")

        angle_rad = math.radians(angle_deg)
        vx = velocity * math.cos(angle_rad)
        vy = velocity * math.sin(angle_rad)
        force = mass * velocity  # impulse approximation

        # Pre-impact phase (projectile approaching)
        pre_impact_frames = num_frames // 3
        for i in range(pre_impact_frames):
            t = (i / pre_impact_frames) * 0.5  # 0 to 0.5 seconds pre-impact
            progress = i / pre_impact_frames

            # Projectile position (approaching from angle)
            proj_x = impact_point["x"] - (1 - progress) * 0.3 * math.cos(angle_rad)
            proj_y = impact_point["y"] - (1 - progress) * 0.3 * math.sin(angle_rad)

            frame = SimFrame(
                time=-0.5 + t,
                objects=[{
                    "type": "projectile",
                    "x": proj_x,
                    "y": proj_y,
                    "radius": 0.015,
                    "color": "#ff6b35",
                }],
                vectors=[{
                    "type": "velocity",
                    "origin": {"x": proj_x, "y": proj_y},
                    "direction": {"x": vx / velocity, "y": vy / velocity},
                    "magnitude": velocity,
                    "color": "#00d4ff",
                    "label": f"{velocity:.1f} m/s",
                }],
                annotations=[{
                    "text": f"v = {velocity:.1f} m/s",
                    "position": {"x": 0.05, "y": 0.05},
                    "color": "#00d4ff",
                }],
            )
            frames.append(frame.to_dict())

        # Impact moment
        impact_frame = SimFrame(
            time=0,
            objects=[{
                "type": "impact_flash",
                "x": impact_point["x"],
                "y": impact_point["y"],
                "radius": 0.05,
                "color": "#ffffff",
            }],
            vectors=[{
                "type": "force",
                "origin": impact_point,
                "direction": {"x": math.cos(angle_rad), "y": math.sin(angle_rad)},
                "magnitude": force,
                "color": "#ff0040",
                "label": f"F = {force:.1f} N",
            }],
            annotations=[
                {"text": "IMPACT", "position": impact_point, "color": "#ff0040", "size": "large"},
                {"text": f"F = {force:.1f} N", "position": {"x": 0.05, "y": 0.1}, "color": "#ff0040"},
                {"text": f"angle = {angle_deg:.0f} deg", "position": {"x": 0.05, "y": 0.15}, "color": "#ffaa00"},
            ],
            highlights=[{
                "type": "radial",
                "center": impact_point,
                "radius": 0.08,
                "color": "rgba(255, 0, 64, 0.3)",
            }],
        )
        frames.append(impact_frame.to_dict())

        # Post-impact phase (damage propagation)
        post_frames = num_frames - pre_impact_frames - 1
        for i in range(post_frames):
            t = i / post_frames  # 0 to 1 progress
            time_s = t * 1.0  # 1 second post-impact

            # Crack propagation (radial from impact point)
            crack_radius = t * 0.25  # grows over time
            num_cracks = self._get_crack_count(surface_type)

            crack_lines = []
            for c in range(num_cracks):
                crack_angle = (c / num_cracks) * 2 * math.pi + (angle_rad * 0.3)
                end_x = impact_point["x"] + crack_radius * math.cos(crack_angle)
                end_y = impact_point["y"] + crack_radius * math.sin(crack_angle)
                crack_lines.append({
                    "type": "crack",
                    "start": impact_point,
                    "end": {"x": end_x, "y": end_y},
                    "color": "#ff6b35",
                    "width": max(1, 3 - t * 2),
                })

            frame = SimFrame(
                time=time_s,
                objects=crack_lines,
                annotations=[
                    {"text": f"Crack propagation: {crack_radius * 100:.0f}cm", "position": {"x": 0.05, "y": 0.05}, "color": "#ff6b35"},
                    {"text": f"Energy dissipated: {t * 100:.0f}%", "position": {"x": 0.05, "y": 0.1}, "color": "#ffaa00"},
                ],
                highlights=[{
                    "type": "radial",
                    "center": impact_point,
                    "radius": crack_radius,
                    "color": f"rgba(255, 107, 53, {0.3 * (1 - t)})",
                }],
            )
            frames.append(frame.to_dict())

        return frames

    def _get_crack_count(self, surface_type: str) -> int:
        counts = {
            "glass": 12,
            "windshield": 8,
            "ceramic": 6,
            "metal": 3,
            "wood": 2,
            "plastic": 4,
            "concrete": 5,
        }
        return counts.get(surface_type, 6)


class TippingSimulator:
    """Simulates tipping and collapse events."""

    def simulate(self, params: dict, duration: float = 3.0, fps: int = 30) -> list[dict]:
        """Generate animation frames for a tipping reconstruction.

        params should include:
        - object_height: height of object (normalized)
        - object_width: width of base (normalized)
        - center_of_mass: {x, y} center of mass position
        - tipping_direction: angle in degrees
        - initial_disturbance: what caused the tipping
        """
        frames = []
        num_frames = int(duration * fps)

        height = params.get("object_height", 0.4)
        width = params.get("object_width", 0.15)
        com = params.get("center_of_mass", {"x": 0.5, "y": 0.5})
        tip_dir = params.get("tipping_direction", 90)
        g = 9.81

        tip_rad = math.radians(tip_dir)

        # Phase 1: Stable state (first third)
        stable_frames = num_frames // 4
        for i in range(stable_frames):
            t = i / num_frames * duration

            frame = SimFrame(
                time=t,
                objects=[{
                    "type": "rectangle",
                    "x": com["x"] - width / 2,
                    "y": com["y"] - height,
                    "width": width,
                    "height": height,
                    "rotation": 0,
                    "color": "#4a9eff",
                }],
                vectors=[{
                    "type": "gravity",
                    "origin": com,
                    "direction": {"x": 0, "y": 1},
                    "magnitude": g,
                    "color": "#00ff88",
                    "label": "mg",
                }],
                annotations=[
                    {"text": "Stable", "position": {"x": 0.05, "y": 0.05}, "color": "#00ff88"},
                    {"text": "CoM within base", "position": {"x": 0.05, "y": 0.1}, "color": "#4a9eff"},
                ],
                highlights=[{
                    "type": "point",
                    "position": com,
                    "color": "#ff0040",
                    "label": "CoM",
                }],
            )
            frames.append(frame.to_dict())

        # Phase 2: Disturbance and tipping
        tip_frames = num_frames - stable_frames
        for i in range(tip_frames):
            progress = i / tip_frames
            t = (stable_frames + i) / num_frames * duration

            # Angular acceleration due to gravity torque
            # theta = 0.5 * alpha * t^2, simplified tipping
            max_angle = 90
            angle = progress ** 2 * max_angle  # accelerating rotation

            angle_rad_current = math.radians(angle)

            # Rotate the object around its base pivot
            pivot_x = com["x"] + (width / 2) * math.cos(tip_rad)
            pivot_y = com["y"]

            # New center of mass position
            new_com_x = pivot_x + (height / 2) * math.sin(angle_rad_current) * math.cos(tip_rad)
            new_com_y = com["y"] - (height / 2) * math.cos(angle_rad_current) + (height / 2)

            # Color transitions from blue to red as instability increases
            r = min(255, int(progress * 255))
            g_color = max(0, int((1 - progress) * 150))
            b = max(0, int((1 - progress) * 255))

            stability = "CRITICAL" if progress > 0.5 else "Unstable"
            stab_color = "#ff0040" if progress > 0.5 else "#ffaa00"

            frame = SimFrame(
                time=t,
                objects=[{
                    "type": "rectangle",
                    "x": com["x"] - width / 2,
                    "y": com["y"] - height,
                    "width": width,
                    "height": height,
                    "rotation": angle * (1 if tip_dir >= 0 else -1),
                    "pivot": {"x": pivot_x, "y": pivot_y},
                    "color": f"rgb({r}, {g_color}, {b})",
                }],
                vectors=[
                    {
                        "type": "gravity",
                        "origin": {"x": new_com_x, "y": new_com_y},
                        "direction": {"x": 0, "y": 1},
                        "magnitude": 9.81,
                        "color": "#00ff88",
                        "label": "mg",
                    },
                    {
                        "type": "torque",
                        "origin": {"x": pivot_x, "y": pivot_y},
                        "direction": {"x": math.cos(tip_rad), "y": 0},
                        "magnitude": progress * 50,
                        "color": "#ff6b35",
                        "label": f"torque",
                    },
                ],
                annotations=[
                    {"text": stability, "position": {"x": 0.05, "y": 0.05}, "color": stab_color},
                    {"text": f"Tilt: {angle:.1f} deg", "position": {"x": 0.05, "y": 0.1}, "color": "#ffaa00"},
                    {"text": f"CoM offset: {progress * width * 100:.1f}cm", "position": {"x": 0.05, "y": 0.15}, "color": "#ff6b35"},
                ],
                highlights=[{
                    "type": "point",
                    "position": {"x": new_com_x, "y": new_com_y},
                    "color": stab_color,
                    "label": "CoM",
                }],
            )
            frames.append(frame.to_dict())

        return frames


class FluidSimulator:
    """Simulates fluid flow events (leaks, spills)."""

    def simulate(self, params: dict, duration: float = 4.0, fps: int = 30) -> list[dict]:
        """Generate animation frames for a fluid trace reconstruction.

        params should include:
        - source_point: {x, y} origin of the fluid
        - flow_direction: primary flow direction in degrees
        - flow_rate: relative flow rate (0-1)
        - spread_factor: how much the fluid spreads
        - duration_hours: how long the leak has been active
        """
        frames = []
        num_frames = int(duration * fps)

        source = params.get("source_point", {"x": 0.3, "y": 0.2})
        flow_dir = params.get("flow_direction", 180)  # degrees, 180 = downward
        flow_rate = params.get("flow_rate", 0.5)
        spread = params.get("spread_factor", 0.3)
        leak_hours = params.get("duration_hours", 24)

        flow_rad = math.radians(flow_dir)

        particles = []

        for i in range(num_frames):
            t = i / num_frames * duration
            progress = i / num_frames

            # Add new particles at the source
            if i % 3 == 0:  # new particle every 3 frames
                particles.append({
                    "x": source["x"] + (random.random() - 0.5) * 0.02,
                    "y": source["y"],
                    "vx": math.cos(flow_rad) * flow_rate * 0.01,
                    "vy": math.sin(flow_rad) * flow_rate * 0.01 + 0.005,  # gravity
                    "age": 0,
                })

            # Update particles
            active_particles = []
            for p in particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.0002  # gravity acceleration
                p["vx"] *= 0.99  # friction
                p["age"] += 1

                # Spread over time
                if p["age"] % 10 == 0:
                    p["vx"] += (0.5 - (hash(str(p["age"])) % 100) / 100) * spread * 0.002

                if p["age"] < 120 and 0 <= p["x"] <= 1 and 0 <= p["y"] <= 1:
                    active_particles.append(p)

            particles = active_particles

            # Build particle objects for this frame
            particle_objects = []
            for p in particles:
                opacity = max(0.2, 1 - p["age"] / 120)
                particle_objects.append({
                    "type": "particle",
                    "x": p["x"],
                    "y": p["y"],
                    "radius": 0.005 + p["age"] * 0.0001,
                    "color": f"rgba(64, 164, 255, {opacity})",
                })

            # Flow path highlight
            flow_extent = progress * 0.4
            flow_end_x = source["x"] + flow_extent * math.cos(flow_rad)
            flow_end_y = source["y"] + flow_extent * math.sin(flow_rad) + flow_extent * 0.3

            frame = SimFrame(
                time=t,
                objects=[
                    {
                        "type": "source_marker",
                        "x": source["x"],
                        "y": source["y"],
                        "radius": 0.02,
                        "color": "#ff0040",
                        "pulse": True,
                    },
                    *particle_objects[:50],  # limit particles for performance
                ],
                vectors=[{
                    "type": "flow",
                    "origin": source,
                    "direction": {"x": math.cos(flow_rad), "y": math.sin(flow_rad)},
                    "magnitude": flow_rate,
                    "color": "#40a4ff",
                    "label": "flow",
                }],
                annotations=[
                    {"text": f"Source: ({source['x']:.2f}, {source['y']:.2f})", "position": {"x": 0.05, "y": 0.05}, "color": "#ff0040"},
                    {"text": f"Flow rate: {flow_rate * 100:.0f}%", "position": {"x": 0.05, "y": 0.1}, "color": "#40a4ff"},
                    {"text": f"Duration: ~{leak_hours:.0f}h", "position": {"x": 0.05, "y": 0.15}, "color": "#ffaa00"},
                    {"text": f"Spread: {flow_extent * 100:.0f}cm", "position": {"x": 0.05, "y": 0.2}, "color": "#40a4ff"},
                ],
                highlights=[{
                    "type": "flow_path",
                    "start": source,
                    "end": {"x": flow_end_x, "y": flow_end_y},
                    "width": spread * 0.1 + progress * 0.05,
                    "color": "rgba(64, 164, 255, 0.15)",
                }],
            )
            frames.append(frame.to_dict())

        return frames


def get_simulator(damage_type: str):
    """Factory function to get the appropriate simulator."""
    simulators = {
        "impact": ImpactSimulator(),
        "tipping": TippingSimulator(),
        "fluid": FluidSimulator(),
    }
    return simulators.get(damage_type, ImpactSimulator())
