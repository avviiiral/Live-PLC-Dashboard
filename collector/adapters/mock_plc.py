import threading
import time
from collector.core.types import PLCConfig, TagConfig


class MockPLCAdapter:
    """Offline simulator for the Middle Testing MW tag set.

    Each adapter instance owns its own clock and result-cycle state, matching
    the independent re-arm state of each physical PLC. Values are synthetic
    test data and must never be represented as live machine measurements.
    """

    CYCLE_SECONDS = 10.0

    def __init__(self, values=None, plc_config: PLCConfig | None = None):
        self.values = dict(values) if values is not None else None
        self.plc_config = plc_config
        self.connected = False
        self.lock = threading.Lock()
        self.started_at = None

    def connect(self):
        self.connected = True
        if self.started_at is None:
            self.started_at = time.monotonic()

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def _simulation_snapshot(self):
        if self.started_at is None:
            self.started_at = time.monotonic()

        elapsed = max(0.0, time.monotonic() - self.started_at)
        cycle = int(elapsed // self.CYCLE_SECONDS)
        phase = elapsed % self.CYCLE_SECONDS

        # Match the supplied logger's sequence: zero arms; 3 is informational;
        # 1 or 2 emits one event; zero returns before the next cycle.
        if phase < 2.0:
            result = 0
        elif phase < 4.0:
            result = 3
        elif phase < 6.0:
            result = 1 if cycle % 2 == 0 else 2
        else:
            result = 0

        # Distinguish the two simulated PLCs without implying calibrated values.
        plc_offset = 0
        if self.plc_config:
            plc_offset = sum(ord(char) for char in self.plc_config.host) % 7

        return {
            "Coil_Short_MW3008": 0,
            "Continuity_ON_MW412": 1,
            "Aging_Test_MW410": 1,
            "Coil_to_Cont_COM_MW4004": 1,
            "Coil_to_Cont_NO_MW4002": 1,
            "Diode_Test_MW5026": 1,
            "Start_Time_MW438": 120 + cycle + plc_offset,
            "Pull_In_MW422": 80 + (cycle % 5) + plc_offset,
            "Drop_Out_V_MW424": 24 + (cycle % 3),
            "Coil_Resistance_MW426": 150 + (cycle % 11) + plc_offset,
            "Result_MW3112": result,
        }

    def read(self, tag: TagConfig):
        if not self.connected:
            raise ConnectionError("Mock PLC disconnected")

        with self.lock:
            if self.values is not None:
                if tag.name not in self.values:
                    raise KeyError(tag.name)
                value = self.values[tag.name]
            elif self.plc_config is not None:
                snapshot = self._simulation_snapshot()
                if tag.name not in snapshot:
                    raise KeyError(
                        f"Unsupported simulated tag {tag.name!r}; "
                        "check the Middle Testing tag configuration."
                    )
                value = snapshot[tag.name]
            else:
                raise KeyError(
                    f"No mock value configured for {tag.name!r}. "
                    "Pass explicit values or a PLCConfig for simulation."
                )

        return (
            value * tag.scale + tag.offset
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            else value
        )

    def set_value(self, name, value):
        with self.lock:
            if self.values is None:
                self.values = self._simulation_snapshot()
            self.values[name] = value
