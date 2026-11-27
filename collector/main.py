import json
import logging
import os
import signal
import threading
from pathlib import Path

from dotenv import load_dotenv

from collector.adapters.mock_plc import MockPLCAdapter
from collector.adapters.siemens_s7 import SiemensS7Adapter
from collector.adapters.modbus_tcp import ModbusTCPAdapter
from collector.communication.api_client import BackendClient
from collector.core.types import PLCConfig, TagConfig
from collector.storage.queue import PersistentEventQueue
from collector.services.runner import StationRunner


def main():
    load_dotenv()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    config_path = Path(os.getenv("COLLECTOR_CONFIG_PATH", "collector/config/example.json"))
    if not config_path.exists():
        raise RuntimeError(f"Collector config missing: {config_path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    api = BackendClient(
        os.getenv("COLLECTOR_API_BASE_URL") or config.get("backend_url"),
        os.getenv("COLLECTOR_TOKEN") or config.get("collector_token"),
    )
    queue = PersistentEventQueue(
        os.getenv("COLLECTOR_QUEUE_PATH", config.get("queue_path", "collector/data/queue.sqlite3"))
    )

    if not config.get("stations"):
        raise RuntimeError("No stations configured; refusing to start")

    stop = threading.Event()

    def shutdown(signum, frame):
        stop.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    adapters = {
        "mock": lambda plc_config: MockPLCAdapter(),
        "s7": lambda plc_config: SiemensS7Adapter(plc_config),
        "modbus_tcp": lambda plc_config: ModbusTCPAdapter(plc_config),
    }

    runners = []
    for station in config["stations"]:
        # A station may contain multiple independent PLCs. The legacy singular
        # "plc" form remains supported for existing collector configurations.
        plc_entries = station.get("plcs") or [station["plc"]]
        for plc in plc_entries:
            plc_config = PLCConfig(
                plc["protocol"],
                plc["host"],
                int(plc.get("port", 102)),
                int(plc.get("rack", 0)),
                int(plc.get("slot", 1)),
                int(plc.get("unit_id", 1)),
            )
            if plc_config.protocol not in adapters:
                raise ValueError(f"Unsupported protocol {plc_config.protocol}")

            tags = [TagConfig(**tag) for tag in station["tags"]]
            runner = StationRunner(
                station["station_id"],
                plc["id"],
                adapters[plc_config.protocol](plc_config),
                tags,
                station["event"],
                api,
                queue,
                config.get("poll_interval_seconds", 1.0),
            )
            runners.append(runner)
            logging.info(
                "Configured station %s with PLC %s at %s",
                station.get("station_name", station["station_id"]),
                plc.get("name", plc["id"]),
                plc["host"],
            )

    threads = [
        threading.Thread(target=runner.run, args=(stop,), daemon=True)
        for runner in runners
    ]
    for thread in threads:
        thread.start()

    try:
        while not stop.wait(30):
            try:
                api.heartbeat({"queue_size": queue.size(), "plcs": len(runners)})
            except Exception:
                logging.exception("Collector heartbeat failed")
    finally:
        stop.set()
        for thread in threads:
            thread.join(timeout=5)
        for runner in runners:
            runner.adapter.disconnect()


if __name__ == "__main__":
    main()
