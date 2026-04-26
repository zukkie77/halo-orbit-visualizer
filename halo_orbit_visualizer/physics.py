import math
from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from .types import CelestialSystem, LagrangePointData, OrbitParameters, Vector2D


@dataclass(frozen=True)
class SystemConfig:
    name: str
    mu: float                    # secondary / (primary + secondary)
    omega: float                 # orbital angular frequency (rad/s)
    primary_label: str
    secondary_label: str
    primary_color: str
    secondary_color: str
    primary_markersize: float
    secondary_markersize: float
    unit_label: str
    axis_limit: float
    orbit_scale: float
    freq_multiplier_l1l2: float  # ω_halo / ω_orbit for L1/L2 (CR3BP approximation)


SYSTEM_CONFIGS: Dict[CelestialSystem, SystemConfig] = {
    CelestialSystem.SUN_EARTH: SystemConfig(
        name="Sun-Earth",
        mu=3.003e-6,
        omega=2 * math.pi / (365.25 * 86400),
        primary_label="Sun",
        secondary_label="Earth",
        primary_color="#FFD700",
        secondary_color="#4488FF",
        primary_markersize=20,
        secondary_markersize=10,
        unit_label="AU",
        axis_limit=1.6,
        orbit_scale=0.08,
        freq_multiplier_l1l2=2.09,
    ),
    CelestialSystem.EARTH_MOON: SystemConfig(
        name="Earth-Moon",
        mu=0.01215,
        omega=2 * math.pi / (27.32 * 86400),
        primary_label="Earth",
        secondary_label="Moon",
        primary_color="#4488FF",
        secondary_color="#CCCCCC",
        primary_markersize=15,
        secondary_markersize=8,
        unit_label="EM units",
        axis_limit=1.6,
        orbit_scale=0.08,
        freq_multiplier_l1l2=2.09,
    ),
}

_K_L1L2 = 1.0 / 2.36  # L1/L2 楕円の y/x 軸比


class LagrangePointCalculator:
    def compute_all(
        self,
        system: CelestialSystem = CelestialSystem.SUN_EARTH,
    ) -> List[LagrangePointData]:
        """L1〜L5の5点を返す。一次天体=原点、二次天体=(1,0) の回転座標系。"""
        mu = SYSTEM_CONFIGS[system].mu
        r_hill = (mu / 3) ** (1 / 3)

        return [
            LagrangePointData("L1", Vector2D(1.0 - r_hill, 0.0)),
            LagrangePointData("L2", Vector2D(1.0 + r_hill, 0.0)),
            LagrangePointData("L3", Vector2D(-(1.0 + 5 * mu / 12), 0.0)),
            LagrangePointData("L4", Vector2D(0.5, math.sqrt(3) / 2)),
            LagrangePointData("L5", Vector2D(0.5, -math.sqrt(3) / 2)),
        ]


class OrbitCalculator:
    def compute_parameters(
        self,
        lagrange_points: List[LagrangePointData],
        epoch_offset_seconds: float,
        system: CelestialSystem = CelestialSystem.SUN_EARTH,
    ) -> List[OrbitParameters]:
        config = SYSTEM_CONFIGS[system]
        omega = config.omega
        fm = config.freq_multiplier_l1l2
        scale = config.orbit_scale

        freq_map = {
            "L1": fm * omega,
            "L2": fm * omega,
            "L3": omega,
            "L4": omega,
            "L5": omega,
        }

        result = []
        for lp in lagrange_points:
            freq = freq_map[lp.name]
            initial_phase = (freq * epoch_offset_seconds) % (2 * math.pi)
            ax = scale
            ay = scale * _K_L1L2 if lp.name in ("L1", "L2") else scale
            result.append(OrbitParameters(
                lagrange_point_name=lp.name,
                semi_axis_x=ax,
                semi_axis_y=ay,
                angular_frequency=freq,
                initial_phase=initial_phase,
            ))
        return result

    def compute_position(
        self,
        params: OrbitParameters,
        sim_time_seconds: float,
    ) -> Vector2D:
        """ラグランジュポイントからの相対位置を返す。"""
        angle = params.angular_frequency * sim_time_seconds + params.initial_phase
        return Vector2D(
            x=params.semi_axis_x * math.cos(angle),
            y=params.semi_axis_y * math.sin(angle),
        )
