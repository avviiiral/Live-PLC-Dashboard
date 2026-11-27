# Collector Setup
1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install `collector/requirements.txt`.
4. Copy `collector/config/example.json` and replace the sample UUIDs with real backend IDs.
5. Sign in as a Django staff user and provision a collector. Store its one-time token securely in the collector host's environment.
6. Configure `COLLECTOR_API_BASE_URL`, `COLLECTOR_TOKEN`, `COLLECTOR_CONFIG_PATH`, and optionally `COLLECTOR_QUEUE_PATH`.
7. Run `python -m collector.main` from the repository root.

Do not delete the local SQLite queue while it contains pending events. Protect local configuration and queue files with operating-system permissions.
