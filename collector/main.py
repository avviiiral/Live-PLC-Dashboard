import hashlib
import json
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
                protocol, plc["host"], int(plc.get("port", 102)),
                int(plc.get("rack", 0)), int(plc.get("slot", 1)),
                int(plc.get("unit_id", 1)),
            )
            tags = [TagConfig(**tag) for tag in station["tags"]]
            runner = StationRunner(
                station["station_id"], plc["id"], adapters[protocol](plc_config),
                tags, station["event"], api, queue,
                float(station.get("poll_interval_seconds", 1.0)),
            )
            runners[(station["station_id"], plc["id"])] = runner
    return runners


def runner_fingerprint(runner):
    """Include connection, tag and event settings so edits trigger safe restart."""
    adapter_cfg = getattr(runner.adapter, "plc_config", None)
    data = {
        "station": runner.station,
        "plc": runner.plc,
        "tags": [
            {
                "name": tag.name, "address": tag.address,
                "data_type": tag.data_type,
                "scale": getattr(tag, "scale", 1),
                "offset": getattr(tag, "offset", 0),
            }
            for tag in runner.tags
        ],
        "interval": runner.interval,
        "event": runner.detector.__dict__,
        "adapter": getattr(adapter_cfg, "__dict__", str(adapter_cfg)),
    }
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()


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
    runners, threads, fingerprints = {}, {}, {}

    def stop_runner(key):
        runner = runners.pop(key)
        thread = threads.pop(key)
        fingerprints.pop(key, None)
        runner.stop_event.set()
        thread.join(timeout=5)
        runner.adapter.disconnect()

    def start_runner(key, runner):
        runner.stop_event = threading.Event()
        thread = threading.Thread(
            target=runner.run, args=(runner.stop_event,),
            daemon=True, name=f"collector-{key[1]}",
        )
        runners[key], threads[key] = runner, thread
        fingerprints[key] = runner_fingerprint(runner)
        thread.start()

    def sync_configuration():
        desired = build_runners(api.configuration(), api, queue)
        desired_fingerprints = {
            key: runner_fingerprint(runner) for key, runner in desired.items()
        }
        for key in list(runners):
            if key not in desired or fingerprints.get(key) != desired_fingerprints.get(key):
                stop_runner(key)
        for key, runner in desired.items():
            if key not in runners:
                start_runner(key, runner)
            else:
                # Dispose the unused adapter constructed for the comparison.
                runner.adapter.disconnect()
        return len(runners)

    logging.info("Starting collector in %s mode", mode)
    backoff = 1
    while not stop.is_set():
        try:
            plc_count = sync_configuration()
            api.heartbeat({"plcs": plc_count, "queue_size": queue.size(), "mode": mode})
            backoff = 1
            stop.wait(sync_interval)
        except Exception:
            logging.exception("Collector configuration sync/heartbeat failed")
            stop.wait(backoff)
            backoff = min(backoff * 2, 30)

    for key in list(runners):
        stop_runner(key)


if __name__ == "__main__":
    main()
