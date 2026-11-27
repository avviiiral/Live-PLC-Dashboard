from urllib.parse import urlparse

import requests


class BackendClient:
    def __init__(self, url, mode="local", token=None, timeout=5):
        if not url:
            raise ValueError("COLLECTOR_API_BASE_URL is required")
        if mode not in {"local", "lan"}:
            raise ValueError("COLLECTOR_MODE must be 'local' or 'lan'")

        self.url = url.rstrip("/")
        self.mode = mode
        self.session = requests.Session()
        self.timeout = timeout

        if mode == "local":
            hostname = urlparse(self.url).hostname
            if hostname not in {"127.0.0.1", "::1", "localhost"}:
                raise ValueError(
                    "Local mode requires a loopback backend URL; "
                    "use COLLECTOR_MODE=lan for remote hosts."
                )
            self.session.headers["X-Collector-Mode"] = "local"
        else:
            if not token:
                raise ValueError(
                    "LAN mode requires one persistent machine credential in root .env."
                )
            self.session.headers["X-Collector-Token"] = token

    def configuration(self):
        response = self.session.get(
            f"{self.url}/api/v1/collectors/configuration/",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def heartbeat(self, details=None):
        response = self.session.post(
            f"{self.url}/api/v1/collectors/heartbeat/",
            json={"status": "online", "details": details or {}},
            timeout=self.timeout,
        )
        response.raise_for_status()

    def send_event(self, event):
        response = self.session.post(
            f"{self.url}/api/v1/production/ingest/",
            json=event,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return bool(response.json().get("accepted"))
