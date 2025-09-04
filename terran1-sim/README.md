# Terran 1 Vehicle Simulation

End-to-end simulation workflow for Relativity Space's **Terran 1** (public-spec approximation): 3‑DOF ascent → CFD‑based aero database (OpenFOAM) → propulsion maps → 6‑DOF + GNC → Monte Carlo dispersions.

> Educational/portfolio project using public information only. No proprietary data.

## Goals
- Build a reproducible **vehicle simulation stack**: trajectory, aerodynamics, propulsion, guidance & control.
- Quantify **performance & sensitivity** with Monte Carlo (winds/density/vehicle dispersions).
- Show professional **V&V breadcrumbs**, assumptions, and clear plots.

## Repo Layout
```
terran1-sim/
  README.md
  config.yaml
  /data/         # Vehicle specs, AeroDB.csv, PropMap.csv
  /traj3dof/     # 3-DOF ascent model
  /sim6dof/      # 6-DOF + GNC
  /aero/         # OpenFOAM external aero cases
  /prop/         # CEA inputs + nozzle CFD
  /mass/         # Mass properties, CG, inertia
  /env/          # Atmosphere models, dispersions
  /mc/           # Monte Carlo runners & results
  /docs/         # Assumptions, V&V notes, figures
  /runs/         # Timestamped run artifacts
```

## Getting Started
1. **Clone** this repo, create a virtual environment (optional), and install any Python deps you add later.
2. Review **`config.yaml`** – it centralizes vehicle & mission parameters.
3. Start with **`/traj3dof`** for a nominal ascent, then replace placeholder aero with **`/aero`** results.
4. Integrate **PropMap** and move to **6‑DOF + GNC**, then run **Monte Carlo**.

## Files to Look At First
- [`config.yaml`](./config.yaml) – vehicle/mission configuration.
- [`/docs/assumptions.md`](./docs/assumptions.md) – decisions & ranges.
- [`/data/`](./data/) – put your `AeroDB_v1.csv` and `PropMap_v1.csv` here.

## Results (update as you go)
Add key figures:
- Nominal ascent (altitude/velocity/q vs time)
- Cd vs Mach from OpenFOAM
- Monte Carlo CDFs and tornado plots

## License
MIT (or your preferred license)
