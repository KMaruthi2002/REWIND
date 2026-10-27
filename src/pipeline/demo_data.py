"""Pre-built realistic demo responses for all Meta AI pipeline stages.

Used when no API key is configured so the full pipeline runs end-to-end
with believable data for UI testing and demo video recording.
"""

# ── Stage 1: SAM 3.1 Segmentation ────────────────────────────────────

DEMO_SEGMENTS = {
    "impact": [
        {
            "label": "primary_fracture_zone",
            "box": {"x1": 0.28, "y1": 0.22, "x2": 0.72, "y2": 0.68},
            "confidence": 0.94,
        },
        {
            "label": "radial_crack_region",
            "box": {"x1": 0.15, "y1": 0.10, "x2": 0.85, "y2": 0.82},
            "confidence": 0.87,
        },
        {
            "label": "secondary_spalling",
            "box": {"x1": 0.38, "y1": 0.55, "x2": 0.62, "y2": 0.78},
            "confidence": 0.79,
        },
    ],
    "tipping": [
        {
            "label": "fallen_object",
            "box": {"x1": 0.20, "y1": 0.35, "x2": 0.80, "y2": 0.90},
            "confidence": 0.96,
        },
        {
            "label": "base_contact_point",
            "box": {"x1": 0.55, "y1": 0.82, "x2": 0.75, "y2": 0.95},
            "confidence": 0.88,
        },
        {
            "label": "debris_scatter",
            "box": {"x1": 0.10, "y1": 0.70, "x2": 0.50, "y2": 0.98},
            "confidence": 0.72,
        },
    ],
    "fluid": [
        {
            "label": "moisture_origin",
            "box": {"x1": 0.25, "y1": 0.08, "x2": 0.45, "y2": 0.25},
            "confidence": 0.91,
        },
        {
            "label": "primary_flow_path",
            "box": {"x1": 0.22, "y1": 0.20, "x2": 0.55, "y2": 0.75},
            "confidence": 0.85,
        },
        {
            "label": "pooling_region",
            "box": {"x1": 0.18, "y1": 0.68, "x2": 0.60, "y2": 0.92},
            "confidence": 0.82,
        },
    ],
}

# ── Stage 2: Muse Spark Analysis ──────────────────────────────────────

DEMO_ANALYSIS = {
    "impact": {
        "damage_description": (
            "High-velocity impact damage consistent with a hard spherical projectile "
            "striking a tempered glass surface at an oblique angle. The fracture pattern "
            "shows a classic Hertzian cone at the point of contact with 11 radial cracks "
            "propagating outward. Secondary concentric ring cracks visible at 4cm and 9cm "
            "from the impact center indicate the energy was sufficient to exceed the "
            "surface compressive stress layer."
        ),
        "physics_analysis": {
            "impact_type": "ballistic_projectile",
            "surface_material": "tempered_glass",
            "energy_transfer": "high",
            "fracture_mechanics": "Hertzian_cone_with_radial_propagation",
        },
        "reconstruction": {
            "narrative": (
                "A hard spherical object approximately 2-3cm in diameter struck the "
                "glass surface at roughly 45 degrees from normal. The projectile was "
                "traveling at an estimated 25-35 m/s, delivering approximately 8-12 "
                "joules of kinetic energy. On contact, a Hertzian cone fracture formed "
                "in under 0.1 milliseconds. Radial cracks then propagated outward at "
                "~1,500 m/s through the tensile stress field on the rear surface. The "
                "crack pattern stabilized within 2 milliseconds of initial contact. "
                "The projectile likely rebounded given the intact central zone."
            ),
            "timeline": [
                {"time": "T-500ms", "event": "Projectile approaching at ~30 m/s, 45-degree trajectory"},
                {"time": "T-0", "event": "Initial contact: Hertzian cone fracture nucleation"},
                {"time": "T+0.05ms", "event": "Cone crack reaches rear surface tensile zone"},
                {"time": "T+0.1ms", "event": "Radial crack initiation from cone boundary"},
                {"time": "T+0.5ms", "event": "11 radial cracks propagating at 1,500 m/s"},
                {"time": "T+1.2ms", "event": "First concentric ring crack forms at 4cm radius"},
                {"time": "T+1.8ms", "event": "Second ring crack at 9cm, energy dissipating"},
                {"time": "T+2.0ms", "event": "Crack propagation arrested, pattern stabilized"},
                {"time": "T+5ms", "event": "Projectile rebounds from surface"},
            ],
        },
        "parameters": {
            "estimated_values": {
                "impact_angle": 45,
                "impact_velocity": 30,
                "projectile_mass": 0.028,
                "projectile_diameter": 2.5,
                "kinetic_energy": 12.6,
                "peak_force": 8400,
                "crack_count": 11,
                "damage_radius": 9,
                "cone_angle": 22,
            },
            "units": {
                "impact_angle": "deg",
                "impact_velocity": "m/s",
                "projectile_mass": "kg",
                "projectile_diameter": "cm",
                "kinetic_energy": "J",
                "peak_force": "N",
                "crack_count": "",
                "damage_radius": "cm",
                "cone_angle": "deg",
            },
            "confidence": "high",
        },
        "visualization_hints": {
            "key_features": ["radial_cracks", "hertzian_cone", "ring_cracks"],
            "suggested_view": "approach_and_impact",
        },
    },
    "tipping": {
        "damage_description": (
            "A tall, narrow bookshelf (~180cm height, ~40cm base width) has toppled "
            "forward. The tipping pattern is consistent with a gradual center-of-mass "
            "shift caused by asymmetric loading on the upper shelves. The base shows "
            "scuff marks indicating the pivot point, and the forward scatter pattern "
            "of objects suggests the shelf accelerated through the final 30 degrees "
            "of its fall."
        ),
        "physics_analysis": {
            "collapse_type": "rotational_tipping",
            "trigger": "center_of_mass_exceeded_base",
            "object_type": "tall_furniture",
            "energy_transfer": "gravitational_potential_to_kinetic",
        },
        "reconstruction": {
            "narrative": (
                "The bookshelf, loaded asymmetrically with heavier items on upper "
                "shelves, had its center of mass elevated to approximately 65% of "
                "its height. A small perturbation (likely contact or vibration) "
                "shifted the center of mass past the tipping threshold. Once the "
                "vertical projection of the center of mass crossed the front edge "
                "of the base, gravitational torque began accelerating the rotation. "
                "The shelf pivoted about its front-bottom edge, reaching an angular "
                "velocity of approximately 3.2 rad/s at ground contact. Total fall "
                "time was approximately 1.1 seconds."
            ),
            "timeline": [
                {"time": "T-2s", "event": "External perturbation shifts center of mass"},
                {"time": "T-1s", "event": "Object begins slow forward lean, CoM approaching base edge"},
                {"time": "T-0", "event": "Tipping point: CoM projection crosses front base edge"},
                {"time": "T+0.2s", "event": "Gravitational torque accelerating rotation, tilt 5 deg"},
                {"time": "T+0.5s", "event": "Objects begin sliding off shelves, tilt 20 deg"},
                {"time": "T+0.8s", "event": "Rapid angular acceleration phase, tilt 50 deg"},
                {"time": "T+1.0s", "event": "Near-horizontal, angular velocity peaks at 3.2 rad/s"},
                {"time": "T+1.1s", "event": "Ground impact, kinetic energy transfers to floor"},
            ],
        },
        "parameters": {
            "estimated_values": {
                "object_height": 180,
                "base_width": 40,
                "estimated_mass": 45,
                "center_of_mass_height": 117,
                "tipping_angle_threshold": 6.3,
                "fall_duration": 1.1,
                "impact_velocity": 5.8,
                "peak_angular_velocity": 3.2,
            },
            "units": {
                "object_height": "cm",
                "base_width": "cm",
                "estimated_mass": "kg",
                "center_of_mass_height": "cm",
                "tipping_angle_threshold": "deg",
                "fall_duration": "s",
                "impact_velocity": "m/s",
                "peak_angular_velocity": "rad/s",
            },
            "confidence": "high",
        },
        "visualization_hints": {
            "key_features": ["center_of_mass_shift", "rotation_acceleration", "debris_scatter"],
            "suggested_view": "side_profile_rotation",
        },
    },
    "fluid": {
        "damage_description": (
            "Water damage pattern on a wall and ceiling junction consistent with a "
            "slow pipe leak above the ceiling line. The staining shows a gravity-driven "
            "flow pattern originating from a point source near the upper-left corner. "
            "Mineral deposits along the flow edges suggest hard water, and the stain "
            "coloration gradient (darker at origin, lighter at edges) indicates the "
            "leak has been active for an extended period, likely 2-4 weeks."
        ),
        "physics_analysis": {
            "flow_type": "gravity_driven_seepage",
            "source": "concealed_pipe_leak",
            "fluid": "municipal_water_supply",
            "wicking_material": "drywall_and_paint",
        },
        "reconstruction": {
            "narrative": (
                "A pinhole leak in a concealed copper pipe fitting above the ceiling "
                "drywall has been releasing water at approximately 15-25 ml per hour. "
                "The water initially saturated the ceiling drywall directly above the "
                "leak point, then gravity drew it downward through the wall cavity. "
                "Capillary action in the gypsum board wicked the moisture laterally, "
                "creating the characteristic fan-shaped stain pattern. The mineral "
                "deposits visible along the flow edges are calcium carbonate from "
                "the hard water supply, deposited as the water evaporates at the "
                "stain boundary. Based on stain area and drying rate analysis, the "
                "leak has been active for approximately 18-25 days."
            ),
            "timeline": [
                {"time": "Day 1", "event": "Pinhole develops in pipe fitting, ~15 ml/hr flow begins"},
                {"time": "Day 2-3", "event": "Ceiling drywall above leak saturates, visible damp spot forms"},
                {"time": "Day 5-7", "event": "Water reaches wall cavity, gravity flow begins downward"},
                {"time": "Day 8-10", "event": "Lateral wicking creates fan pattern, stain diameter ~20cm"},
                {"time": "Day 12-15", "event": "Mineral deposits form along flow edges as water evaporates"},
                {"time": "Day 15-18", "event": "Stain reaches 40cm, paint begins to bubble and peel"},
                {"time": "Day 20-25", "event": "Current state: ~55cm stain with visible flow path and pooling"},
            ],
        },
        "parameters": {
            "estimated_values": {
                "flow_rate": 20,
                "leak_duration_days": 22,
                "total_water_volume": 10.5,
                "stain_diameter": 55,
                "source_height": 245,
                "flow_velocity": 0.3,
                "water_hardness": 180,
                "affected_area": 0.24,
            },
            "units": {
                "flow_rate": "ml/hr",
                "leak_duration_days": "days",
                "total_water_volume": "L",
                "stain_diameter": "cm",
                "source_height": "cm",
                "flow_velocity": "cm/min",
                "water_hardness": "ppm CaCO3",
                "affected_area": "m^2",
            },
            "confidence": "medium",
        },
        "visualization_hints": {
            "key_features": ["source_point", "gravity_flow", "lateral_wicking", "mineral_deposits"],
            "suggested_view": "time_lapse_spread",
        },
    },
}

# ── Stage 3: Muse Wonder Deep Reasoning ───────────────────────────────

DEMO_REASONING = {
    "impact": (
        "## Deep Causal Analysis: Glass Impact Fracture\n\n"
        "### Primary Mechanism\n"
        "The fracture pattern is diagnostic of a **Hertzian contact fracture** in "
        "tempered glass. The key evidence:\n\n"
        "1. **Cone geometry**: The 22-degree half-angle of the cone crack is consistent "
        "with Poisson's ratio of 0.22 for soda-lime glass, confirming the material "
        "identification.\n\n"
        "2. **Radial crack count**: 11 radial cracks suggest the impact energy was "
        "approximately 2.5x the critical threshold for radial crack initiation. Using "
        "Lawn & Marshall's (1979) relation: n ~ (E/H)^(1/2) * (P/P_c), where n is "
        "crack count, E is elastic modulus, H is hardness, and P/P_c is the normalized "
        "load. For tempered glass with E=72 GPa and H=5.5 GPa, 11 cracks corresponds "
        "to P/P_c ~ 2.4.\n\n"
        "3. **Ring crack spacing**: The concentric rings at 4cm and 9cm follow a "
        "geometric progression ratio of ~2.25, consistent with the stress wave "
        "reflection pattern in a 6mm thick tempered glass panel.\n\n"
        "### Projectile Identification\n"
        "The combination of impact parameters (30 m/s, 28g, 2.5cm diameter) is "
        "consistent with a steel ball bearing or a large hailstone (density ~900 "
        "kg/m^3). The intact central zone and rebound trajectory favor a rigid "
        "projectile over ice, which would show more distributed crushing.\n\n"
        "### Confidence Assessment\n"
        "**High confidence** in the reconstruction. The physics are well-constrained "
        "by the fracture pattern. The velocity estimate has an uncertainty of +/- 5 m/s "
        "based on crack spacing analysis. The angle estimate is constrained to +/- 5 "
        "degrees by the asymmetry of the radial crack pattern."
    ),
    "tipping": (
        "## Deep Causal Analysis: Furniture Tipping Event\n\n"
        "### Stability Analysis\n"
        "The critical stability parameter is the ratio of base width to the height "
        "of the center of mass. For this bookshelf:\n\n"
        "- Base width: 40cm\n"
        "- Center of mass height (loaded): 117cm\n"
        "- Stability ratio: 40/117 = 0.34\n\n"
        "A stability ratio below 0.5 indicates marginal stability. At 0.34, the "
        "object requires only a 6.3-degree tilt to pass the tipping threshold.\n\n"
        "### Root Cause Chain\n"
        "1. **Loading asymmetry**: Heavy items placed on upper shelves raised the "
        "center of mass from its unloaded position (~45% height) to 65% height.\n"
        "2. **Base friction**: The scuff marks suggest rubber or felt pads on a smooth "
        "floor, providing ~0.4 coefficient of friction, insufficient to resist the "
        "overturning moment once initiated.\n"
        "3. **Trigger event**: The perturbation energy needed is only ~2.3 J, which "
        "could come from leaning against the shelf, a pet jumping on it, seismic "
        "microtremor, or even slamming a nearby door.\n\n"
        "### Energy Budget\n"
        "Total gravitational potential energy converted: mgh = 45 * 9.81 * 0.9 = "
        "397 J. Of this, approximately 60% was absorbed by the impact deformation, "
        "25% by object scatter, and 15% by acoustic emission.\n\n"
        "### Prevention Note\n"
        "Wall anchoring with a single L-bracket at 150cm height would have provided "
        "a restraining moment of ~180 Nm, far exceeding the tipping moment of ~26 Nm "
        "at the threshold angle."
    ),
    "fluid": (
        "## Deep Causal Analysis: Concealed Water Leak\n\n"
        "### Flow Physics\n"
        "The stain pattern reveals two distinct transport mechanisms:\n\n"
        "1. **Gravity-driven film flow**: The primary vertical flow path shows a "
        "width consistent with a thin film (~0.1mm) flowing at Reynolds number < 1 "
        "(fully laminar). Using the Nusselt film thickness equation for the observed "
        "flow rate of ~20 ml/hr on a vertical surface: delta = (3*mu*Q / (rho*g*W))^(1/3) "
        "= 0.12mm, consistent with observation.\n\n"
        "2. **Capillary wicking**: The lateral spread in the gypsum board follows "
        "Washburn's equation: L^2 = (gamma*r*cos(theta)*t) / (2*mu). The observed "
        "lateral spread of ~27.5cm over 22 days gives an effective pore radius of "
        "~15 micrometers, consistent with Type X drywall.\n\n"
        "### Leak Source Identification\n"
        "The point-source geometry and steady flow rate point to a fitting failure "
        "rather than a pipe crack. Common causes at this flow rate:\n"
        "- Compression fitting that has loosened over thermal cycling (most likely)\n"
        "- Solder joint with a pinhole from flux corrosion\n"
        "- Thread seal failure on a brass fitting\n\n"
        "### Damage Progression Forecast\n"
        "Without intervention, the leak will:\n"
        "- Day 30: Saturate the wall cavity insulation, increasing thermal losses\n"
        "- Day 45: Mold colonization becomes likely (moisture > 60% RH sustained)\n"
        "- Day 60-90: Structural damage to wall framing begins\n\n"
        "### Confidence Assessment\n"
        "**Medium confidence** overall. The flow rate and duration estimates have "
        "wider uncertainty (+/- 30%) because they depend on the drywall's specific "
        "porosity and the ambient humidity, which affect evaporation rate."
    ),
}

# ── Physics Simulation Parameters (for physics_sim.py) ────────────────

DEMO_SIM_PARAMS = {
    "impact": {
        "impact_angle_deg": 45,
        "impact_velocity_mps": 30,
        "impactor_mass_kg": 0.028,
        "impact_point": {"x": 0.48, "y": 0.42},
        "surface_type": "glass",
    },
    "tipping": {
        "object_height": 0.45,
        "object_width": 0.12,
        "center_of_mass": {"x": 0.50, "y": 0.45},
        "tipping_direction": 90,
        "initial_disturbance": "asymmetric_loading",
    },
    "fluid": {
        "source_point": {"x": 0.30, "y": 0.12},
        "flow_direction": 200,
        "flow_rate": 0.4,
        "spread_factor": 0.35,
        "duration_hours": 528,
    },
}
