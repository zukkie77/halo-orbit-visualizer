import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import RadioButtons, Slider

from .physics import SYSTEM_CONFIGS
from .types import CelestialSystem, LagrangePointData, OrbitParameters, Vector2D

_LP_COLORS = {
    "L1": "#e74c3c",
    "L2": "#3498db",
    "L3": "#2ecc71",
    "L4": "#f39c12",
    "L5": "#9b59b6",
}


class VisualizationView:
    def __init__(self) -> None:
        self._markers: Dict[str, plt.Line2D] = {}

    def setup(
        self,
        lagrange_points: List[LagrangePointData],
        orbit_params: List[OrbitParameters],
        system: CelestialSystem = CelestialSystem.SUN_EARTH,
    ) -> Tuple[Figure, Axes]:
        fig, ax = plt.subplots(figsize=(9, 9))
        plt.subplots_adjust(bottom=0.20)

        fig.patch.set_facecolor("#0a0a1a")
        ax.set_facecolor("#0a0a1a")

        self._draw_content(ax, lagrange_points, orbit_params, system)

        fig.canvas.mpl_connect("close_event", lambda _: plt.close("all"))
        return fig, ax

    def redraw(
        self,
        ax: Axes,
        lagrange_points: List[LagrangePointData],
        orbit_params: List[OrbitParameters],
        system: CelestialSystem = CelestialSystem.SUN_EARTH,
    ) -> List[Artist]:
        """システム切り替え時にAxesを再描画し、新しいマーカーリストを返す。"""
        ax.cla()
        ax.set_facecolor("#0a0a1a")
        self._markers.clear()
        self._draw_content(ax, lagrange_points, orbit_params, system)
        return list(self._markers.values())

    def _draw_content(
        self,
        ax: Axes,
        lagrange_points: List[LagrangePointData],
        orbit_params: List[OrbitParameters],
        system: CelestialSystem,
    ) -> None:
        config = SYSTEM_CONFIGS[system]

        ax.set_aspect("equal")
        ax.set_xlim(-config.axis_limit, config.axis_limit)
        ax.set_ylim(-config.axis_limit, config.axis_limit)
        ax.set_xlabel(f"X ({config.unit_label})", color="white")
        ax.set_ylabel(f"Y ({config.unit_label})", color="white")
        ax.set_title(
            f"Halo Orbit Visualizer — {config.name} System\n"
            "[1] Sun-Earth  [2] Earth-Moon",
            color="white",
            fontsize=10,
        )
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333355")

        # 一次天体（太陽 / 地球）
        ax.plot(
            0, 0, "o",
            color=config.primary_color,
            markersize=config.primary_markersize,
            label=config.primary_label,
            zorder=5,
        )
        # 二次天体の公転参考円
        theta = np.linspace(0, 2 * math.pi, 360)
        ax.plot(np.cos(theta), np.sin(theta), "--", color="#334466", linewidth=0.8, zorder=1)
        # 二次天体（地球 / 月）
        ax.plot(
            1, 0, "o",
            color=config.secondary_color,
            markersize=config.secondary_markersize,
            label=config.secondary_label,
            zorder=5,
        )

        lp_map = {lp.name: lp for lp in lagrange_points}
        for params in orbit_params:
            lp = lp_map[params.lagrange_point_name]
            color = _LP_COLORS[lp.name]
            orbit_theta = np.linspace(0, 2 * math.pi, 360)
            ox = lp.position.x + params.semi_axis_x * np.cos(orbit_theta)
            oy = lp.position.y + params.semi_axis_y * np.sin(orbit_theta)
            ax.plot(ox, oy, "-", color=color, linewidth=0.7, alpha=0.4, zorder=2)
            ax.plot(
                lp.position.x, lp.position.y,
                "+", color=color, markersize=10, markeredgewidth=1.5,
                label=lp.name, zorder=4,
            )
            (marker,) = ax.plot(
                lp.position.x, lp.position.y,
                "o", color=color, markersize=6, zorder=6,
            )
            self._markers[lp.name] = marker

        ax.legend(loc="upper right", facecolor="#111133", labelcolor="white", fontsize=8)

    def update_markers(
        self,
        positions: List[Tuple[str, Vector2D]],
    ) -> List[Artist]:
        updated: List[Artist] = []
        for name, pos in positions:
            marker = self._markers[name]
            marker.set_data([pos.x], [pos.y])
            updated.append(marker)
        return updated


class SpeedControlUI:
    SLIDER_MIN: float = 0.0
    SLIDER_MAX: float = 9.0
    SLIDER_DEFAULT: float = 6.0

    def setup(self, fig: Figure) -> Slider:
        ax_slider = fig.add_axes([0.22, 0.08, 0.62, 0.03])
        ax_slider.set_facecolor("#1a1a2e")
        slider = Slider(
            ax_slider,
            label="Speed (log₁₀)",
            valmin=self.SLIDER_MIN,
            valmax=self.SLIDER_MAX,
            valinit=self.SLIDER_DEFAULT,
            color="#4488cc",
        )
        slider.label.set_color("white")
        slider.valtext.set_color("white")
        self.update_label(slider, self.get_multiplier(self.SLIDER_DEFAULT))
        return slider

    def get_multiplier(self, slider_value: float) -> float:
        return 10.0 ** slider_value

    def update_label(self, slider: Slider, multiplier: float) -> None:
        exp = int(round(math.log10(multiplier))) if multiplier >= 1 else 0
        slider.valtext.set_text(f"×10^{exp}")


class SystemSwitchUI:
    LABELS: List[str] = [s.value for s in CelestialSystem]

    def setup(self, fig: Figure) -> RadioButtons:
        ax_radio = fig.add_axes([0.01, 0.04, 0.14, 0.11])
        ax_radio.set_facecolor("#1a1a2e")
        radio = RadioButtons(
            ax_radio,
            self.LABELS,
            activecolor="#4488cc",
        )
        for label in radio.labels:
            label.set_color("white")
            label.set_fontsize(8)
        return radio
