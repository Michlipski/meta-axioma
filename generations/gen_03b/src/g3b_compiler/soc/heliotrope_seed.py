"""Tier 1 Situation of Concern & Universal IR Seed Specification for `axioma_heliotrope`.

Axioma Heliotrope: Heliotropic Microclimate & Solar Shadow Choreographer Studio
Canonical Application ID: axioma_heliotrope
SoC ID: soc_heliotropic_microclimate_studio
Primary Persona: Elena, The Permaculture Designer & Heliotropic Landscaper

Governing Axioms:
- [L1-G3B-000] Waterloo Situation of Concern Normalization: Macro, Meso, Micro decomposition
- [L1-G3B-011] Universal Compositional Contract IR: Typed nouns, algebraic invariants, inductive proofs
- [L1-002] Functorial Reversibility: 1-tap Functorial Undo via Deep History restoration
"""

from typing import Dict, Any, List

from .models import (
    SituationOfConcern,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)
from .normalizer import SoCNormalizer
from ..ir.contract_ir import (
    ContractIR,
    DomainNoun,
    DomainVerb,
    FieldDef,
    ComposedVerb,
    VerbCompositionStep,
)
from ..ir.statechart_ir import (
    StatechartIR,
    StateNode,
    StateNodeType,
    Transition,
    HistoryType,
)
from ..ir.topology_ir import (
    TopologyIR,
    TopologyNode,
    NodeRole,
    NetworkChannel,
    ChannelType,
    ConsensusContract,
    ConsensusProtocol,
)


SOC_ID_HELIOTROPE = "soc_heliotropic_microclimate_studio"

REQUIRED_INVARIANTS_HELIOTROPE: List[str] = [
    "parcel_width_m == 30.0",
    "parcel_length_m == 20.0",
    "grid_resolution_m == 1.0",
    "total_cells_count == 600",
    "solar_altitude_deg >= -90.0",
    "solar_altitude_deg <= 90.0",
    "solar_azimuth_deg >= 0.0",
    "solar_azimuth_deg < 360.0",
    "shadow_length >= 0.0",
    "direct_sun_hours >= 0.0",
    "direct_sun_hours <= 24.0",
    "suitability_score >= 0.0",
    "suitability_score <= 1.0",
    "undo_stack_depth >= 0",
]


def build_heliotrope_soc() -> SituationOfConcern:
    """Constructs and normalizes the Tier 1 Situation of Concern for `axioma_heliotrope`."""
    macro_soc = SituationOfConcern(
        soc_id=SOC_ID_HELIOTROPE,
        title="Axioma Heliotrope: Heliotropic Microclimate & Solar Shadow Choreographer Studio",
        narrative=(
            "Urban permaculture designers, regenerative landscapers, and residential homesteaders struggle "
            "with spatial-temporal shadow occlusion on complex residential properties. Standard 2D landscape "
            "drafting tools ignore 4D seasonal solar ephemeris, while heavy 3D architectural CAD packages impose "
            "prohibitive cognitive overhead, steep learning curves, and dozens of non-intuitive clicks before "
            "answering basic permaculture questions (e.g., 'Will this raised vegetable bed receive >= 6 hours "
            "of direct sunlight during the shoulder seasons?'). Elena, designing a 30m x 20m residential parcel "
            "in Portland, OR (lat: 45.5152° N, lon: -122.6784° W) containing a 2-story home (12x8m, height 7m, "
            "gable 9m), a detached garage (6x6m, height 3.5m), a mature conical cedar tree (radius 2m, height 8m), "
            "and a 1.8m perimeter fence, requires instant real-time solar raytracing across Solstices and Equinoxes, "
            "a 1m^2 cumulative insolation heatmap (600 discrete cells), rapid zonal asset microclimate evaluation "
            "(raised bed, gazebo, tanning spot), and a 1-tap Functorial Undo ([L1-002]) with Steps-to-Value <= 3."
        ),
        altitude=SoCAltitude.MACRO,
        actors=[
            Actor(
                name="Elena",
                role="Permaculture Designer & Heliotropic Landscaper (Primary Persona)",
                motivations=[
                    "Design high-yield, resilient edible permaculture guilds matched to microclimate sun hours",
                    "Determine exact shadow cast by residential structures across Summer Solstice, Winter Solstice, and Equinoxes",
                    "Rapidly place garden assets (raised beds >=6h sun, shade gazebos <=4h sun, tanning spots) with instant visual feedback",
                    "Maintain creative flow with 1-tap Functorial Undo without losing layout state",
                    "Achieve high-value design decisions in <= 3 interactive steps without CAD software bloat",
                ],
                frustrations=[
                    "Static 2D plans hide seasonal shadow occlusions, causing client vegetable beds to fail in autumn/spring",
                    "Heavy 3D CAD suites (Sketchup, Revit, Blender) require steep learning curves, slow raytrace rendering, and >15 clicks per study",
                    "Accidental object placement or destructive edits without seamless functorial rollback force tedious redesign",
                    "Lack of discrete 1m^2 cumulative insolation heatmaps for quantitative sun-hour verification",
                ],
            ),
            Actor(
                name="The Sun Vector (Natural Deterministic Ephemeris)",
                role="Astronomical Kinematics Source (NOAA Algorithm)",
                motivations=[
                    "Cast physical shadows governed strictly by spherical trigonometry, solar declination, hour angle, and atmospheric refraction",
                    "Vary peak solar elevation from 21.0 deg (Winter Solstice noon) to 68.0 deg (Summer Solstice noon) in Portland, OR",
                    "Cast elongated winter shadows exceeding 18m from a 7m house wall, drastically compressing southern yard insolation",
                ],
                frustrations=[
                    "Oversimplified flat-earth software models that treat solar angles as static or homogeneous",
                ],
            ),
            Actor(
                name="Residential Client / Homeowner",
                role="Permaculture Beneficiary & Stakeholder",
                motivations=[
                    "Maximize seasonal harvest of sun-loving vegetables (tomatoes, peppers requiring >= 6-8 hrs direct sun)",
                    "Enjoy comfortable afternoon shade in outdoor seating/gazebo areas during July-August heatwaves",
                    "Verify return on landscaping investment before breaking ground on excavation and hardscaping",
                ],
                frustrations=[
                    "Disappointment when expensive raised beds end up permanently shadowed by garage or cedar tree",
                ],
            ),
        ],
        frictions=[
            Friction(
                description="Spatial-temporal shadow blindspots: 2D designs place sun-dependent assets in chronic shadow zones",
                severity=FrictionSeverity.CRITICAL,
                impact="Stunted crop yields, mold-prone outdoor living areas, and costly post-planting relocation of permanent hardscaping",
                trigger_conditions=["Winter and shoulder season sun angles drop below 35 degrees, casting shadows across 65% of the parcel"],
            ),
            Friction(
                description="CAD cognitive overhead and workflow friction: Existing raytracing tools require >15 steps to value",
                severity=FrictionSeverity.HIGH,
                impact="Forces landscape designers to guess solar hours rather than running quantitative raytrace simulations",
                trigger_conditions=["Importing CAD models, setting up lighting rigs, configuring ray bounces, and waiting minutes for offline render"],
            ),
            Friction(
                description="Destructive asset placement without instant reversibility (violates [L1-002])",
                severity=FrictionSeverity.HIGH,
                impact="Exploratory placement of garden assets cannot be effortlessly unwound, discouraging design experimentation",
                trigger_conditions=["Accidental placement, invalid microclimate drop, or comparative alternate layout exploration"],
            ),
            Friction(
                description="Thermal disparity between summer scorch and winter freeze across microclimates",
                severity=FrictionSeverity.MEDIUM,
                impact="Heat-sensitive plants scorched near south-facing garage wall; frost pockets trapped in north-fence dead zones",
                trigger_conditions=["Extreme solstice temperature and radiation differentials"],
            ),
        ],
        constraints=[
            EnvironmentalConstraint(
                nature=ConstraintType.THERMODYNAMIC,
                description="Conservation of solar radiant flux: cumulative solar insolation per 1m^2 cell is strictly bounded by integral of direct ray exposure over solar day (0.0 <= sun_hours <= 24.0)",
                boundary_limit="0.0 <= sun_hours <= 24.0; Max daylight Portland Summer Solstice ~15.7h, Winter Solstice ~8.7h",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description="Physical spatial boundaries: parcel is strictly 30m width (E-W) by 20m length (N-S); obstacles (house, garage, tree, fence) must maintain non-negative coordinates inside parcel",
                boundary_limit="0 <= x <= 30m, 0 <= y <= 20m; obstacle height >= 0.0m",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.REGULATORY,
                description="NOAA Astronomical Kinematics: solar azimuth in [0, 360), solar elevation in [-90, 90] derived from Portland, OR coordinates (45.5152 deg N, -122.6784 deg W)",
                boundary_limit="lat=45.5152, lon=-122.6784; declination in [-23.45, 23.45]",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.ERGONOMIC,
                description="Waterloo Human Ergonomics Invariant: Steps-to-Value <= 3 (1. Select parcel preset -> 2. Run solar seasonal sweep -> 3. Drop asset & inspect microclimate score)",
                boundary_limit="Interactive Steps-to-Value <= 3; 1-tap Functorial Undo latency < 50ms",
            ),
        ],
        unmet_needs=[
            "Instant real-time geometric shadow projection across 30m x 20m parcel with multiple obstacle types (gable house, garage, conical tree, perimeter fence)",
            "Quantitative 1m^2 cumulative insolation heatmap (600 discrete cells) displaying total hours of direct sunlight across Solstices and Equinoxes",
            "Automatic zonal suitability scoring for garden assets (raised bed, gazebo, tanning spot) with occlusion conflict warnings",
            "1-tap Functorial Undo ([L1-002]) leveraging XState v5 Deep History restoration to reversibly explore design alternatives",
            "Ultra-lightweight, zero-bloat browser studio executing in <= 3 steps without CAD plugins or cloud dependencies",
        ],
    )

    SoCNormalizer.normalize_tier1(macro_soc)

    # Meso Level: Solar Raytracing & Heatmap Integration Subsystem
    meso_specs = [
        {
            "soc_id": "soc_meso_solar_raytracing_and_insolation_engine",
            "title": "Subsystem: Solar Kinematics Raytracing & 600m^2 Insolation Heatmap Engine",
            "narrative": "Discrete 1m^2 spatial grid integration calculating line-of-sight ray intersections between solar vector and 3D obstacle bounding volumes across daylight hours.",
            "frictions": [
                Friction(
                    description="Computational latency of real-time ray-polygon intersection across 600 cells over 96 daily time-steps",
                    severity=FrictionSeverity.HIGH,
                    impact="Frame drop or sluggish UI during solar scrubber slider manipulation",
                    trigger_conditions=["Continuous user scrubbing through daylight hours or seasonal transitions"],
                ).to_dict()
            ],
            "unmet_needs": ["Optimized 2.5D polygon shadow projection and vectorized NumPy/TypedArray cumulative integration executing in < 16ms"],
        }
    ]
    SoCNormalizer.decompose_fractal(macro_soc, meso_specs)

    # Micro Level: Permaculture Asset Microclimate Qualification & Functorial Undo
    micro_specs = [
        {
            "soc_id": "soc_micro_asset_qualification_and_undo",
            "title": "Interaction: Zonal Microclimate Qualification & 1-Tap Functorial Undo",
            "narrative": "Interactive drag-and-drop placement of permaculture assets with instantaneous microclimate suitability checks, threshold alerts, and functorial state rollback.",
            "frictions": [
                Friction(
                    description="Ambiguity in plant microclimate requirements and cognitive dissonance upon occluded placement",
                    severity=FrictionSeverity.MEDIUM,
                    impact="Designer unsure whether 5.8 hours is acceptable for full-sun vegetable cultivars",
                    trigger_conditions=["Dropping asset on shadow boundary edge"],
                ).to_dict()
            ],
            "unmet_needs": ["Visual status pill (OPTIMAL, SUBOPTIMAL, OCCLUDED) with explicit sun-hour delta and 1-tap undo keybinding"],
        }
    ]
    SoCNormalizer.decompose_fractal(macro_soc.sub_socs[0], micro_specs)

    return macro_soc


def build_heliotrope_contract_ir() -> ContractIR:
    """Constructs the Universal Compositional ContractIR for `axioma_heliotrope`."""
    nouns = {
        "ParcelLayout": DomainNoun(
            name="ParcelLayout",
            description="30m x 20m residential parcel boundary in Portland OR with 1m^2 grid resolution",
            fields=[
                FieldDef("parcel_id", "str", False, "Unique parcel identifier"),
                FieldDef("width_m", "float", False, "Parcel width along X-axis (30.0m)"),
                FieldDef("length_m", "float", False, "Parcel length along Y-axis (20.0m)"),
                FieldDef("grid_resolution_m", "float", False, "Heatmap cell resolution (1.0m)"),
                FieldDef("latitude", "float", False, "Geolocation latitude (45.5152 deg N)"),
                FieldDef("longitude", "float", False, "Geolocation longitude (-122.6784 deg W)"),
                FieldDef("north_azimuth_offset_deg", "float", False, "Orientation offset relative to true North (0.0 to 360.0)"),
            ],
            invariants=[
                "width_m == 30.0",
                "length_m == 20.0",
                "grid_resolution_m == 1.0",
                "latitude >= -90.0",
                "latitude <= 90.0",
                "longitude >= -180.0",
                "longitude <= 180.0",
            ],
        ),
        "PhysicalObstacle": DomainNoun(
            name="PhysicalObstacle",
            description="Physical structure or canopy casting shadows: house, garage, tree, perimeter fence",
            fields=[
                FieldDef("obstacle_id", "str", False, "Unique obstacle ID"),
                FieldDef("obstacle_type", "str", False, "HOUSE, GARAGE, TREE, FENCE"),
                FieldDef("origin_x", "float", False, "X-coordinate of origin in meters (0 to 30)"),
                FieldDef("origin_y", "float", False, "Y-coordinate of origin in meters (0 to 20)"),
                FieldDef("width_m", "float", False, "Bounding box width in meters"),
                FieldDef("length_m", "float", False, "Bounding box length in meters"),
                FieldDef("height_m", "float", False, "Base eave or wall height in meters"),
                FieldDef("roof_ridge_height_m", "float", False, "Peak roof ridge or tree apex height in meters"),
                FieldDef("canopy_radius_m", "float", False, "Radius for conical canopy (cedar tree)"),
            ],
            invariants=[
                "origin_x >= 0.0",
                "origin_x <= 30.0",
                "origin_y >= 0.0",
                "origin_y <= 20.0",
                "height_m >= 0.0",
                "canopy_radius_m >= 0.0",
            ],
        ),
        "SolarPosition": DomainNoun(
            name="SolarPosition",
            description="Astronomical NOAA solar kinematics vector for Portland OR",
            fields=[
                FieldDef("solar_timestamp", "str", False, "ISO-8601 simulation timestamp"),
                FieldDef("day_of_year", "int", False, "Day of year (1 to 365)"),
                FieldDef("solar_hour", "float", False, "Solar hour (0.0 to 24.0)"),
                FieldDef("declination_deg", "float", False, "Solar declination (-23.45 to +23.45)"),
                FieldDef("hour_angle_deg", "float", False, "Hour angle relative to solar noon (-180 to 180)"),
                FieldDef("solar_azimuth_deg", "float", False, "Azimuth angle (0.0 to 360.0 clockwise from North)"),
                FieldDef("solar_altitude_deg", "float", False, "Solar elevation above horizon (-90.0 to 90.0)"),
                FieldDef("is_sun_above_horizon", "bool", False, "True if solar_altitude_deg > 0.0"),
            ],
            invariants=[
                "solar_azimuth_deg >= 0.0",
                "solar_azimuth_deg < 360.0",
                "solar_altitude_deg >= -90.0",
                "solar_altitude_deg <= 90.0",
                "day_of_year >= 1",
                "day_of_year <= 366",
            ],
        ),
        "InsolationGridCell": DomainNoun(
            name="InsolationGridCell",
            description="1m^2 discrete spatial cell tracking cumulative direct sun hours across seasonal sweep",
            fields=[
                FieldDef("cell_x", "int", False, "Discrete X coordinate (0 to 29)"),
                FieldDef("cell_y", "int", False, "Discrete Y coordinate (0 to 19)"),
                FieldDef("direct_sun_hours", "float", False, "Cumulative direct sun hours in day (0.0 to 24.0)"),
                FieldDef("diffuse_insolation_kwh", "float", False, "Estimated solar irradiance in kWh/m^2"),
                FieldDef("is_occluded_at_peak", "bool", False, "True if occluded during solar noon window (11:00-13:00)"),
                FieldDef("primary_shadow_caster_id", "str", True, "ID of obstacle causing longest occlusion"),
            ],
            invariants=[
                "cell_x >= 0",
                "cell_x < 30",
                "cell_y >= 0",
                "cell_y < 20",
                "direct_sun_hours >= 0.0",
                "direct_sun_hours <= 24.0",
                "diffuse_insolation_kwh >= 0.0",
            ],
        ),
        "GardenAssetPlacement": DomainNoun(
            name="GardenAssetPlacement",
            description="Placed permaculture or recreational asset evaluated against solar microclimate",
            fields=[
                FieldDef("asset_id", "str", False, "Unique asset placement ID"),
                FieldDef("asset_type", "str", False, "RAISED_BED, GAZEBO, TANNING_SPOT"),
                FieldDef("pos_x", "float", False, "Target X coordinate (0.0 to 30.0)"),
                FieldDef("pos_y", "float", False, "Target Y coordinate (0.0 to 20.0)"),
                FieldDef("min_sun_hours_required", "float", False, "Minimum sun hours for viability (e.g. 6.0 for edible bed)"),
                FieldDef("max_sun_hours_tolerated", "float", False, "Maximum sun hours tolerated (e.g. 4.0 for shade gazebo)"),
                FieldDef("actual_sun_hours", "float", False, "Interpolated solar hours from insolation grid"),
                FieldDef("suitability_score", "float", False, "Normalized microclimate fitness score (0.0 to 1.0)"),
                FieldDef("is_valid_microclimate", "bool", False, "True if microclimate satisfies asset constraints"),
            ],
            invariants=[
                "pos_x >= 0.0",
                "pos_x <= 30.0",
                "pos_y >= 0.0",
                "pos_y <= 20.0",
                "suitability_score >= 0.0",
                "suitability_score <= 1.0",
                "actual_sun_hours >= 0.0",
                "actual_sun_hours <= 24.0",
            ],
        ),
        "HeliotropicState": DomainNoun(
            name="HeliotropicState",
            description="Top-level immutable application state snapshot enabling 1-tap Functorial Undo",
            fields=[
                FieldDef("state_id", "str", False, "State snapshot UUID"),
                FieldDef("active_season", "str", False, "SUMMER_SOLSTICE, WINTER_SOLSTICE, EQUINOX"),
                FieldDef("total_cells_computed", "int", False, "Total cells in active grid (600)"),
                FieldDef("total_assets_placed", "int", False, "Number of active garden assets"),
                FieldDef("undo_stack_depth", "int", False, "Depth of undo history stack (>= 0)"),
                FieldDef("is_occlusion_free", "bool", False, "True if zero placed assets have critical occlusion warnings"),
            ],
            invariants=[
                "total_cells_computed == 600",
                "total_assets_placed >= 0",
                "undo_stack_depth >= 0",
            ],
        ),
    }

    verbs = {
        "CalculateSolarVector": DomainVerb(
            name="CalculateSolarVector",
            description="Compute NOAA astronomical solar azimuth and altitude for Portland OR at target date and hour",
            parameters=[
                FieldDef("latitude", "float", False, "Latitude (45.5152 deg N)"),
                FieldDef("longitude", "float", False, "Longitude (-122.6784 deg W)"),
                FieldDef("day_of_year", "int", False, "Day of year (1-365)"),
                FieldDef("solar_hour", "float", False, "Hour of day (0.0 to 24.0)"),
            ],
            return_type="SolarPosition",
            pre_conditions=[
                "latitude >= -90.0",
                "latitude <= 90.0",
                "day_of_year >= 1",
                "day_of_year <= 366",
                "solar_hour >= 0.0",
                "solar_hour <= 24.0",
            ],
            post_conditions=[
                "solar_altitude_deg >= -90.0",
                "solar_altitude_deg <= 90.0",
                "solar_azimuth_deg >= 0.0",
                "solar_azimuth_deg < 360.0",
                "solar_vector_computed == True",
            ],
            modifies_nouns=["SolarPosition"],
        ),
        "ProjectPolygonShadows": DomainVerb(
            name="ProjectPolygonShadows",
            description="Raytrace geometric shadow extrusion polygons for house, garage, tree, and fence given solar vector",
            parameters=[
                FieldDef("solar_altitude_deg", "float", False, "Solar elevation angle"),
                FieldDef("solar_azimuth_deg", "float", False, "Solar azimuth angle"),
                FieldDef("obstacle_count", "int", False, "Number of physical obstacles (4)"),
            ],
            return_type="List[ShadowPolygon]",
            pre_conditions=[
                "solar_altitude_deg >= -90.0",
                "solar_azimuth_deg >= 0.0",
                "solar_vector_computed == True",
                "obstacle_count >= 4",
            ],
            post_conditions=[
                "shadow_polygons_projected == True",
                "shadow_length >= 0.0",
            ],
            modifies_nouns=["PhysicalObstacle"],
        ),
        "IntegrateCumulativeInsolation": DomainVerb(
            name="IntegrateCumulativeInsolation",
            description="Sweep sun across daylight arc and integrate direct sun hours for each 1m^2 grid cell (30x20=600 cells)",
            parameters=[
                FieldDef("active_season", "str", False, "SUMMER_SOLSTICE, WINTER_SOLSTICE, EQUINOX"),
                FieldDef("grid_cell_count", "int", False, "Total cells in parcel (600)"),
            ],
            return_type="List[InsolationGridCell]",
            pre_conditions=[
                "shadow_polygons_projected == True",
                "shadow_length >= 0.0",
                "grid_cell_count == 600",
            ],
            post_conditions=[
                "cumulative_heatmap_ready == True",
                "direct_sun_hours >= 0.0",
                "direct_sun_hours <= 24.0",
                "total_cells_computed == 600",
            ],
            modifies_nouns=["InsolationGridCell", "HeliotropicState"],
        ),
        "EvaluateZonalPlacement": DomainVerb(
            name="EvaluateZonalPlacement",
            description="Evaluate candidate asset microclimate against cumulative insolation heatmap",
            parameters=[
                FieldDef("asset_type", "str", False, "RAISED_BED, GAZEBO, TANNING_SPOT"),
                FieldDef("target_x", "float", False, "X position in meters (0 to 30)"),
                FieldDef("target_y", "float", False, "Y position in meters (0 to 20)"),
            ],
            return_type="GardenAssetPlacement",
            pre_conditions=[
                "cumulative_heatmap_ready == True",
                "target_x >= 0.0",
                "target_x <= 30.0",
                "target_y >= 0.0",
                "target_y <= 20.0",
            ],
            post_conditions=[
                "suitability_score >= 0.0",
                "suitability_score <= 1.0",
                "actual_sun_hours >= 0.0",
                "asset_evaluated == True",
            ],
            modifies_nouns=["GardenAssetPlacement", "HeliotropicState"],
        ),
        "ExecuteFunctorialUndo": DomainVerb(
            name="ExecuteFunctorialUndo",
            description="Category-theoretic Functorial Undo restoring previous immutable state snapshot without data loss",
            parameters=[
                FieldDef("undo_stack_depth", "int", False, "Current depth of undo history stack"),
            ],
            return_type="HeliotropicState",
            pre_conditions=[
                "undo_stack_depth > 0",
            ],
            post_conditions=[
                "undo_stack_depth >= 0",
                "functorial_state_restored == True",
            ],
            modifies_nouns=["HeliotropicState"],
        ),
    }

    # Child Sub-Contracts for inductive composition verification
    sub_solar = ContractIR(
        contract_id="sub_solar_kinematics",
        title="NOAA Solar Kinematics Subcontract",
        description="Calculates solar vector from astronomical kinematics",
    )
    sub_solar.add_verb(verbs["CalculateSolarVector"])

    sub_shadow = ContractIR(
        contract_id="sub_shadow_projection",
        title="Polygon Shadow Raytracing Subcontract",
        description="Projects shadow extrusion polygons",
    )
    sub_shadow.add_verb(verbs["ProjectPolygonShadows"])

    sub_insolation = ContractIR(
        contract_id="sub_insolation_integration",
        title="Cumulative Insolation Integration Subcontract",
        description="Integrates direct sunlight hours over 600 grid cells",
    )
    sub_insolation.add_verb(verbs["IntegrateCumulativeInsolation"])

    sub_eval = ContractIR(
        contract_id="sub_asset_evaluation",
        title="Zonal Asset Microclimate Evaluation Subcontract",
        description="Evaluates asset placement suitability score",
    )
    sub_eval.add_verb(verbs["EvaluateZonalPlacement"])

    parent_verb = DomainVerb(
        name="ChoreographMicroclimateCycle",
        description=(
            "End-to-end solar choreography cycle: calculate solar vector -> project shadows "
            "-> integrate 600m^2 heatmap -> evaluate asset placement."
        ),
        parameters=[
            FieldDef("latitude", "float", False, "Latitude (45.5152 deg N)"),
            FieldDef("longitude", "float", False, "Longitude (-122.6784 deg W)"),
            FieldDef("day_of_year", "int", False, "Day of year (1-365)"),
            FieldDef("solar_hour", "float", False, "Solar hour (0.0 to 24.0)"),
            FieldDef("target_x", "float", False, "Asset target X (0 to 30)"),
            FieldDef("target_y", "float", False, "Asset target Y (0 to 20)"),
        ],
        return_type="GardenAssetPlacement",
        pre_conditions=[
            "latitude >= -90.0",
            "latitude <= 90.0",
            "day_of_year >= 1",
            "day_of_year <= 366",
            "solar_hour >= 0.0",
            "solar_hour <= 24.0",
            "target_x >= 0.0",
            "target_x <= 30.0",
            "target_y >= 0.0",
            "target_y <= 20.0",
            "obstacle_count >= 4",
            "grid_cell_count == 600",
        ],
        post_conditions=[
            "asset_evaluated == True",
            "suitability_score >= 0.0",
            "suitability_score <= 1.0",
        ],
        modifies_nouns=["SolarPosition", "PhysicalObstacle", "InsolationGridCell", "GardenAssetPlacement", "HeliotropicState"],
    )

    steps = [
        VerbCompositionStep(
            child_contract_id="sub_solar_kinematics",
            child_verb_name="CalculateSolarVector",
            argument_bindings={"latitude": "latitude", "longitude": "longitude", "day_of_year": "day_of_year", "solar_hour": "solar_hour"},
            output_binding="solar_vector",
        ),
        VerbCompositionStep(
            child_contract_id="sub_shadow_projection",
            child_verb_name="ProjectPolygonShadows",
            argument_bindings={"solar_altitude_deg": "solar_vector.solar_altitude_deg", "solar_azimuth_deg": "solar_vector.solar_azimuth_deg", "obstacle_count": "obstacle_count"},
            output_binding="shadow_polygons",
        ),
        VerbCompositionStep(
            child_contract_id="sub_insolation_integration",
            child_verb_name="IntegrateCumulativeInsolation",
            argument_bindings={"active_season": "active_season", "grid_cell_count": "grid_cell_count"},
            output_binding="insolation_grid",
        ),
        VerbCompositionStep(
            child_contract_id="sub_asset_evaluation",
            child_verb_name="EvaluateZonalPlacement",
            argument_bindings={"asset_type": "asset_type", "target_x": "target_x", "target_y": "target_y"},
            output_binding="evaluated_asset",
        ),
    ]

    composed = {
        "ChoreographMicroclimateCycle": ComposedVerb(
            parent_verb=parent_verb,
            child_steps=steps,
        )
    }

    contract = ContractIR(
        contract_id="contract_axioma_heliotrope",
        title="Axioma Heliotrope Microclimate Studio Contract",
        description="Formal invariants, nouns, and verbs governing real-time solar raytracing, insolation heatmaps, and zonal microclimates",
        nouns=nouns,
        verbs=verbs,
        composed_verbs=composed,
    )

    contract.sub_contracts[sub_solar.contract_id] = sub_solar
    contract.sub_contracts[sub_shadow.contract_id] = sub_shadow
    contract.sub_contracts[sub_insolation.contract_id] = sub_insolation
    contract.sub_contracts[sub_eval.contract_id] = sub_eval

    return contract


def build_heliotrope_statechart_ir() -> StatechartIR:
    """Constructs the Universal Hierarchical StatechartIR (exactly 16 states) for `axioma_heliotrope`.

    Hierarchy:
    - Root: heliotrope_studio (Compound)
      - orienting_parcel (Compound)
        - orienting_parcel.calibrating_bounds (Atomic)
        - orienting_parcel.positioning_structures (Atomic)
      - simulating_heliotropism (Compound)
        - simulating_heliotropism.computing_solar_vector (Atomic)
        - simulating_heliotropism.raytracing_shadows (Atomic)
        - simulating_heliotropism.integrating_heatmap (Atomic)
      - evaluating_zonal_placement (Compound)
        - evaluating_zonal_placement.candidate_selected (Atomic)
        - evaluating_zonal_placement.placement_verified (Atomic)
      - dead_end_occlusion (Compound)
        - dead_end_occlusion.rejection_latched (Atomic)
      - telemetry_monitoring (Parallel orthogonal state)
        - telemetry_monitoring.live_stream (Atomic)
      - history_anchor (Deep History pseudo-state for 1-tap Functorial Undo)

    Total states: 16 (Certified by FormalModelChecker).
    """
    # 1. orienting_parcel substates
    sn_calib = StateNode(
        id="orienting_parcel.calibrating_bounds",
        node_type=StateNodeType.ATOMIC,
        description="Calibrate 30m x 20m parcel boundary and geolocation coordinates",
        transitions=[
            Transition(event="BOUNDS_CALIBRATED", target="orienting_parcel.positioning_structures", description="Bounds set"),
            Transition(event="TRIGGER_UNDO_BOUNDS", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_pos = StateNode(
        id="orienting_parcel.positioning_structures",
        node_type=StateNodeType.ATOMIC,
        description="Position home, garage, tree, and perimeter fence",
        transitions=[
            Transition(event="STRUCTURES_PLACED", target="simulating_heliotropism.computing_solar_vector", description="Structures placed"),
            Transition(event="REORIENT_BOUNDS", target="orienting_parcel.calibrating_bounds", description="Re-calibrate bounds"),
            Transition(event="TRIGGER_UNDO_STRUCTURES", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_orient = StateNode(
        id="orienting_parcel",
        node_type=StateNodeType.COMPOUND,
        initial="orienting_parcel.calibrating_bounds",
        description="Compound state: Parcel spatial configuration and obstacle positioning",
        states={
            "orienting_parcel.calibrating_bounds": sn_calib,
            "orienting_parcel.positioning_structures": sn_pos,
        },
        transitions=[
            Transition(event="QUICK_SIMULATE", target="simulating_heliotropism.computing_solar_vector", description="Proceed to simulation"),
        ],
    )

    # 2. simulating_heliotropism substates
    sn_solar = StateNode(
        id="simulating_heliotropism.computing_solar_vector",
        node_type=StateNodeType.ATOMIC,
        description="Calculate NOAA solar vector (azimuth, elevation) for target date/time",
        transitions=[
            Transition(event="VECTOR_COMPUTED", target="simulating_heliotropism.raytracing_shadows", description="Solar vector ready"),
            Transition(event="TRIGGER_UNDO_SOLAR", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_raytrace = StateNode(
        id="simulating_heliotropism.raytracing_shadows",
        node_type=StateNodeType.ATOMIC,
        description="Raytrace obstacle polygon shadows across parcel plane",
        transitions=[
            Transition(event="SHADOWS_PROJECTED", target="simulating_heliotropism.integrating_heatmap", description="Shadow polygons traced"),
            Transition(event="RECOMPUTE_VECTOR", target="simulating_heliotropism.computing_solar_vector", description="Update solar angle"),
            Transition(event="TRIGGER_UNDO_SHADOWS", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_heat = StateNode(
        id="simulating_heliotropism.integrating_heatmap",
        node_type=StateNodeType.ATOMIC,
        description="Integrate 1m^2 cumulative insolation heatmap across daylight arc",
        transitions=[
            Transition(event="HEATMAP_READY", target="evaluating_zonal_placement.candidate_selected", description="Insolation grid ready for asset placement"),
            Transition(event="NEW_SEASON_SWEEP", target="simulating_heliotropism.computing_solar_vector", description="Sweep solstice or equinox"),
            Transition(event="TRIGGER_UNDO_HEATMAP", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_sim = StateNode(
        id="simulating_heliotropism",
        node_type=StateNodeType.COMPOUND,
        initial="simulating_heliotropism.computing_solar_vector",
        description="Compound state: Solar kinematics and insolation heatmap integration",
        states={
            "simulating_heliotropism.computing_solar_vector": sn_solar,
            "simulating_heliotropism.raytracing_shadows": sn_raytrace,
            "simulating_heliotropism.integrating_heatmap": sn_heat,
        },
        transitions=[
            Transition(event="RECONFIGURE_PARCEL", target="orienting_parcel.calibrating_bounds", description="Return to parcel orientation"),
        ],
    )

    # 3. evaluating_zonal_placement substates
    sn_candidate = StateNode(
        id="evaluating_zonal_placement.candidate_selected",
        node_type=StateNodeType.ATOMIC,
        description="Select candidate asset (raised bed, gazebo, tanning spot) and target coords",
        transitions=[
            Transition(event="EVALUATE_MICROCLIMATE", target="evaluating_zonal_placement.placement_verified", description="Evaluate solar insolation requirements"),
            Transition(event="TRIGGER_UNDO_CANDIDATE", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_verified = StateNode(
        id="evaluating_zonal_placement.placement_verified",
        node_type=StateNodeType.FINAL,
        description="Asset placement meets solar microclimate criteria (>= 6 hrs direct sun for bed)",
        transitions=[
            Transition(event="OCCLUSION_CONFLICT_DETECTED", target="dead_end_occlusion.rejection_latched", description="Shadow occlusion violates requirements"),
            Transition(event="PLACE_ANOTHER_ASSET", target="evaluating_zonal_placement.candidate_selected", description="Place additional asset"),
            Transition(event="RUN_SEASONAL_COMPARISON", target="simulating_heliotropism.computing_solar_vector", description="Verify across seasons"),
            Transition(event="INSPECT_TELEMETRY", target="telemetry_monitoring", description="Inspect live solar telemetry"),
            Transition(event="TRIGGER_UNDO_VERIFIED", target="history_anchor", description="Rollback to deep history"),
        ],
    )

    sn_eval = StateNode(
        id="evaluating_zonal_placement",
        node_type=StateNodeType.COMPOUND,
        initial="evaluating_zonal_placement.candidate_selected",
        description="Compound state: Garden asset placement and microclimate qualification",
        states={
            "evaluating_zonal_placement.candidate_selected": sn_candidate,
            "evaluating_zonal_placement.placement_verified": sn_verified,
        },
        transitions=[
            Transition(event="RECALIBRATE_SIMULATION", target="simulating_heliotropism.computing_solar_vector", description="Back to solar simulation"),
        ],
    )

    # 4. dead_end_occlusion substates
    sn_rejection = StateNode(
        id="dead_end_occlusion.rejection_latched",
        node_type=StateNodeType.ATOMIC,
        description="Asset placed in chronic shadow zone (< minimum threshold)",
        transitions=[
            Transition(event="RESOLVE_CONFLICT", target="evaluating_zonal_placement.candidate_selected", description="Select alternate coordinates"),
            Transition(event="TRIGGER_UNDO_OCCLUSION", target="history_anchor", description="1-tap Functorial Undo to restore last valid state"),
        ],
    )

    sn_occlusion = StateNode(
        id="dead_end_occlusion",
        node_type=StateNodeType.COMPOUND,
        initial="dead_end_occlusion.rejection_latched",
        description="Compound state: Handling severe shadow occlusion warning and resolution",
        states={
            "dead_end_occlusion.rejection_latched": sn_rejection,
        },
        transitions=[
            Transition(event="FORCE_RETRY", target="evaluating_zonal_placement.candidate_selected", description="Retry placement"),
        ],
    )

    # 5. history_anchor pseudo-state (Deep History)
    sn_history = StateNode(
        id="history_anchor",
        node_type=StateNodeType.HISTORY,
        history_type=HistoryType.DEEP,
        description="Deep History pseudo-state anchoring parcel layout and asset placement for 1-tap Functorial Undo",
        transitions=[
            Transition(event="HISTORY_RESTORE", target="orienting_parcel.calibrating_bounds", description="Fallback default target if history empty"),
        ],
    )

    # 6. telemetry_monitoring (Parallel orthogonal state)
    sn_telemetry_stream = StateNode(
        id="telemetry_monitoring.live_stream",
        node_type=StateNodeType.ATOMIC,
        description="Streaming telemetry metrics and Landauer bit dissipation",
        transitions=[
            Transition(event="TELEMETRY_PULSE", target="telemetry_monitoring.live_stream", description="Heartbeat pulse"),
            Transition(event="RETURN_TO_STUDIO", target="evaluating_zonal_placement.placement_verified", description="Return to main design canvas"),
        ],
    )

    sn_telemetry = StateNode(
        id="telemetry_monitoring",
        node_type=StateNodeType.PARALLEL,
        description="Parallel orthogonal region: Real-time telemetry monitoring and Landauer bit dissipation ledger",
        states={
            "telemetry_monitoring.live_stream": sn_telemetry_stream,
        },
        transitions=[
            Transition(event="RESUME_DESIGN", target="evaluating_zonal_placement.placement_verified", description="Resume interactive permaculture design"),
        ],
    )

    # Root compound state
    root = StateNode(
        id="heliotrope_studio",
        node_type=StateNodeType.COMPOUND,
        initial="orienting_parcel",
        description="Root compound state machine for Axioma Heliotrope Studio",
        states={
            "orienting_parcel": sn_orient,
            "simulating_heliotropism": sn_sim,
            "evaluating_zonal_placement": sn_eval,
            "dead_end_occlusion": sn_occlusion,
            "telemetry_monitoring": sn_telemetry,
            "history_anchor": sn_history,
        },
    )

    return StatechartIR(
        id="statechart_axioma_heliotrope",
        root=root,
        context_schema={
            "parcel_width": "float",
            "parcel_length": "float",
            "active_season": "str",
            "solar_azimuth": "float",
            "solar_elevation": "float",
            "placed_assets_count": "int",
            "undo_stack_depth": "int",
            "occlusion_warning_active": "bool",
        },
        initial_context={
            "parcel_width": 30.0,
            "parcel_length": 20.0,
            "active_season": "SUMMER_SOLSTICE",
            "solar_azimuth": 180.0,
            "solar_elevation": 68.0,
            "placed_assets_count": 0,
            "undo_stack_depth": 0,
            "occlusion_warning_active": False,
        },
    )


def build_heliotrope_topology_ir(inject_fault: bool = False) -> TopologyIR:
    """Constructs the local hardware TopologyIR for Axioma Heliotrope."""
    topo = TopologyIR(topology_id=f"topo_{SOC_ID_HELIOTROPE}")

    host_studio = "127.0.0.1" if inject_fault else "192.168.1.100"
    host_raytracer = "localhost" if inject_fault else "192.168.1.101"
    host_verifier = "192.168.1.102"

    topo.add_node(TopologyNode(
        node_id="node_heliotrope_studio",
        role=NodeRole.ORCHESTRATOR,
        host_interface=host_studio,
        port=8080,
        capabilities=["parcel_canvas_ui", "statechart_engine", "functorial_undo", "solar_kinematics"],
        memory_mb_limit=4096,
    ))
    topo.add_node(TopologyNode(
        node_id="node_solar_raytracer",
        role=NodeRole.WORKER,
        host_interface=host_raytracer,
        port=8081,
        capabilities=["polygon_shadow_projection", "cumulative_insolation_integration", "enclave_fallback"],
        memory_mb_limit=4096,
    ))
    topo.add_node(TopologyNode(
        node_id="node_microclimate_verifier",
        role=NodeRole.VERIFIER,
        host_interface=host_verifier,
        port=8082,
        capabilities=["zonal_suitability_evaluator", "compositional_contract_verifier"],
        memory_mb_limit=2048,
    ))

    topo.add_channel(NetworkChannel(
        channel_id="ch_solar_raytrace_rpc",
        source_node_id="node_heliotrope_studio",
        target_node_id="node_solar_raytracer",
        channel_type=ChannelType.RPC,
        port=8081,
        latency_ms_budget=20,
        tls_enforced=False,
    ))
    topo.add_channel(NetworkChannel(
        channel_id="ch_microclimate_audit_rpc",
        source_node_id="node_heliotrope_studio",
        target_node_id="node_microclimate_verifier",
        channel_type=ChannelType.RPC,
        port=8082,
        latency_ms_budget=15,
        tls_enforced=True,
    ))

    topo.consensus = ConsensusContract(
        protocol=ConsensusProtocol.SHEAF_QUORUM,
        quorum_fraction=0.67,
        heartbeat_interval_ms=500,
        partition_strategy="fail_closed",
    )
    return topo


def build_heliotrope_domain_spec() -> Dict[str, Any]:
    """Returns the full domain specification dictionary for `axioma_heliotrope`."""
    contract = build_heliotrope_contract_ir()
    statechart = build_heliotrope_statechart_ir()
    topo = build_heliotrope_topology_ir(inject_fault=False)
    endpoints = [f"http://{n.host_interface}:{n.port}" for n in topo.nodes.values()]
    return {
        "contract_ir": contract.to_dict(),
        "statechart_ir": statechart.to_dict(),
        "topology_ir": topo.to_dict(),
        "endpoints": endpoints,
        "soc": build_heliotrope_soc().to_dict(),
        "contract": contract.to_dict(),
        "statechart": statechart.to_dict(),
        "invariants": REQUIRED_INVARIANTS_HELIOTROPE,
        "obstacles": [
            {
                "id": "house_main",
                "type": "HOUSE",
                "origin_x": 5.0,
                "origin_y": 6.0,
                "width_m": 12.0,
                "length_m": 8.0,
                "height_m": 7.0,
                "roof_ridge_height_m": 9.0,
                "description": "2-story residential house (12x8m, eave 7m, gable ridge 9m)",
            },
            {
                "id": "garage_detached",
                "type": "GARAGE",
                "origin_x": 20.0,
                "origin_y": 12.0,
                "width_m": 6.0,
                "length_m": 6.0,
                "height_m": 3.5,
                "roof_ridge_height_m": 3.5,
                "description": "Detached single-story garage (6x6m, flat/low-slope 3.5m)",
            },
            {
                "id": "cedar_tree",
                "type": "TREE",
                "origin_x": 8.0,
                "origin_y": 16.0,
                "width_m": 4.0,
                "length_m": 4.0,
                "height_m": 2.0,
                "roof_ridge_height_m": 8.0,
                "canopy_radius_m": 2.0,
                "description": "Mature conical western red cedar tree (radius 2m, height 8m)",
            },
            {
                "id": "fence_perimeter",
                "type": "FENCE",
                "origin_x": 0.0,
                "origin_y": 0.0,
                "width_m": 30.0,
                "length_m": 20.0,
                "height_m": 1.8,
                "roof_ridge_height_m": 1.8,
                "description": "Perimeter cedar privacy fence (height 1.8m)",
            },
        ],
        "geolocation": {
            "latitude": 45.5152,
            "longitude": -122.6784,
            "city": "Portland, OR",
            "timezone_offset_utc": -8.0,
        },
        "seasons": {
            "SUMMER_SOLSTICE": {"day_of_year": 172, "peak_altitude": 68.0, "daylight_hours": 15.7},
            "EQUINOX": {"day_of_year": 80, "peak_altitude": 44.5, "daylight_hours": 12.0},
            "WINTER_SOLSTICE": {"day_of_year": 355, "peak_altitude": 21.0, "daylight_hours": 8.7},
        },
        "asset_catalog": {
            "RAISED_BED": {
                "name": "Organic Edible Raised Bed (4x8ft)",
                "min_sun_hours": 6.0,
                "max_sun_hours": 24.0,
                "ideal_sun_hours": 8.0,
                "width_m": 2.4,
                "length_m": 1.2,
            },
            "GAZEBO": {
                "name": "Dappled Shade Timber Gazebo (10x10ft)",
                "min_sun_hours": 0.0,
                "max_sun_hours": 4.0,
                "ideal_sun_hours": 2.0,
                "width_m": 3.0,
                "length_m": 3.0,
            },
            "TANNING_SPOT": {
                "name": "Heliotropic Solar Tanning Deck",
                "min_sun_hours": 5.0,
                "max_sun_hours": 24.0,
                "ideal_sun_hours": 7.0,
                "width_m": 2.0,
                "length_m": 2.0,
            },
        },
    }
