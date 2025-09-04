# Terran 1 — Vehicle & Mission Assumptions
_Last updated: YYYY-MM-DD_

> **Scope:** End-to-end vehicle simulation using **public information only** (approximate/educational). Any missing data are estimated with transparent ranges and documented rationale.

---

## 0) Project Context
- **Vehicle:** Relativity Space **Terran 1** (2-stage, LOX/LCH4)
- **Objective:** Build a reproducible stack: 3-DOF ascent → CFD-based AeroDB → Propulsion maps → 6-DOF + GNC → Monte Carlo dispersions.
- **Deliverables:** Nominal ascent, AeroDB (Cd/Cl/Cm vs Mach, α), PropMap (Thrust/Isp vs altitude), closed-loop 6-DOF, MC sensitivity analysis, plots & report.

---

## 1) Vehicle Overview (Public Specs – filled)
- **Overall length:** 33.5 m
- **Diameter:** 2.28 m
- **Fairing OD/length:** ~2.28 m OD, ~6–7 m long (public renders/press images)
- **Stage configuration:** S1 — 9× Aeon 1; S2 — 1× AeonVac
- **Payload class to LEO:** ~1,250 kg (advertised)
- **Launch site (example mission):** CCAFS LC-16
- **Notes:** All values from Relativity Space press releases and aerospace references.

---

## 2) Mass Properties (Estimated — no public breakdown released)
> Values below are **estimates**, based on Terran 1’s published size and payload class, plus typical methalox stage fractions. Will refine if more public info emerges.

### Stage 1 (estimates)
- **Prop mass (kg):** ~92,000 (range 85,000–100,000)
- **Dry mass (kg):** ~9,000 (range 7,000–10,000)
- **Propellant mass fraction:** ~0.91
- **CG travel:** forward during burn (curve TBD)
- **Inertia (principal):** slender-body approximation (TBD)

### Stage 2 (estimates)
- **Prop mass (kg):** ~18,000 (range 15,000–22,000)
- **Dry mass (kg):** ~2,000 (range 1,500–2,500)
- **Propellant mass fraction:** ~0.90
- **CG/Inertia:** TBD

**Rationale:** No official stage masses published. Estimates derived from Terran 1’s overall dimensions, LOX/LCH4 density, and typical dry-mass fractions of small orbital-class launchers (Rocket Lab Electron, Firefly Alpha, Falcon 1 for reference class).

---

## 3) Propulsion (public specs + estimated parameters)

### Aeon 1 (Stage 1 engines)
- **Count:** 9
- **Cycle:** Oxygen-rich staged combustion
- **Sea-level thrust (kN):** ~100 (public spec)
- **Vacuum thrust (kN):** ~110–115 (estimated)
- **Isp SL (s):** ~310 (typical for LOX/LCH4 engines of this class)
- **Isp Vac (s):** ~330 (estimated)
- **Throttle range:** TBD (assume 60–100% until sourced)
- **Gimbal authority/rate:** TBD (assume ±5°, 10–20°/s)

### AeonVac (Stage 2 engine)
- **Count:** 1
- **Cycle:** Oxygen-rich staged combustion
- **Vacuum thrust (kN):** ~126 (public spec)
- **Isp Vac (s):** ~358 (public spec)
- **Sea-level thrust (kN):** N/A (vacuum-optimized)
- **Restart capability:** TBD

**Implementation plan:**  
- Seed performance curves with NASA CEA runs for methane/LOX.  
- Tune thrust/Isp vs ambient pressure to match these public values.  
- Export results into `/data/PropMap_v1.csv` for trajectory integration.

Artifacts to produce:
- `/data/PropMap_v1.csv` — columns: altitude_m, p_amb_Pa, thrust_kN, Isp_s, throttle

---

## 4) Aerodynamics (OpenFOAM plan)

**Goal:** Generate an initial aerodynamic database (AeroDB_v1) for Terran 1 using OpenFOAM to replace placeholder Cd in the 3-DOF model and feed the 6-DOF sim with forces/moments.

### 4.1 Geometry & Reference Quantities
- **External geometry:** Axisymmetric **nosecone + cylindrical main body + payload fairing** (no fins assumed for first pass).
- **Diameter (D):** 2.28 m
- **Reference area (S):** \( S = \pi (D/2)^2 = \pi \times 1.14^2 \approx 4.084\ \mathrm{m}^2 \) → **4.084 m²** (use this value consistently)
- **Reference length:** **D** (2.28 m) for non-dimensionalization
- **Axes:** Body-fixed X along the longitudinal axis, Y/Z lateral

### 4.2 Flow Conditions & Case Matrix
- **Mach numbers:** 0.3, 0.8, 0.95, 1.10, 1.50, 2.0, 3.0, 5.0  
  (dense near transonic where shocks form; you can add 0.9/1.0/1.2 later)
- **Angles of attack (α):** −4°, −2°, 0°, +2°, +4°, +6°, +8°
- **Reynolds number:** Compute from freestream ρ, μ, a(T); track but don’t target a specific Re for v1
- **Assumption:** Zero sideslip (β = 0) for v1; add β sweeps later if needed (for lateral stability)

**Outputs per case:** Cd, Cl, Cm (about CG/location you’ll define below), plus Cp and τ_w fields for diagnostics.

### 4.3 Meshing & Domain
- **Mesher:** `snappyHexMesh` on a base `blockMesh` domain
- **Domain extents (axisymmetric external flow):**
  - Upstream: ≥ **10D**
  - Radial (side): ≥ **10D**
  - Downstream: ≥ **20–30D** (to capture wake/pressure recovery)
- **Near-wall resolution (two valid strategies):**
  - **Low-Re (recommended for SST):** target **y+ ~ 1–5** with 20–30 prism layers (growth ~1.15–1.2)
  - **Wall-function approach:** target **y+ ~ 30–100** with appropriate wall functions; use if mesh budget is tight
- **Refinement:** Local surface/volume refinements at the **nose, fairing shoulder, and base**; add shock-aligned refinement boxes for transonic/supersonic cases

### 4.4 Turbulence & Solvers
- **Model:** **k-ω SST (compressible)** for external aerodynamic forces (robust across M=0.3–5.0)
- **Steady vs transient:**
  - Start with **`rhoSimpleFoam`** (steady RANS) for sub/supersonic cases
  - Use **`rhoPimpleFoam`** (pseudo-transient) for transonic cases (M≈0.9–1.2) to aid shock convergence
- **Numerics:**
  - Density/pressure schemes: total variation diminishing (TVD) or limited upwind
  - Grad/Div schemes: second-order where stable; apply limiters around shocks
  - Convergence: residuals < 1e-5 (or force coefficients steady within <0.5% over 500 iterations)

### 4.5 Boundary Conditions (illustrative)
- **Inlet (freestream):** `freestream` for U, T; `totalTemperature`/`totalPressure` as needed; or specify p/T/U from ISA at the equivalent flight altitude if you want altitude-specific cases
- **Outlet:** `pressureOutlet` (or `waveTransmissive`/`inletOutlet` for stability)
- **Farfield:** `freestream` (matching inlet values)
- **Wall (vehicle):** `noSlip`; thermal BC either adiabatic or fixed heat-flux = 0 for aero-only
- **Symmetry:** none for AoA sweeps (use full 3D); for α=0° only, you may use a wedge/half model to save cells

### 4.6 Reference Frame, Forces & Moments
- **Reference area:** **4.084 m²**
- **Reference length:** **2.28 m**
- **Moment reference (x_ref):** choose a fixed point along the axis (e.g., **stage-level CG at liftoff** or **geometric center**) and document it.  
  > Note: For vehicle-level sims, you’ll later transform moments to the **time-varying CG**; store both the force/moment at the CFD reference and the transform logic in your sim.

- **Extraction:** Use `forces` / `forcesCoeffs` function objects to write **Cd, Cl, Cm** per case to CSV.

### 4.7 Post-Processing & AeroDB_v1
- **CSV structure (`/data/AeroDB_v1.csv`):**  
  `Mach, alpha_deg, Re, Cd, Cl, Cm, x_ref_m, S_ref_m2, L_ref_m`
- **Contour exports:** pressure coefficient (Cp), Mach, and wall shear stress around the nose/fairing for documentation
- **Interpolation:** Build bilinear or spline interpolation (Mach × α) in your sim code; outside the grid, clamp or extrapolate cautiously

### 4.8 Validation & Sanity Checks
- **Subsonic Cd (M≈0.3):** compare against slender-body/empirical estimates (order-of-magnitude check)
- **Transonic (M≈0.95–1.10):** expect higher uncertainty; ensure mesh-independence in shock regions (refinement study)
- **Supersonic (M≥2):** check shock angles vs oblique shock relations at small α (qualitative)
- **Sensitivity:** run a small **mesh refinement study** (coarse/medium/fine) at M=0.95 and M=2.0, α=0° to quantify Cd changes
- **Numerical stability:** ensure force coefficients settle; if oscillatory, switch to pseudo-transient or refine shocks

### 4.9 Known Limitations (v1)
- **Base drag** not modeled accurately with axisymmetric closure → v2 task: add base region treatment or body-of-revolution with base cavity modeling
- **Fairing separation**, protuberances (avionics pods, cable raceways), and ring steps omitted in v1
- **No control-surface effects** (no fins assumed)
- **RANS limitations** in predicting shock/boundary-layer interaction at transonic → widen uncertainty bands there

### 4.10 To-Do (Aero)
- [ ] Build axisymmetric CAD with correct D and approximate L/D and fairing ogive
- [ ] Set up `blockMesh` + `snappyHexMesh` with prism layers; hit y+ target
- [ ] Run the first three cases: (M=0.3, α=0°), (M=0.95, α=0°), (M=2.0, α=0°)
- [ ] Extract Cd/Cl/Cm and write initial `AeroDB_v1.csv`
- [ ] Validate subsonic Cd vs slender-body estimate; inspect transonic shocks
- [ ] Add α sweeps at M=0.95 and M=2.0; then fill out full Mach grid

Artifacts to produce:
- `/data/AeroDB_v1.csv` — columns: Mach, alpha_deg, Cd, Cl, Cm

---

## 5) Environments

- **Atmosphere (truth runs):** U.S. Standard Atmosphere 1976 (mean density, pressure, temperature vs altitude).
- **Winds/density (Monte Carlo):** Earth-GRAM (Global Reference Atmospheric Model) — seasonal climatology for CCAFS (Cape Canaveral), including wind shear and density perturbations.
- **Gravity:** WGS-84 Earth gravitational parameter (μ = 3.986004418 × 10^14 m³/s²).
- **Earth rotation:** included in inertial-to-Earth-fixed transforms for ascent targeting (optional for early 3-DOF runs, recommended for 6-DOF).


---

## 6) Trajectory & GNC

### 6.1 Truth Model (3-DOF)
- **Dynamics:** Planar 3-DOF point-mass equations of motion (Earth-fixed to inertial).
- **Inputs:** Time histories of thrust (from PropMap), drag (from AeroDB), and gravity losses.
- **Pitch program:** Open-loop gravity turn with pitchover near ~10–15 s after liftoff.
- **Constraints:** Enforce Max-Q (target ~30–40 kPa, TBD), axial acceleration ≤ ~5 g, lateral acceleration ≤ ~0.25 g.
- **Outputs:** Altitude, velocity, flight-path angle, dynamic pressure, acceleration vs time.

### 6.2 6-DOF Vehicle Dynamics
- **Equations:** Rigid-body 6-DOF with quaternions (attitude propagation), translational dynamics with thrust, drag, lift, gravity.
- **Control effectors:** Thrust vector control (gimbal) on Aeon 1 cluster and AeonVac.
- **Actuator limits:** Authority ±5° (placeholder), rate limit 10–20 °/s (placeholder).
- **Sensors:** Ideal IMU for v1; add bias/noise in Monte Carlo.

### 6.3 Guidance
- **Stage 1:** Open-loop pitch-rate command to follow gravity-turn trajectory, throttle shaping for Max-Q relief.
- **Stage 2:** Polynomial guidance law or energy-optimal ascent; closed-loop correction to target orbit (altitude, velocity, inclination).
- **Target orbit (example mission):** 200 km circular, 28.5° inclination (Cape Canaveral).

### 6.4 Autopilot / Control Laws
- **Controller:** PID (v1) or LQR for attitude hold and rate tracking.
- **Control allocation:** distribute gimbal commands across S1 engine cluster (9× Aeon 1) — simplified average gimbal for v1.

### 6.5 Events
- Liftoff
- Pitchover
- Max-Q
- MECO (Main Engine Cut-Off, S1)
- Stage separation
- Fairing separation
- SECO (Second Engine Cut-Off, S2)
- Orbit insertion (target circular orbit)

**Artifacts:**  
- `/traj3dof/nominal.py` → baseline ascent profiles.  
- `/sim6dof/vehicle6dof.py` → rigid-body dynamics with TVC.  
- Plots: altitude vs time, velocity vs time, q vs time, pitch vs time, accel vs time.  


Key plots:
- altitude/velocity/flight-path angle vs time; q and acceleration vs time; pitch/throttle schedules

---

## 7) Monte Carlo Dispersions

**Purpose:** Quantify robustness of Terran 1 ascent to realistic variations in vehicle parameters, environment, and sensors. Provide probability distributions of performance metrics (orbit insertion, Max-Q, structural loads) and identify dominant sensitivities.

### 7.1 Vehicle Dispersions
- **Stage masses:** ±2% (prop and dry, independent)
- **CG location:** ±1–2% of stage length (longitudinal offset)
- **Thrust levels:** ±3% (engine-to-engine variation)
- **Isp:** ±2% (mixture ratio, chamber conditions)
- **Gimbal bias:** ±0.2° offset; rate limit ±10% variation
- **Fairing mass/separation:** ±5% (mass uncertainty + separation timing jitter)

### 7.2 Aerodynamic Dispersions
- **Cd:** ±5% global; amplified ±10% in transonic regime (M ≈ 0.9–1.2)
- **Cl/Cm:** ±10% slope uncertainty (due to RANS limits)
- **Base drag:** modeled with additional ±20% uncertainty (if included)

### 7.3 Environment Dispersions
- **Atmosphere:** Earth-GRAM seasonal CCAFS profiles (temperature, density, winds)
- **Winds:** profiles varied in magnitude and shear; include crosswinds
- **Density perturbations:** ±5% at altitudes <20 km, per GRAM

### 7.4 Sensor/Avionics Dispersions
- **IMU bias:** ±50–100 μg accel, ±0.01–0.05 °/hr gyro (placeholder ranges)
- **IMU noise:** Gaussian white noise, 3σ consistent with commercial-grade units
- **Navigation update rate:** assume 10 Hz (TBD)

### 7.5 Simulation Plan
- **Runs per campaign:** 500–1000 shots
- **Metrics recorded:**  
  - Orbit insertion errors (apogee, perigee, inclination, Δv shortfall/excess)  
  - Max dynamic pressure (q_max) distribution  
  - Max axial/lateral acceleration  
  - Propellant reserves at MECO/SECO  
  - Flight termination criteria violations (if applicable)

- **Analysis outputs:**  
  - CDFs of orbit parameters  
  - Histograms of q_max and accel peaks  
  - Tornado plots of sensitivities (rank-ordered)  
  - Success/failure rate (orbit insertion within tolerance)  

**Exit Criteria:**  
Monte Carlo converged (metrics stable ±1% with additional samples). Top-3 sensitivities identified. Performance robustness assessed with confidence intervals.

---

## 8) Data Artifacts & Directory Conventions

**Repo structure is designed for reproducibility and traceability. Each artifact must be version-controlled or generated reproducibly from inputs.**

### 8.1 Data
- `/data/AeroDB_v1.csv`  
  - Source: OpenFOAM cases (Section 4)  
  - Contents: Mach, α, Cd, Cl, Cm, reference values  
  - Used by: 3-DOF and 6-DOF sims  

- `/data/PropMap_v1.csv`  
  - Source: CEA + nozzle CFD (Section 3)  
  - Contents: altitude, ambient pressure, thrust, Isp, throttle setting  
  - Used by: all trajectory models  

- `/data/MassProperties_v1.csv`  
  - Source: assumptions (Section 2)  
  - Contents: stage, prop mass, dry mass, CG, inertia estimates  
  - Used by: trajectory + 6-DOF models  

### 8.2 Simulation Runs
- `/runs/YYYY-MM-DD/###/`  
  - Each run folder contains:  
    - `config.yaml` snapshot  
    - Inputs (data hash, case setup)  
    - Outputs: logs, CSVs, plots  
  - Naming convention: run index (e.g., 001, 002)  

### 8.3 Documentation
- `/docs/assumptions.md` — master assumptions (this file)  
- `/docs/VnV.md` — verification & validation breadcrumbs  
- `/docs/figures/` — key figures (q-max plots, trajectories, CFD contours, MC CDFs)  

### 8.4 Scripts & Code
- `/traj3dof/` — nominal ascent solver (Python/MATLAB)  
- `/sim6dof/` — 6-DOF rigid-body dynamics + GNC  
- `/aero/` — OpenFOAM cases and postprocessing scripts  
- `/prop/` — propulsion curve generation (CEA inputs, nozzle CFD)  
- `/mass/` — mass property estimates, inertia calculators  
- `/env/` — atmospheric models (USSA76, Earth-GRAM interface)  
- `/mc/` — Monte Carlo runners, dispersions, analysis scripts  

**Principle:** *Every figure in the final report can be regenerated by running code with the appropriate config + data snapshot.*  


---

## 9) Open Questions / To-Do

### Vehicle & Mass Properties
- [ ] Replace **Stage 1 & 2 prop/dry mass** placeholders with sourced values or refined estimates.
- [ ] Add **fairing mass** and separation event timing (public data TBD).
- [ ] Establish **CG curves** vs burn for both stages (currently placeholder).

### Propulsion
- [ ] Confirm **AeonVac restart capability** (number of restarts, if any).
- [ ] Identify **throttle range** for Aeon 1 & AeonVac (public data TBD).
- [ ] Establish **gimbal authority & rate limits** (S1 engine cluster, S2 AeonVac).

### Aerodynamics
- [ ] Validate **OpenFOAM mesh independence** at M=0.95 and M=2.0.
- [ ] Add **base drag model** for improved transonic/supersonic fidelity.
- [ ] Evaluate **aero uncertainty bands** (±% values may need tightening after CFD).

### Environments
- [ ] Acquire **Earth-GRAM seasonal data** for Cape Canaveral (Monte Carlo dispersions).
- [ ] Document **atmospheric density perturbations** vs standard deviations.

### Trajectory & GNC
- [ ] Implement **throttle shaping** to actively control Max-Q in 3-DOF.
- [ ] Expand **6-DOF autopilot** beyond PID (consider LQR or gain-scheduled controller).
- [ ] Add **attitude sensor models** (bias, drift, noise).

### Monte Carlo
- [ ] Define **success criteria** for orbit insertion (e.g., ±2 km altitude, ±10 m/s velocity).
- [ ] Run convergence study: how many shots until statistics stabilize?
- [ ] Automate **sensitivity ranking** (tornado plots).

### Documentation
- [ ] Update `/docs/assumptions.md` as TBDs are resolved.
- [ ] Add citations for all public data (vehicle specs, engine performance, environment models).
- [ ] Expand `/docs/VnV.md` with verification cases (slender-body Cd, nozzle Cf, etc.).

---

## 10) Change Log

- 2025-09-04: Initial draft of assumptions.md created (template).
- 2025-09-05: Populated Section 1 (Vehicle Overview) with public Terran 1 specs (length, diameter, payload, engines).
- 2025-09-05: Added Stage 1 & 2 **mass property estimates** (prop/dry ranges, mass fractions).
- 2025-09-06: Updated **Propulsion** section with Aeon 1 and AeonVac thrust/Isp values from public data.
- 2025-09-06: Expanded **Aerodynamics** plan with OpenFOAM meshing, solver setup, and reference area.
- 2025-09-07: Refined **Environments, Trajectory & GNC, Monte Carlo, Artifacts, To-Do** into repo-aligned sections.
- 2025-09-07: Added Open Questions / To-Do list (organized by vehicle, propulsion, aero, env, trajectory, MC).

---

## References (to populate as you cite)
- Public Terran 1 vehicle overview/specs — **TBD link**  
- Engine public figures (Aeon 1, AeonVac) — **TBD link**  
- Launch site & mission context (LC-16) — **TBD link**  
- Atmosphere & dispersions: U.S. Standard Atmosphere 1976; Earth-GRAM — **TBD link**  
- Aerodynamics references (slender-body correlations; transonic RANS caveats) — **TBD link**
