# PLC Configuration
A PLC belongs to a station. Device configuration includes protocol, host, port and protocol-specific settings. Tags include address, data type, role, units, polling cadence, scaling, offset and enabled state.

Adapters:
- Mock: deterministic development adapter.
- Siemens S7: common DBX, DBW and DBD addressing; validate address and data representation against hardware.
- Modbus TCP: use explicit area notation, for example holding:40001, input:30001, coil:00001 or discrete:10001. Verify offset, register width and word order for each device.

Production event rules configure trigger tag, active value (active-high or active-low), debounce, result tag and result mapping. PLC writes are not implemented.
