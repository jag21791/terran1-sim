# Terran 1 — Vehicle & Mission Assumptions
_Last updated: YYYY-MM-DD_

> **Scope:** End-to-end vehicle simulation using **public information only** (approximate/educational). Any missing data are estimated with transparent ranges and documented rationale.

---

## 0) Project Context
- **Vehicle:** Relativity Space **Terran 1** (2-stage, LOX/LCH4)
- **Objective:** Build a reproducible stack: 3-DOF ascent → CFD-based AeroDB → Propulsion maps → 6-DOF + GNC → Monte Carlo dispersions.
- **Deliverables:** Nominal ascent, AeroDB (Cd/Cl/Cm vs Mach, α), PropMap (Thrust/Isp vs altitude), closed-loop 6-DOF, MC sensitivity analysis, plots & report.

---

## 1) Vehicle Overview (Public Specs – fill in from sources)
- **Overall length:** **TBD** (public spec)
- **Diameter:** **TBD** (public spec)
- **Fairing OD/length:** **TBD** (public spec)
- **Stage configuration:** S1 — **9× Aeon 1**, S2 — **1× AeonVac** (public)
- **Payload class to LEO:** **TBD** (public spec)
- **Launch site (example mission):** CCAFS **LC-16**
- **Notes:** Document sources in _References_.

---

## 2) Mass Properties (Initial Estimates → refine as data found)
> Start with reasonable ranges and tighten as you cite sources or calibrate.

### Stage 1 (placeholders)
- **Prop mass (kg):** _85,000–100,000_  
- **Dry mass (kg):** _7,000–10,000_  
- **CG travel:** forward during burn (curve **TBD**)
- **Inertia (principal):** slender-body approximation (**TBD**)

### Stage 2 (placeholders)
- **Prop mass (kg):** _15,000–22,000_  
- **Dry mass (kg):** _1,500–2,500_  
- **CG/Inertia:** **TBD**

**Rationale:** Based on typical LOX/LCH4 vehicles of similar size; refine with public mass fraction hints or reverse-engineering from performance.

---

## 3) Propulsion (seed from chemistry codes → tune to public thrust/Isp)
### Aeon 1 (Stage 1) — Assumptions
- **Sea-level thrust (kN):** **~100** per engine _(placeholder)_  
- **Vac thrust/Isp:** **TBD**  
- **Throttle range:** assume **60–100%** (until sourced)  
- **Gimbal authority/rate:** assume **±5°**, **10–20°/s** (until sourced)

### AeonVac (Stage 2) — Assumptions
- **Vac thrust (kN):** **~120–130** _(placeholder)_  
- **Isp (s):** **~350–360** _(placeholder)_  
- **Restart:** **TBD**

**Implementation plan:**  
- Use NASA CEA (or equivalent) to seed **Thrust/Isp vs ambient pressure** for LOX/LCH4;  
- Tune curves to match public engine numbers as you find them.

Artifacts to produce:
- `/data/PropMap_v1.csv` — columns: altitude_m, p_amb_Pa, thrust_kN, Isp_s, throttle

---

## 4) Aerodynamics (OpenFOAM plan)
- **Geometry:** axisymmetric **nosecone + cylindrical body + fairing** (no fins assumed)
- **Reference area:** \( S = \pi (D/2)^2 \)
- **Flight envelope:** \( \alpha \in [-4^\circ, +8^\circ] \), Mach ∈ {0.3, 0.9, 1.1, 1.5, 2, 3, 5}
- **Modeling:** compressible RANS (e.g., **k-ω SST**), y⁺ targets appropriate for wall treatment; inflation layers; snappyHexMesh refinement
- **Transonic note:** expect higher uncertainty (±5–10%) around M≈0.9–1.2  
- **Validation breadcrumbs:**  
  - Compare subsonic Cd to slender-body/empirical correlations  
  - Document transonic shock structure via contours  
  - For hypersonic method confidence, reference double-wedge experiments (e.g., **Swantek & Austin, UIUC**) from prior work.

Artifacts to produce:
- `/data/AeroDB_v1.csv` — columns: Mach, alpha_deg, Cd, Cl, Cm

---

## 5) Environments
- **Atmosphere (truth runs):** **U.S. Standard Atmosphere 1976**  
- **Winds/density (Monte Carlo):** **Earth-GRAM** seasonal profiles for CCAFS (or equivalent climatology if GRAM unavailable)  
- **Gravity:** WGS-84 μ; Earth rotation included for inertial transforms (optional at 3-DOF stage)

---

## 6) Trajectory & GNC
- **3-DOF “truth”:** planar gravity-turn ascent with pitch program; constraints for **Max-Q** and **axial/lateral accel**  
- **6-DOF:** rigid body EOM (quaternions) with thrust-vector control (S1/S2 gimbals); basic actuator dynamics & limits  
- **Guidance:** open-loop pitch program → simple rate-command autopilot → S2 closed-loop targeting  
- **Events:** liftoff, pitchover, Max-Q, MECO, staging, fairing sep, SECO

Key plots:
- altitude/velocity/flight-path angle vs time; q and acceleration vs time; pitch/throttle schedules

---

## 7) Monte Carlo Dispersions (initial set)
- **Mass:** ±2%  
- **Thrust:** ±3%  
- **Isp:** ±2%  
- **Aerodynamics (Cd):** ±5% (amplify near transonic)  
- **Winds/density:** sampled from Earth-GRAM distributions  
- **Sensors:** IMU bias/noise (TBD)  
- **Other:** CG offset ±TBD, gimbal bias ±TBD

**Exit criteria:** 100–1000 shots; CDFs of orbit insertion errors; Max-Q distributions; constraint violation rates; sensitivity (tornado) ranking.

---

## 8) Data Artifacts & Directory Conventions
- `/data/AeroDB_v1.csv` — aerodynamic coefficients  
- `/data/PropMap_v1.csv` — propulsion map  
- `/runs/YYYY-MM-DD/NNN/` — logs, configs, plots for each run batch  
- `/docs/VnV.md` — verification/validation notes & cross-checks  
- `/docs/figures/` — PNGs: ascent, Cd(Mach), pressure contours, MC CDFs

---

## 9) Open Questions / To-Do
- [ ] Replace placeholder masses with sourced values (dry/prop for S1/S2, fairing mass)  
- [ ] Confirm fairing dimensions and separation event timing  
- [ ] Confirm AeonVac restart & throttle assumptions  
- [ ] Establish gimbal authority & rate limits (S1/S2)  
- [ ] Add heating estimates (optional CLA/thermal handoff)  
- [ ] Cite all specs in **References** and in `README.md`

---

## 10) Change Log
- YYYY-MM-DD: Initial assumptions drafted.

---

## References (to populate as you cite)
- Public Terran 1 vehicle overview/specs — **TBD link**  
- Engine public figures (Aeon 1, AeonVac) — **TBD link**  
- Launch site & mission context (LC-16) — **TBD link**  
- Atmosphere & dispersions: U.S. Standard Atmosphere 1976; Earth-GRAM — **TBD link**  
- Aerodynamics references (slender-body correlations; transonic RANS caveats) — **TBD link**
