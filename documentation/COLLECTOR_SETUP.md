# Collector Setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install `collector/requirements.txt`.
4. Copy or edit `collector/config/example.json`; replace the sample station and PLC UUID placeholders with real backend IDs.
5. Sign in as a Django staff user and provision a collector. Assign it to the target station and store its one-time token securely in the collector host's environment.
6. Configure `COLLECTOR_API_BASE_URL`, `COLLECTOR_TOKEN`, `COLLECTOR_CONFIG_PATH`, and optionally `COLLECTOR_QUEUE_PATH`.
7. Run `python -m collector.main` from the repository root.

A station config may contain a `plcs` array. Each PLC receives its own adapter, polling thread and event-detector state. The older singular `plc` config form remains supported.

For the Middle Testing example, two Siemens S7 PLCs are configured under one station. Their IP addresses and tag addresses are sourced from the operator-provided HMI logger. The tag list is assumed to be identical on both PLCs; verify this against the HMI project before enabling the second PLC.

Do not delete the local SQLite queue while it contains pending events. Protect local configuration and queue files with operating-system permissions.
