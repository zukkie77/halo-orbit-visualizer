import pytest
from halo_orbit_visualizer.time_manager import TimeManager


class TestTimeManager:
    def test_epoch_offset_is_non_negative(self):
        tm = TimeManager()
        assert tm.epoch_offset_seconds >= 0.0

    def test_sim_time_starts_at_epoch_offset(self):
        tm = TimeManager()
        assert tm.sim_time_seconds == tm.epoch_offset_seconds

    def test_advance_increases_sim_time(self):
        tm = TimeManager()
        before = tm.sim_time_seconds
        tm.advance(1000.0, 1.0)
        assert tm.sim_time_seconds == pytest.approx(before + 1.0)

    def test_advance_applies_multiplier(self):
        tm = TimeManager()
        before = tm.sim_time_seconds
        tm.advance(1000.0, 1_000_000.0)
        assert tm.sim_time_seconds == pytest.approx(before + 1_000_000.0)

    def test_advance_delta_ms_to_seconds_conversion(self):
        tm = TimeManager()
        before = tm.sim_time_seconds
        tm.advance(500.0, 2.0)
        # 500ms * 2x = 1.0 second
        assert tm.sim_time_seconds == pytest.approx(before + 1.0)

    def test_epoch_offset_is_read_only(self):
        tm = TimeManager()
        with pytest.raises(AttributeError):
            tm.epoch_offset_seconds = 0.0

    def test_j2000_epoch_is_year_2000(self):
        # J2000起算秒は 2000-01-01 12:00 UTC からの経過秒
        # 2026年時点で約 26年 × 365.25 × 86400 ≒ 8.2e8 秒以上あるはず
        tm = TimeManager()
        assert tm.epoch_offset_seconds > 8e8
