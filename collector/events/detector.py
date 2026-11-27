import time
import uuid
from datetime import datetime, timezone


class ProductionEventDetector:
    """Emit one production event per armed trigger cycle.

    The default mode supports boolean active-high/active-low triggers. Numeric
    result registers can use active_values=[1, 2] and rearm_value=0, matching
    the Middle Testing Siemens logger: zero arms the detector, then PASS/FAIL
    is captured once until the next zero.
    """

    def __init__(
        self,
        trigger_tag,
        active_value=True,
        debounce_ms=100,
        result_tag=None,
        result_mapping=None,
        active_values=None,
        rearm_value=None,
    ):
        self.tag = trigger_tag
        self.active_value = active_value
        self.active_values = set(active_values) if active_values is not None else None
        self.rearm_value = rearm_value
        self.debounce = max(0, debounce_ms) / 1000
        self.result_tag = result_tag
        self.mapping = result_mapping or {"true": "PASS", "false": "FAIL"}
        self.armed = rearm_value is None
        self.active = False
        self.started = None
        self.candidate = None
        self.emitted = False

    def _event(self, values, trigger_value):
        result = values.get(self.result_tag) if self.result_tag else trigger_value
        status = self.mapping.get(str(result).lower(), "UNKNOWN")
        return {
            "id": str(uuid.uuid4()),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "result_status": status,
            "payload": dict(values),
        }

    def update(self, values):
        if self.tag not in values:
            return None

        value = values[self.tag]
        now = time.monotonic()

        if self.rearm_value is not None:
            if value == self.rearm_value:
                self.armed = True
                self.candidate = None
                self.started = None
                self.emitted = False
                return None

            is_active = value in (self.active_values or set())
            if not is_active or not self.armed:
                self.candidate = None
                self.started = None
                return None

            if value != self.candidate:
                self.candidate = value
                self.started = now

            if self.started is not None and now - self.started >= self.debounce:
                self.armed = False
                self.emitted = True
                return self._event(values, value)
            return None

        is_active = value == self.active_value
        if not is_active:
            self.active = False
            self.started = None
            self.candidate = None
            self.emitted = False
            return None

        if not self.active:
            self.active = True
            self.started = now
            self.candidate = value

        if not self.emitted and self.started is not None and now - self.started >= self.debounce:
            self.emitted = True
            return self._event(values, value)
        return None
