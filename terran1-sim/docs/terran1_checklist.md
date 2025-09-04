# 🚀 Terran 1 Vehicle Simulation Project Checklist

## 0. Setup
- [ ] Create repo with folders: /aero, /prop, /mass, /traj3dof, /sim6dof, /mc, /docs, /runs
- [ ] Add `config.yaml` to root for centralized parameters
- [ ] Collect public Terran 1 specs (dimensions, thrust, Isp, payloads)

## 1. Data Pack
- [ ] Compile vehicle geometry, stage masses, thrust levels
- [ ] Record Aeon 1 & AeonVac engine performance ranges
- [ ] Define mission profile (launch site: CCAFS LC-16, target orbit ~200 km LEO)
- [ ] Document assumptions in `/docs/assumptions.md`

## 2. 3-DOF Ascent Model
- [ ] Implement mass depletion + thrust curves
- [ ] Integrate 3-DOF EOM with pitch program
- [ ] Use U.S. Std Atm (mean conditions)
- [ ] Plot nominal ascent: altitude, velocity, q, a vs time

## 3. Aero Database (OpenFOAM)
- [ ] Build approximate Terran 1 geometry (nosecone + cylinder + fairing)
- [ ] Mesh with snappyHexMesh (refine BL layers)
- [ ] Run CFD cases: Mach 0.3, 0.9, 1.1, 2, 3, 5; α = -4°…+8°
- [ ] Output Cd/Cl/Cm vs Mach, α into `AeroDB_v1.csv`

## 4. Propulsion Maps
- [ ] Use NASA CEA or tabulated numbers to seed T/Isp vs altitude
- [ ] Run axisymmetric nozzle CFD in OpenFOAM
- [ ] Generate thrust coefficient vs ambient pressure
- [ ] Save results into `PropMap_v1.csv`

## 5. 6-DOF & GNC
- [ ] Build rigid-body 6-DOF EOM (quaternions)
- [ ] Add thrust vector control model (gimbal limits, dynamics)
- [ ] Implement simple autopilot (PID or LQR) and pitch schedule tracker
- [ ] Run closed-loop ascent with AeroDB and PropMap

## 6. Monte Carlo Campaign
- [ ] Integrate Earth-GRAM atmospheric profiles for dispersions
- [ ] Define uncertainties: thrust ±3%, mass ±2%, Isp ±2%, Cd ±5%
- [ ] Run 100–1000 Monte Carlo cases
- [ ] Generate CDFs for orbit insertion, Max-Q distributions, tornado plots

## 7. Reporting
- [ ] One-pager mission summary (payload, margins, constraints)
- [ ] Aero/prop plots with pressure contours
- [ ] Monte Carlo outcomes (success rates, sensitivities)
- [ ] Recommendations for fidelity improvements
