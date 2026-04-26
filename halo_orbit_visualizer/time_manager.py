import sys
from datetime import datetime, timezone

# J2000.0 エポック = 2000-01-01 12:00:00 UTC
_J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class TimeManager:
    def __init__(self) -> None:
        try:
            now = datetime.now(timezone.utc)
            self._epoch_offset: float = (now - _J2000).total_seconds()
        except Exception:
            print("Warning: failed to get system time; using epoch offset 0", file=sys.stderr)
            self._epoch_offset = 0.0
        self._sim_time: float = self._epoch_offset

    @property
    def epoch_offset_seconds(self) -> float:
        return self._epoch_offset

    @property
    def sim_time_seconds(self) -> float:
        return self._sim_time

    def advance(self, real_delta_ms: float, multiplier: float) -> None:
        self._sim_time += (real_delta_ms / 1000.0) * multiplier
