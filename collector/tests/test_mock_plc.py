import unittest

from collector.adapters.mock_plc import MockPLCAdapter
from collector.core.types import PLCConfig, TagConfig


TAG_NAMES = [
    "Coil_Short_MW3008",
    "Continuity_ON_MW412",
    "Aging_Test_MW410",
    "Coil_to_Cont_COM_MW4004",
    "Coil_to_Cont_NO_MW4002",
    "Diode_Test_MW5026",
    "Start_Time_MW438",
    "Pull_In_MW422",
    "Drop_Out_V_MW424",
    "Coil_Resistance_MW426",
    "Result_MW3112",
]


class MockPLCAdapterTests(unittest.TestCase):
    def test_simulator_provides_every_middle_testing_tag_as_int(self):
        adapter = MockPLCAdapter(
            plc_config=PLCConfig("mock", "192.168.0.1", 102, 0, 1)
        )
        adapter.connect()
        try:
            values = {
                name: adapter.read(TagConfig(name, name, f"MW{index}", "INT"))
                for index, name in enumerate(TAG_NAMES)
            }
            self.assertEqual(set(values), set(TAG_NAMES))
            self.assertTrue(all(isinstance(value, int) for value in values.values()))
            self.assertEqual(values["Result_MW3112"], 0)
        finally:
            adapter.disconnect()

    def test_each_plc_adapter_has_independent_simulation_clock(self):
        first = MockPLCAdapter(
            plc_config=PLCConfig("mock", "192.168.0.1", 102, 0, 1)
        )
        second = MockPLCAdapter(
            plc_config=PLCConfig("mock", "192.168.0.5", 102, 0, 1)
        )
        first.connect()
        second.connect()
        self.assertIsNot(first.started_at, second.started_at)
        first.disconnect()
        second.disconnect()


if __name__ == "__main__":
    unittest.main()
