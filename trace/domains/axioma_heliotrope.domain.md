# Domain: Axioma Heliotrope (`soc_heliotropic_microclimate_studio`)

- **Generation:** System $G_{3b}$ (`SystemG3bCompiler` via Dual-Model Routing + 4-Stage Subagent Witness)
- **App Path:** `apps/axioma_heliotrope/`
- **Target Epoch:** `generations/gen_03b/epochs/epoch_heliotrope_studio/`
- **Port:** `8080`
- **SHA-256 Telemetry Chain Head:** `9b751be835f1efe7cecc06afc41733166569d0c1542ec57e9260c8b49accaa31`

## 1. Waterloo Situation of Concern (`[L1-G3B-000]`)
- **Root Friction:** Landscape designers, permaculturists, and urban homesteaders design outdoor spaces without physical solar and shadow awareness. Trees, roofs, fences, and detached structures cast dynamic, seasonal shadows that create disparate microclimates. Planting light-demanding cultivars (edible vegetables requiring $\ge 6\text{h}$ direct sun) in chronic winter/equinox shadow zones leads to plant death, wasted capital, and frustration.
- **Co-Equal Actors:**
  - **Elena (The Permaculture Designer & Landscaper):** Models the parcel boundary, positions physical obstacles (pitched-roof house, garage, mature cedar tree, boundary fence), scrubs the diurnal solar slider, and evaluates zonal garden asset placements.
  - **The Solar Ephemeris Engine (NOAA Kinematics Solver):** Computes exact solar declination, equation of time, solar altitude, and solar azimuth for Portland, OR ($45.5152^\circ\text{ N}, -122.6784^\circ\text{ W}$) across Solstices and Equinoxes.
  - **The 3D Raytracer & Discrete Heatmap Integrator:** Projects 2.5D polygon shadow extrusions across the $30\text{m} \times 20\text{m}$ yard and integrates direct sunlight hours across 600 discrete $1\text{m}^2$ grid cells.
  - **The Deterministic Exception Enclave (`[L1-016]`):** Traps float singularities or out-of-bounds inputs, guaranteeing continuous server operation with deterministic fallback values.

## 2. Core Entities (`ContractIR` Nouns)
1. **`ParcelLayout`**
   - Fields: `parcel_id: str`, `width_m: float`, `length_m: float`, `grid_resolution_m: float`, `latitude: float`, `longitude: float`, `north_azimuth_offset_deg: float`
   - Invariants: `width_m == 30.0`, `length_m == 20.0`, `grid_resolution_m == 1.0`, `latitude >= -90.0`, `latitude <= 90.0`, `longitude >= -180.0`, `longitude <= 180.0`
2. **`PhysicalObstacle`**
   - Fields: `obstacle_id: str`, `obstacle_type: str`, `origin_x: float`, `origin_y: float`, `width_m: float`, `length_m: float`, `height_m: float`, `roof_ridge_height_m: float`, `canopy_radius_m: float`
   - Invariants: `origin_x >= 0.0`, `origin_x <= 30.0`, `origin_y >= 0.0`, `origin_y <= 20.0`, `height_m >= 0.0`, `canopy_radius_m >= 0.0`
3. **`SolarPosition`**
   - Fields: `solar_timestamp: str`, `day_of_year: int`, `solar_hour: float`, `declination_deg: float`, `hour_angle_deg: float`, `solar_azimuth_deg: float`, `solar_altitude_deg: float`, `is_sun_above_horizon: bool`
   - Invariants: `solar_azimuth_deg >= 0.0`, `solar_azimuth_deg < 360.0`, `solar_altitude_deg >= -90.0`, `solar_altitude_deg <= 90.0`, `day_of_year >= 1`, `day_of_year <= 366`
4. **`InsolationGridCell`**
   - Fields: `cell_x: int`, `cell_y: int`, `direct_sun_hours: float`, `diffuse_insolation_kwh: float`, `is_occluded_at_peak: bool`, `primary_shadow_caster_id: str`
   - Invariants: `cell_x >= 0`, `cell_x < 30`, `cell_y >= 0`, `cell_y < 20`, `direct_sun_hours >= 0.0`, `direct_sun_hours <= 24.0`, `diffuse_insolation_kwh >= 0.0`
5. **`GardenAssetPlacement`**
   - Fields: `asset_id: str`, `asset_type: str`, `pos_x: float`, `pos_y: float`, `min_sun_hours_required: float`, `max_sun_hours_tolerated: float`, `actual_sun_hours: float`, `suitability_score: float`, `is_valid_microclimate: bool`
   - Invariants: `pos_x >= 0.0`, `pos_x <= 30.0`, `pos_y >= 0.0`, `pos_y <= 20.0`, `suitability_score >= 0.0`, `suitability_score <= 1.0`, `actual_sun_hours >= 0.0`, `actual_sun_hours <= 24.0`
6. **`HeliotropicState`**
   - Fields: `state_id: str`, `active_season: str`, `total_cells_computed: int`, `total_assets_placed: int`, `undo_stack_depth: int`, `is_occlusion_free: bool`
   - Invariants: `total_cells_computed == 600`, `total_assets_placed >= 0`, `undo_stack_depth >= 0`

## 3. Compositional Contracts (`ContractIR` Verbs)
- **`ChoreographMicroclimateCycle`:**
  - `CalculateSolarVector` ($\text{lat, lon, day, hour} \to \text{SolarPosition}$)
  - $\to$ `ProjectPolygonShadows` ($\text{SolarPosition, obstacles} \to \text{ShadowPolygons}$)
  - $\to$ `IntegrateCumulativeInsolation` ($\text{ShadowPolygons, time-steps} \to \text{InsolationGrid}$)
  - $\to$ `EvaluateZonalPlacement` ($\text{InsolationGrid, asset\_type, x, y} \to \text{SuitabilityScore}$)
- **`ExecuteFunctorialUndo` (`[L1-002]`):**
  - Reverts prior layout and placement snapshot from deep history stack.
