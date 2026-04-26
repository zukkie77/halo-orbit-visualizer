from dataclasses import dataclass
from enum import Enum


class CelestialSystem(str, Enum):
    SUN_EARTH = "Sun-Earth"
    EARTH_MOON = "Earth-Moon"


@dataclass(frozen=True)
class Vector2D:
    x: float  # AU
    y: float  # AU


@dataclass(frozen=True)
class LagrangePointData:
    name: str         # "L1" | "L2" | "L3" | "L4" | "L5"
    position: Vector2D  # AU, 回転座標系（太陽=原点、地球=(1,0)）


@dataclass(frozen=True)
class OrbitParameters:
    lagrange_point_name: str
    semi_axis_x: float        # AU（視覚的誇張スケール込み）
    semi_axis_y: float        # AU
    angular_frequency: float  # rad/s
    initial_phase: float      # rad


@dataclass
class AnimationState:
    sim_time_seconds: float  # J2000エポック起算の仮想時刻（秒）
    time_multiplier: float   # 1.0〜1e9
