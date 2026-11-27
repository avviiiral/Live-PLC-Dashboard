import logging
import os
import signal
import threading

from dotenv import load_dotenv

from collector.adapters.mock_plc import MockPLCAdapter
from collector.adapters.siemens_s7 import SiemensS7Adapter
from collector.adapters.modbus_tcp import ModbusTCPAdapter
from collector.communication.api_client import BackendClient
from collector.core.types import PLCConfig, TagConfig
from collector.services.runner import StationRunner
from collector.storage.queue import PersistentEventQueue


def build_runners(config, api, queue):
    """Create one isolated connection/detector per configured PLC."""
    adapters = {
        "mock": lambda cfg: MockPLCAdapter(plc_config=cfg),
        "s7": lambda cfg: SiemensS7Adapter(cfg),
        "modbus_tcp": lambda cfg: ModbusTCPAdapter(cfg),
    }
    runners = {}
    for station in config.get("stations", []):
        for plc in station.get("plcs", []):
            protocol = plc["protocol"]
            if protocol not in adapters:
                raise ValueError(f"Unsupported protocol: {protocol}")
            plc_config = PLCConfig(
                protocol,
                plc["host"],
                int(plc.get("port", 102)),
                int(plc.get("rack", 0)),
                int(plc.get("slot", 1)),
                int(plc.get("unit_id", 1)),
            )
            tags = [TagConfig(**tag) for tag in station["tags"]]
            runner = StationRunner(
                station["station_id"],
                plc["id"],
                adapters[protocol](plc_config),
                tags,
                station["event"],
                api,
                queue,
                float(station.get("poll_interval_seconds", 1.0)),
            )
            runners[(station["station_id"], plc["id"])] = runner
    return runners


def main():
    load_dotenv()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())

    mode = os.getenv("COLLECTOR_MODE", "local").strip().lower()
    api = BackendClient(
        os.getenv("COLLECTOR_API_BASE_URL", "http://127.0.0.1:8000"),
        mode=mode,
        token=os.getenv("COLLECTOR_TOKEN"),
    )
    queue = PersistentEventQueue(
        os.getenv("COLLECTOR_QUEUE_PATH", "collector/data/queue.sqlite3")
    )
    sync_interval = max(float(os.getenv("COLLECTOR_SYNC_INTERVAL", "15")), 2.0)

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    runners, threads = {}, {}

    def sync_configuration():
        desired = build_runners(api.configuration(), api, queue)

        # Remove disabled/deleted assignments and stop their PLC workers.
        for key in set(runners) - set(desired):
            runner = runners.pop(key)
            thread = threads.pop(key)
            runner.stop_event.set()
            thread.join(timeout=5)
            runner.adapter.disconnect()

        # Start only new PLCs. Existing runners keep their re-arm state.
        for key in set(desired) - set(runners):
            runner = desired[key]
            runner.stop_event = threading.Event()
            thread = threading.Thread(
                target=runner.run,
                args=(runner.stop_event,),
                daemon=True,
                name=f"collector-{key[1]}",
            )
            runners[key] = runner
            threads[key] = thread
            thread.start()
        return len(runners)

    logging.info("Starting collector in %s mode", mode)
    backoff = 1
    while not stop.is_set():
        try:
            plc_count = sync_configuration()
            api.heartbeat(
                {"plcs": plc_count, "queue_size": queue.size(), "mode": mode}
            )
            backoff = 1
            stop.wait(sync_interval)
        except Exception:
            logging.exception("Collector configuration sync/heartbeat failed")
            stop.wait(backoff)
            backoff = min(backoff * 2, 30)

    for key, runner in list(runners.items()):
        runner.stop_event.set()
        threads[key].join(timeout=5)
        runner.adapter.disconnect()


if __name__ == "__main__":
    main()
