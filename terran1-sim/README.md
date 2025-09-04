# Terran 1 Vehicle Simulation

End-to-end simulation workflow for Relativity Space's **Terran 1** (public-spec approximation): 3‑DOF ascent → CFD‑based aero database (OpenFOAM) → propulsion maps → 6‑DOF + GNC → Monte Carlo dispersions.

> Portfolio project using public information only. No proprietary data.

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

## Results
Add key figures:
- Nominal ascent (altitude/velocity/q vs time)
- Cd vs Mach from OpenFOAM
- Monte Carlo CDFs and tornado plots

## License

