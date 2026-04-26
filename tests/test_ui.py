import pytest
import matplotlib
matplotlib.use("Agg")  # ヘッドレス環境でのテスト用
from halo_orbit_visualizer.ui import SpeedControlUI, SystemSwitchUI
from halo_orbit_visualizer.types import CelestialSystem


class TestSpeedControlUI:
    def setup_method(self):
        self.ui = SpeedControlUI()

    def test_get_multiplier_at_zero_returns_one(self):
        assert self.ui.get_multiplier(0.0) == pytest.approx(1.0)

    def test_get_multiplier_at_six_returns_million(self):
        assert self.ui.get_multiplier(6.0) == pytest.approx(1_000_000.0)

    def test_get_multiplier_at_nine_returns_billion(self):
        assert self.ui.get_multiplier(9.0) == pytest.approx(1e9)

    def test_get_multiplier_at_three(self):
        assert self.ui.get_multiplier(3.0) == pytest.approx(1000.0)

    def test_slider_min_max_default(self):
        assert SpeedControlUI.SLIDER_MIN == 0.0
        assert SpeedControlUI.SLIDER_MAX == 9.0
        assert SpeedControlUI.SLIDER_DEFAULT == 6.0


class TestSystemSwitchUI:
    def test_labels_match_celestial_systems(self):
        labels = SystemSwitchUI.LABELS
        assert CelestialSystem.SUN_EARTH.value in labels
        assert CelestialSystem.EARTH_MOON.value in labels

    def test_label_count(self):
        assert len(SystemSwitchUI.LABELS) == 2
