# PLC Configuration

A PLC belongs to a station. Device configuration includes protocol, host, port and protocol-specific settings. Tags include address, data type, role, units, polling cadence, scaling, offset and enabled state.

## Middle Testing reference configuration

The repository includes `collector/config/example.json` for the supplied station:

- Plant: **BGLIIN-Waluj**
- Production line: **20 - Amp**
- Station: **Middle Testing**
- PLC_1_EtherLink1: `192.168.0.1`
- PLC_2_EtherLink2: `192.168.0.5`
- Siemens S7 rack/slot: `0/1`
- Polling interval: 1 second
- Result marker: `MW3112`

Both PLCs are configured as independent connections under the same station. Each has its own event detector/re-arm state. The event rule waits until that PLC's MW3112 reads 0, then captures one event when it reads 1 (PASS) or 2 (FAIL). It will not capture again until that same PLC's MW3112 returns to 0.

The tag list is copied from the supplied EtherLink1 logger and applied to both PLCs. **This is an explicit assumption, not a verified fact.** Confirm that the same marker-memory offsets and data types are valid on EtherLink2 before enabling collection.

### Marker-memory addressing

The S7 adapter accepts Siemens marker-memory byte offsets such as `MW3008`, `MW412` and `MW3112`. MW is read as a two-byte big-endian marker word; configured `INT` values are decoded as signed 16-bit integers. These offsets are byte offsets, not word indexes.

The collector is read-only: it calls S7 read operations and does not write PLC memory. The PLCs must permit S7 communication from the collector host, and rack/slot, access protection and network routing must be confirmed at the plant.

Adapters also support DBX/DBB/DBW/DBD addresses. Modbus TCP uses explicit area notation, for example holding:40001, input:30001, coil:00001 or discrete:10001. Verify offset, register width and word order for each device.

## Setup requirements

Before running the sample:
1. Create company **BGLIIN-Waluj**, plant, line **20 - Amp**, and station **Middle Testing** in Django admin.
2. Create two Siemens S7 PLCDevice records under that station using the exact IPs above.
3. Create the eleven PLCTag records for each PLC, using the names and MW addresses in the sample JSON.
4. Register a collector and assign it to the Middle Testing station.
5. Replace the station and PLC UUID placeholders in the JSON and set the provisioned token in the local environment.

Do not commit real collector tokens or local factory credentials.

## Other adapters

- Mock: deterministic development adapter.
- Siemens S7: marker memory and common DB addressing.
- Modbus TCP: explicit register/coil area notation.

PLC writes are not implemented.
