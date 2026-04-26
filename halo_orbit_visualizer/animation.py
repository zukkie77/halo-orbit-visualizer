from typing import List, Optional, Tuple

from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .physics import OrbitCalculator, SYSTEM_CONFIGS
from .time_manager import TimeManager
from .types import CelestialSystem, LagrangePointData, OrbitParameters, Vector2D
from .ui import SpeedControlUI, SystemSwitchUI, VisualizationView


class AnimationController:
    FRAME_INTERVAL_MS: int = 50

    def start(
        self,
        fig: Figure,
        orbit_params: List[OrbitParameters],
        lagrange_positions: List[LagrangePointData],
        time_manager: TimeManager,
        orbit_calculator: OrbitCalculator,
        view: VisualizationView,
        speed_ui: SpeedControlUI,
        ax: Optional[Axes] = None,
        system_switch_ui: Optional[SystemSwitchUI] = None,
        lp_calculator=None,
        system: Optional[CelestialSystem] = None,
    ) -> FuncAnimation:
        self._fig = fig
        self._ax = ax
        self._time_manager = time_manager
        self._orbit_calculator = orbit_calculator
        self._orbit_params = orbit_params
        self._lp_map = {lp.name: lp for lp in lagrange_positions}
        self._view = view
        self._lp_calc = lp_calculator
        self._current_system = system or CelestialSystem.SUN_EARTH
        self._pending_redraw: Optional[Tuple] = None
        self._multiplier: float = speed_ui.get_multiplier(SpeedControlUI.SLIDER_DEFAULT)

        def on_speed_change(val: float) -> None:
            self._multiplier = speed_ui.get_multiplier(val)
            speed_ui.update_label(self._slider, self._multiplier)

        self._slider = speed_ui.setup(fig)
        self._slider.on_changed(on_speed_change)

        self._radio = None
        if system_switch_ui is not None and ax is not None and lp_calculator is not None:
            self._radio = system_switch_ui.setup(fig)
            self._radio.on_clicked(self._on_system_switch)
            # キーボードショートカット: 1=Sun-Earth, 2=Earth-Moon
            fig.canvas.mpl_connect("key_press_event", self._on_key_press)

        anim = FuncAnimation(
            fig,
            self._update_frame,
            interval=self.FRAME_INTERVAL_MS,
            blit=False,
            cache_frame_data=False,
        )
        return anim

    def _on_key_press(self, event) -> None:
        key_map = {
            "1": CelestialSystem.SUN_EARTH,
            "2": CelestialSystem.EARTH_MOON,
        }
        if event.key in key_map:
            target = key_map[event.key]
            if self._radio is not None:
                self._radio.set_active(list(CelestialSystem).index(target))
            self._on_system_switch(target.value)

    def _on_system_switch(self, label: str) -> None:
        system = CelestialSystem(label)
        if system == self._current_system:
            return
        self._current_system = system
        lagrange_points = self._lp_calc.compute_all(system)
        orbit_params = self._orbit_calculator.compute_parameters(
            lagrange_points, self._time_manager.epoch_offset_seconds, system
        )
        self._orbit_params = orbit_params
        self._lp_map = {lp.name: lp for lp in lagrange_points}
        self._pending_redraw = (lagrange_points, orbit_params, system)

    def _update_frame(self, frame: int) -> list:
        if self._pending_redraw is not None:
            lagrange_points, orbit_params, system = self._pending_redraw
            self._pending_redraw = None
            return self._view.redraw(self._ax, lagrange_points, orbit_params, system)

        self._time_manager.advance(self.FRAME_INTERVAL_MS, self._multiplier)
        t = self._time_manager.sim_time_seconds
        positions = []
        for params in self._orbit_params:
            lp = self._lp_map[params.lagrange_point_name]
            rel = self._orbit_calculator.compute_position(params, t)
            positions.append((
                params.lagrange_point_name,
                Vector2D(x=lp.position.x + rel.x, y=lp.position.y + rel.y),
            ))
        return self._view.update_markers(positions)
