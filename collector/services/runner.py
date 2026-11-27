import logging
import time

from collector.events.detector import ProductionEventDetector

logger = logging.getLogger(__name__)


class StationRunner:
    def __init__(
        self, station_id, plc_id, adapter, tags, event_config, api, queue, interval=1.0
    ):
        self.station = station_id
        self.plc = plc_id
        self.adapter = adapter
        self.tags = tags
        self.api = api
        self.queue = queue
        self.interval = max(interval, 0.02)
        self.detector = ProductionEventDetector(
            trigger_tag=event_config["trigger_tag"],
            active_value=event_config.get("active_value", True),
            debounce_ms=event_config.get("debounce_ms", 100),
            result_tag=event_config.get("result_tag"),
            result_mapping=event_config.get("result_mapping", {}),
            active_values=event_config.get("active_values"),
            rearm_value=event_config.get("rearm_value"),
        )

    def flush(self):
        for event in self.queue.peek():
            try:
                self.api.send_event(event)
                self.queue.acknowledge(event["id"])
            except Exception:
                logger.exception("Pending event delivery failed")
                break

    def poll_once(self):
        if not self.adapter.is_connected():
            self.adapter.connect()

        values = {tag.name: self.adapter.read(tag) for tag in self.tags}
        event = self.detector.update(values)
        if event:
            event.update({"station": self.station, "plc": self.plc})
            self.queue.enqueue(event)
            self.flush()

    def run(self, stop):
        delay = 1
        while not stop.is_set():
            started = time.monotonic()
            try:
                self.poll_once()
                self.flush()
                delay = 1
            except Exception:
                logger.exception("PLC poll failed")
                self.adapter.disconnect()
                stop.wait(min(delay, 30))
                delay = min(delay * 2, 30)
            stop.wait(max(0, self.interval - (time.monotonic() - started)))
