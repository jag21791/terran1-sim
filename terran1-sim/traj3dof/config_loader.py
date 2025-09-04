
"""
traj3dof.config_loader
----------------------
Load and validate simulation configuration from a repo-level config.yaml.
Also computes derived quantities (like aero reference area) and can snapshot
the active configuration to a run directory for reproducibility.
"""

from __future__ import annotations
import math
import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


DEFAULT_CONFIG_FILENAME = "config.yaml"


def _deep_update(base: dict, updates: dict) -> dict:
    """Recursively merge `updates` into `base` (in-place) and return base."""
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def _compute_ref_area(diameter_m: float) -> float:
    """Compute reference area for a circular cross-section."""
    r = diameter_m * 0.5
    return math.pi * r * r


def _ensure_derived(cfg: Dict[str, Any]) -> None:
    """Fill in derived values if missing (e.g., aero.ref_area_m2)."""
    veh = cfg.get("vehicle", {})
    aero = cfg.setdefault("aero", {})
    d = veh.get("diameter_m", None)
    if d is not None and "ref_area_m2" not in aero:
        aero["ref_area_m2"] = _compute_ref_area(float(d))


def _require(cfg: Dict[str, Any], path: str) -> Any:
    """Require a dotted path to exist in cfg; raise KeyError if missing."""
    node = cfg
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"Missing required config key: {path}")
        node = node[part]
    return node


def validate_config(cfg: Dict[str, Any]) -> None:
    """
    Minimal schema validation. Raises KeyError if a required field is missing.
    """
    required_paths = [
        "vehicle.name",
        "vehicle.diameter_m",
        "vehicle.length_m",
        "vehicle.stages",
        "vehicle.stage1.engines",
        "vehicle.stage1.prop_mass_kg",
        "vehicle.stage1.dry_mass_kg",
        "vehicle.stage1.burn_time_s",
        "vehicle.stage2.engines",
        "vehicle.stage2.prop_mass_kg",
        "vehicle.stage2.dry_mass_kg",
        "vehicle.stage2.burn_time_s",
        "mission.target_orbit.altitude_km",
        "simulation.dt_s",
        "simulation.max_time_s",
        "simulation.earth_radius_m",
        "simulation.gravity_mu",
    ]
    for p in required_paths:
        _require(cfg, p)


def load_config(
    repo_root: Optional[Path] = None,
    filename: str = DEFAULT_CONFIG_FILENAME,
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Load a YAML config from the repo root (or a provided repo_root),
    apply optional deep overrides, compute derived values, and validate.
    """
    if repo_root is None:
        # Assume repo layout: <repo>/traj3dof/config_loader.py (this file)
        repo_root = Path(__file__).resolve().parents[1]
    cfg_path = repo_root / filename
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("r") as f:
        cfg = yaml.safe_load(f) or {}

    # Optional overrides
    cfg = _deep_update(cfg, copy.deepcopy(overrides) if overrides else {})

    # Derived values (e.g., aero.ref_area_m2 from vehicle.diameter_m)
    _ensure_derived(cfg)

    # Validate minimal schema
    validate_config(cfg)

    return cfg


def snapshot_config(cfg: Dict[str, Any], run_dir: Path) -> Path:
    """
    Save a copy of the active configuration to the run directory.
    Returns the path to the snapshot file.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    snap_path = run_dir / "config.snapshot.yaml"
    with snap_path.open("w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    return snap_path
