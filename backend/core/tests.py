import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import CollectorAgent, Company, PLCDevice, PLCTag, Plant, ProductionLine, Station
from .services import get_or_create_local_collector, register_collector, serialize_collector_configuration


class PlatformTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser(
            "admin", "admin@example.invalid", "test-only-password"
        )
        self.client.force_authenticate(admin)
        company = Company.objects.create(name="Demo", code="demo")
        plant = Plant.objects.create(company=company, name="Plant", code="plant")
        line = ProductionLine.objects.create(plant=plant, name="Line", code="line")
        self.station = Station.objects.create(
            line=line, name="Station", code="station",
            event_config={
                "trigger_tag": "Result", "result_tag": "Result",
                "active_values": [1, 2], "rearm_value": 0,
                "result_mapping": {"0": "NOTHING", "1": "PASS", "2": "FAIL"},
            },
        )
        self.plc = PLCDevice.objects.create(
            station=self.station, name="Mock PLC", protocol="mock", host="127.0.0.1"
        )
        PLCTag.objects.create(
            plc=self.plc, name="Result", address="MW10", data_type="INT", role="result"
        )

    def add_remote_collector(self):
        agent, token = register_collector("Remote collector")
        agent.assigned_stations.add(self.station)
        return agent, token

    def test_station_list(self):
        self.assertEqual(self.client.get("/api/v1/stations/").status_code, 200)

    def test_health(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/health/").status_code, 200)

    def test_local_identity_is_persistent_and_has_no_generated_secret(self):
        first = get_or_create_local_collector()
        second = get_or_create_local_collector()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.token_hash, "local-mode-no-token")

    def test_remote_configuration_scopes_each_plc_and_its_own_tags(self):
        second = PLCDevice.objects.create(
            station=self.station, name="Second PLC", protocol="mock", host="127.0.0.2"
        )
        PLCTag.objects.create(
            plc=second, name="SecondResult", address="MW22", data_type="INT", role="result"
        )
        agent, token = self.add_remote_collector()
        self.client.force_authenticate(None)
        response = self.client.get(
            "/api/v1/collectors/configuration/", HTTP_X_COLLECTOR_TOKEN=token
        )
        self.assertEqual(response.status_code, 200)
        configs = response.data["stations"]
        self.assertEqual(len(configs), 2)
        by_plc = {item["plcs"][0]["id"]: item for item in configs}
        self.assertEqual(
            [tag["name"] for tag in by_plc[str(self.plc.id)]["tags"]], ["Result"]
        )
        self.assertEqual(
            [tag["name"] for tag in by_plc[str(second.id)]["tags"]], ["SecondResult"]
        )

    def test_local_configuration_requires_loopback(self):
        self.client.force_authenticate(None)
        local = get_or_create_local_collector()
        local.assigned_stations.add(self.station)
        response = self.client.get(
            "/api/v1/collectors/configuration/",
            HTTP_X_COLLECTOR_MODE="local", REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["stations"]), 1)
        denied = self.client.get(
            "/api/v1/collectors/configuration/",
            HTTP_X_COLLECTOR_MODE="local", REMOTE_ADDR="192.168.1.20",
        )
        self.assertEqual(denied.status_code, 401)

    def test_unassigned_local_agent_cannot_ingest_station_event(self):
        self.client.force_authenticate(None)
        get_or_create_local_collector()
        data = {
            "id": str(uuid.uuid4()),
            "station": str(self.station.id),
            "plc": str(self.plc.id),
            "occurred_at": "2026-01-01T10:00:00Z",
            "result_status": "PASS",
            "payload": {"Result": 1},
        }
        response = self.client.post(
            "/api/v1/production/ingest/", data, format="json",
            HTTP_X_COLLECTOR_MODE="local", REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(response.status_code, 403)

    def test_remote_ingestion_preserves_uuid_and_is_idempotent(self):
        agent, token = self.add_remote_collector()
        self.client.force_authenticate(None)
        event_id = str(uuid.uuid4())
        data = {
            "id": event_id, "station": str(self.station.id), "plc": str(self.plc.id),
            "occurred_at": "2026-01-01T10:00:00Z", "result_status": "PASS",
            "payload": {"Result": 1},
        }
        first = self.client.post(
            "/api/v1/production/ingest/", data, format="json",
            HTTP_X_COLLECTOR_TOKEN=token,
        )
        second = self.client.post(
            "/api/v1/production/ingest/", data, format="json",
            HTTP_X_COLLECTOR_TOKEN=token,
        )
        self.assertEqual(first.status_code, 202)
        self.assertEqual(first.data["event_id"], event_id)
        self.assertTrue(second.data["duplicate"])
