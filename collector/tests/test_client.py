import unittest

from collector.communication.api_client import BackendClient


class BackendClientModeTests(unittest.TestCase):
    def test_local_mode_requires_loopback_and_sends_no_token(self):
        client = BackendClient("http://127.0.0.1:8000", mode="local")
        self.assertEqual(client.session.headers["X-Collector-Mode"], "local")
        self.assertNotIn("X-Collector-Token", client.session.headers)

    def test_local_mode_rejects_remote_backend_url(self):
        with self.assertRaises(ValueError):
            BackendClient("http://192.168.1.10:8000", mode="local")

    def test_lan_mode_requires_one_persistent_machine_token(self):
        with self.assertRaises(ValueError):
            BackendClient("http://192.168.1.10:8000", mode="lan")
        client = BackendClient(
            "http://192.168.1.10:8000", mode="lan", token="test-machine-token"
        )
        self.assertEqual(client.session.headers["X-Collector-Token"], "test-machine-token")
        self.assertNotIn("X-Collector-Mode", client.session.headers)


if __name__ == "__main__":
    unittest.main()
