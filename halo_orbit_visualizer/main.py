import matplotlib
matplotlib.use("TkAgg")  # Ubuntu デスクトップ向けバックエンド

import matplotlib.pyplot as plt

from .animation import AnimationController
from .physics import LagrangePointCalculator, OrbitCalculator
from .time_manager import TimeManager
from .types import CelestialSystem
from .ui import SpeedControlUI, SystemSwitchUI, VisualizationView


def main() -> None:
    lp_calc = LagrangePointCalculator()
    orbit_calc = OrbitCalculator()
    time_mgr = TimeManager()

    system = CelestialSystem.SUN_EARTH
    lagrange_points = lp_calc.compute_all(system)
    orbit_params = orbit_calc.compute_parameters(
        lagrange_points, time_mgr.epoch_offset_seconds, system
    )

    view = VisualizationView()
    fig, ax = view.setup(lagrange_points, orbit_params, system)

    speed_ui = SpeedControlUI()
    system_switch_ui = SystemSwitchUI()
    ctrl = AnimationController()
    _anim = ctrl.start(
        fig=fig,
        orbit_params=orbit_params,
        lagrange_positions=lagrange_points,
        time_manager=time_mgr,
        orbit_calculator=orbit_calc,
        view=view,
        speed_ui=speed_ui,
        ax=ax,
        system_switch_ui=system_switch_ui,
        lp_calculator=lp_calc,
        system=system,
    )

    plt.show()


if __name__ == "__main__":
    main()
