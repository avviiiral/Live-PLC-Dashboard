import unittest
from unittest.mock import patch

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


def make_adapter(host="192.168.0.1"):
    return MockPLCAdapter(
        plc_config=PLCConfig("mock", host, 102, 0, 1)
    )


class MockPLCAdapterTests(unittest.TestCase):
    def test_simulator_provides_every_middle_testing_tag_as_int(self):
        adapter = make_adapter()
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

    def test_result_sequence_matches_logger_rearm_and_capture_values(self):
        adapter = make_adapter()
        adapter.started_at = 100.0
        adapter.connect()
        result_tag = TagConfig("result", "Result_MW3112", "MW3112", "INT")

        expected = [(100.0, 0), (103.0, 3), (105.0, 1), (107.0, 0), (115.0, 2)]
        for clock_value, expected_result in expected:
            with patch("collector.adapters.mock_plc.time.monotonic", return_value=clock_value):
                self.assertEqual(adapter.read(result_tag), expected_result)
        adapter.disconnect()

    def test_two_plcs_have_independent_simulation_clocks_and_instances(self):
        first = make_adapter("192.168.0.1")
        second = make_adapter("192.168.0.5")
        first.connect()
        second.connect()
        self.assertIsNot(first, second)
        self.assertNotEqual(first.plc_config.host, second.plc_config.host)
        first.disconnect()
        second.disconnect()


if __name__ == "__main__":
    unittest.main()
