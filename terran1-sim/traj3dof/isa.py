"""
traj3dof.isa
------------
International Standard Atmosphere (USSA-76) utility.

This module provides a lightweight ISA implementation suitable for
launch-ascent simulations. We'll build it in blocks. **Block 1** includes:
- Module header & documentation
- Physical constants
- ISA layer definitions up to ~47 km (more layers can be added later)

All units are SI (meters, seconds, Kelvin, Pascals).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

# --- Physical constants (SI) ---
G0 = 9.80665          # m/s^2, standard gravity
R_AIR = 287.05287     # J/(kg*K), specific gas constant for dry air
GAMMA = 1.4           # cp/cv for dry air (used for speed of sound)

@dataclass(frozen=True)
class ISALayer:
    """
    One ISA layer between geometric altitudes h0 <= h < h1 with a linear
    temperature lapse rate L (K/m). At the base we store T0 (K) and p0 (Pa).
    """
    h0: float   # base geometric altitude [m]
    T0: float   # base temperature [K]
    p0: float   # base pressure [Pa]
    L: float    # lapse rate [K/m]

# --- ISA layers (USSA-76) ---
# We start with layers commonly sufficient for ascent modeling to ~47 km.
# Additional layers can be appended later when needed.
ISA_LAYERS: List[ISALayer] = [
    ISALayer(h0=0.0,     T0=288.15, p0=101325.0, L=-0.0065),  # 0–11 km (troposphere)
    ISALayer(h0=11000.0, T0=216.65, p0=22632.06, L=0.0),      # 11–20 km (tropopause, isothermal)
    ISALayer(h0=20000.0, T0=216.65, p0=5474.889, L=0.001),    # 20–32 km (stratosphere 1)
    ISALayer(h0=32000.0, T0=228.65, p0=868.019,  L=0.0028),   # 32–47 km (stratosphere 2)
    # Future extension (optional):
    # ISALayer(h0=47000.0, T0=270.65, p0=110.906, L=0.0),     # 47–51 km (isothermal)
]

def _find_layer(h_m: float) -> Tuple[ISALayer, float, int]:
    """
    Locate the ISA layer for altitude h_m. Returns (layer, h_next, idx),
    where h_next is the base altitude of the *next* layer (or +inf if none).
    This helper lets us branch on isothermal vs gradient layers cleanly later.
    """
    for i, layer in enumerate(ISA_LAYERS):
        h_next = ISA_LAYERS[i+1].h0 if i+1 < len(ISA_LAYERS) else float('inf')
        if layer.h0 <= h_m < h_next:
            return layer, h_next, i
    # If above our last defined layer, clamp to the last layer for now.
    last = ISA_LAYERS[-1]
    return last, float('inf'), len(ISA_LAYERS)-1

def _tp_in_layer(h_m: float):
    """
    Compute temperature T [K] and pressure p [Pa] at altitude h_m within the
    current ISA layer using base (T0, p0) and lapse rate L.
    """
    layer, h_next, _ = _find_layer(h_m)
    h0, T0, p0, L = layer.h0, layer.T0, layer.p0, layer.L
    dh = h_m - h0

    if abs(L) < 1e-12:
        T = T0
        p = p0 * math.exp(-G0 * dh / (R_AIR * T0))
    else:
        T = T0 + L * dh
        p = p0 * (T/T0) ** (-G0 / (R_AIR * L))

    return T, p

def isa_tp(h_m: float):
    """
    Public API (Block 2): return (T [K], p [Pa]) at altitude h_m using ISA layers.
    For now this is up to ~47 km (see ISA_LAYERS). Higher can be added later.
    """
    if h_m < 0.0:
        h_m = 0.0
    return _tp_in_layer(h_m)
