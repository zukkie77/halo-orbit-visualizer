import math
import pytest
from halo_orbit_visualizer.physics import LagrangePointCalculator, OrbitCalculator
from halo_orbit_visualizer.types import CelestialSystem


class TestLagrangePointCalculator:
    def setup_method(self):
        self.calc = LagrangePointCalculator()

    def test_returns_five_points(self):
        points = self.calc.compute_all()
        assert len(points) == 5

    def test_names_are_l1_through_l5(self):
        points = self.calc.compute_all()
        names = [p.name for p in points]
        assert names == ["L1", "L2", "L3", "L4", "L5"]

    def test_l1_is_between_sun_and_earth(self):
        points = {p.name: p for p in self.calc.compute_all()}
        # L1 は太陽(x=0)と地球(x=1)の間
        assert 0 < points["L1"].position.x < 1
        assert abs(points["L1"].position.y) < 0.01

    def test_l2_is_beyond_earth(self):
        points = {p.name: p for p in self.calc.compute_all()}
        # L2 は地球(x=1)より遠い
        assert points["L2"].position.x > 1
        assert abs(points["L2"].position.y) < 0.01

    def test_l3_is_on_opposite_side_of_sun(self):
        points = {p.name: p for p in self.calc.compute_all()}
        # L3 は太陽(x=0)の反対側（x<0）
        assert points["L3"].position.x < 0
        assert abs(points["L3"].position.y) < 0.01

    def test_l4_l5_form_equilateral_triangle_with_sun_and_earth(self):
        points = {p.name: p for p in self.calc.compute_all()}
        # L4・L5 は太陽・地球から 1 AU 離れた正三角形配置
        sun = (0.0, 0.0)
        earth = (1.0, 0.0)
        for name in ("L4", "L5"):
            lp = points[name]
            dist_from_sun = math.sqrt(lp.position.x**2 + lp.position.y**2)
            dist_from_earth = math.sqrt(
                (lp.position.x - 1.0) ** 2 + lp.position.y**2
            )
            assert abs(dist_from_sun - 1.0) < 1e-6, f"{name} not 1 AU from Sun"
            assert abs(dist_from_earth - 1.0) < 1e-6, f"{name} not 1 AU from Earth"

    def test_l4_has_positive_y(self):
        points = {p.name: p for p in self.calc.compute_all()}
        assert points["L4"].position.y > 0

    def test_l5_has_negative_y(self):
        points = {p.name: p for p in self.calc.compute_all()}
        assert points["L5"].position.y < 0

    def test_l1_l2_are_equidistant_from_earth(self):
        points = {p.name: p for p in self.calc.compute_all()}
        d1 = abs(1.0 - points["L1"].position.x)
        d2 = abs(points["L2"].position.x - 1.0)
        assert abs(d1 - d2) < 1e-4


class TestOrbitCalculator:
    def setup_method(self):
        self.lp_calc = LagrangePointCalculator()
        self.orbit_calc = OrbitCalculator()
        self.lp = self.lp_calc.compute_all()

    def test_returns_five_orbit_parameters(self):
        params = self.orbit_calc.compute_parameters(self.lp, 0.0)
        assert len(params) == 5

    def test_orbit_params_names_match_lagrange_points(self):
        params = self.orbit_calc.compute_parameters(self.lp, 0.0)
        names = [p.lagrange_point_name for p in params]
        assert set(names) == {"L1", "L2", "L3", "L4", "L5"}

    def test_compute_position_is_deterministic(self):
        params = self.orbit_calc.compute_parameters(self.lp, 0.0)
        for p in params:
            pos1 = self.orbit_calc.compute_position(p, 1000.0)
            pos2 = self.orbit_calc.compute_position(p, 1000.0)
            assert pos1.x == pos2.x
            assert pos1.y == pos2.y

    def test_compute_position_is_periodic(self):
        params = {p.lagrange_point_name: p for p in self.orbit_calc.compute_parameters(self.lp, 0.0)}
        for name, p in params.items():
            period = 2 * math.pi / p.angular_frequency
            pos0 = self.orbit_calc.compute_position(p, 0.0)
            pos1 = self.orbit_calc.compute_position(p, period)
            assert abs(pos0.x - pos1.x) < 1e-6, f"{name} x not periodic"
            assert abs(pos0.y - pos1.y) < 1e-6, f"{name} y not periodic"

    def test_orbit_sizes_are_visible(self):
        params = self.orbit_calc.compute_parameters(self.lp, 0.0)
        for p in params:
            assert p.semi_axis_x > 0.001, f"{p.lagrange_point_name} orbit too small"
            assert p.semi_axis_y > 0.001, f"{p.lagrange_point_name} orbit too small"


class TestEarthMoonSystem:
    def setup_method(self):
        self.calc = LagrangePointCalculator()
        self.orbit_calc = OrbitCalculator()
        self.lp = self.calc.compute_all(CelestialSystem.EARTH_MOON)

    def test_returns_five_points(self):
        assert len(self.lp) == 5

    def test_l1_between_earth_and_moon(self):
        points = {p.name: p for p in self.lp}
        # Earth-Moon系: 地球(x=0), 月(x=1)
        assert 0 < points["L1"].position.x < 1

    def test_l2_beyond_moon(self):
        points = {p.name: p for p in self.lp}
        assert points["L2"].position.x > 1

    def test_l1_hill_sphere_larger_than_sun_earth(self):
        se_lp = {p.name: p for p in self.calc.compute_all(CelestialSystem.SUN_EARTH)}
        em_lp = {p.name: p for p in self.lp}
        # Earth-Moon の μ が大きいため Hill sphere 半径も大きい
        se_dist = abs(1.0 - se_lp["L1"].position.x)
        em_dist = abs(1.0 - em_lp["L1"].position.x)
        assert em_dist > se_dist

    def test_l4_l5_equilateral_triangle(self):
        points = {p.name: p for p in self.lp}
        for name in ("L4", "L5"):
            lp = points[name]
            dist_from_primary = math.sqrt(lp.position.x**2 + lp.position.y**2)
            dist_from_secondary = math.sqrt(
                (lp.position.x - 1.0) ** 2 + lp.position.y**2
            )
            assert abs(dist_from_primary - 1.0) < 1e-6
            assert abs(dist_from_secondary - 1.0) < 1e-6

    def test_orbit_frequency_different_from_sun_earth(self):
        se_lp = self.calc.compute_all(CelestialSystem.SUN_EARTH)
        se_params = {p.lagrange_point_name: p
                     for p in self.orbit_calc.compute_parameters(se_lp, 0.0, CelestialSystem.SUN_EARTH)}
        em_params = {p.lagrange_point_name: p
                     for p in self.orbit_calc.compute_parameters(self.lp, 0.0, CelestialSystem.EARTH_MOON)}
        # 月の公転周期は約27日、地球の公転は365日なので L1 の周波数が異なる
        assert em_params["L1"].angular_frequency != se_params["L1"].angular_frequency

    def test_orbit_periodicity_earth_moon(self):
        params = {p.lagrange_point_name: p
                  for p in self.orbit_calc.compute_parameters(self.lp, 0.0, CelestialSystem.EARTH_MOON)}
        for name, p in params.items():
            period = 2 * math.pi / p.angular_frequency
            pos0 = self.orbit_calc.compute_position(p, 0.0)
            pos1 = self.orbit_calc.compute_position(p, period)
            assert abs(pos0.x - pos1.x) < 1e-6, f"EM {name} x not periodic"
            assert abs(pos0.y - pos1.y) < 1e-6, f"EM {name} y not periodic"
