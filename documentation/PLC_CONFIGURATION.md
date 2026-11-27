# PLC Configuration

PLC configuration belongs in Django records. Company, plant, line, station, PLCDevice, PLCTag and station event_config are the configuration source of truth; the collector syncs these from the API. JSON files are not required to add equipment.

## Middle Testing reference
- Plant: BGLIIN-Waluj
- Line: 20 - Amp
- Station: Middle Testing
- PLC_1_EtherLink1: 192.168.0.1
- PLC_2_EtherLink2: 192.168.0.5
- Siemens S7 rack/slot: 0/1
- Poll interval: 1 second
- Result register: MW3112

Configure station event_config:
```json
{
  "trigger_tag": "Result_MW3112",
  "result_tag": "Result_MW3112",
  "active_values": [1, 2],
  "rearm_value": 0,
  "result_mapping": {"0": "NOTHING", "1": "PASS", "2": "FAIL", "3": "IN_PROGRESS"}
}
```

Create 11 INT tags on each PLC: Coil_Short_MW3008 (MW3008), Continuity_ON_MW412 (MW412), Aging_Test_MW410 (MW410), Coil_to_Cont_COM_MW4004 (MW4004), Coil_to_Cont_NO_MW4002 (MW4002), Diode_Test_MW5026 (MW5026), Start_Time_MW438 (MW438), Pull_In_MW422 (MW422), Drop_Out_V_MW424 (MW424), Coil_Resistance_MW426 (MW426), Result_MW3112 (MW3112). Set the Result tag role to `result`.

The same tag map on EtherLink2 is an assumption from the supplied EtherLink1 logger, not hardware-verified. Confirm offsets and data types before enabling the second PLC.

Siemens MW addresses are byte offsets, read as two-byte big-endian signed INT values. The collector is read-only. Verify S7 permissions, rack/slot, access protection and routing at the plant.
