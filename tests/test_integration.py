import matplotlib
matplotlib.use("Agg")

import pytest
from halo_orbit_visualizer.physics import LagrangePointCalculator, OrbitCalculator
from halo_orbit_visualizer.time_manager import TimeManager
from halo_orbit_visualizer.types import CelestialSystem
from halo_orbit_visualizer.ui import SpeedControlUI, SystemSwitchUI, VisualizationView
from halo_orbit_visualizer.animation import AnimationController


class TestIntegration:
    def setup_method(self):
        self.lp_calc = LagrangePointCalculator()
        self.orbit_calc = OrbitCalculator()
        self.time_mgr = TimeManager()
        self.lagrange_points = self.lp_calc.compute_all()
        self.orbit_params = self.orbit_calc.compute_parameters(
            self.lagrange_points, self.time_mgr.epoch_offset_seconds
        )

    def test_initialization_sequence_completes(self):
        assert len(self.lagrange_points) == 5
        assert len(self.orbit_params) == 5

    def test_animation_controller_start_returns_func_animation(self):
        from matplotlib.animation import FuncAnimation
        view = VisualizationView()
        fig, _ = view.setup(self.lagrange_points, self.orbit_params)
        speed_ui = SpeedControlUI()
        ctrl = AnimationController()
        anim = ctrl.start(
            fig=fig,
            orbit_params=self.orbit_params,
            lagrange_positions=self.lagrange_points,
            time_manager=self.time_mgr,
            orbit_calculator=self.orbit_calc,
            view=view,
            speed_ui=speed_ui,
        )
        assert isinstance(anim, FuncAnimation)
        import matplotlib.pyplot as plt
        plt.close("all")

    def test_update_frame_returns_non_empty_artist_list(self):
        view = VisualizationView()
        fig, _ = view.setup(self.lagrange_points, self.orbit_params)
        speed_ui = SpeedControlUI()
        ctrl = AnimationController()
        ctrl.start(
            fig=fig,
            orbit_params=self.orbit_params,
            lagrange_positions=self.lagrange_points,
            time_manager=self.time_mgr,
            orbit_calculator=self.orbit_calc,
            view=view,
            speed_ui=speed_ui,
        )
        artists = ctrl._update_frame(0)
        assert len(artists) == 5
        import matplotlib.pyplot as plt
        plt.close("all")

    def test_system_switch_updates_orbit_params(self):
        view = VisualizationView()
        fig, ax = view.setup(self.lagrange_points, self.orbit_params, CelestialSystem.SUN_EARTH)
        speed_ui = SpeedControlUI()
        system_switch_ui = SystemSwitchUI()
        ctrl = AnimationController()
        ctrl.start(
            fig=fig,
            orbit_params=self.orbit_params,
            lagrange_positions=self.lagrange_points,
            time_manager=self.time_mgr,
            orbit_calculator=self.orbit_calc,
            view=view,
            speed_ui=speed_ui,
            ax=ax,
            system_switch_ui=system_switch_ui,
            lp_calculator=self.lp_calc,
            system=CelestialSystem.SUN_EARTH,
        )
        se_freq = ctrl._orbit_params[0].angular_frequency
        ctrl._on_system_switch(CelestialSystem.EARTH_MOON.value)
        em_freq = ctrl._orbit_params[0].angular_frequency
        assert se_freq != em_freq
        assert ctrl._current_system == CelestialSystem.EARTH_MOON
        assert ctrl._pending_redraw is not None
        import matplotlib.pyplot as plt
        plt.close("all")
