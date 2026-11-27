import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import CollectorAgent, Company, PLCDevice, PLCTag, Plant, ProductionLine, Station
from .services import register_collector


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
            line=line,
            name="Station",
            code="station",
            event_config={
                "trigger_tag": "Result",
                "result_tag": "Result",
                "active_values": [1, 2],
                "rearm_value": 0,
                "result_mapping": {"0": "NOTHING", "1": "PASS", "2": "FAIL"},
            },
        )
        self.plc = PLCDevice.objects.create(
            station=self.station,
            name="Mock PLC",
            protocol="mock",
            host="127.0.0.1",
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

    def test_remote_configuration_is_scoped_to_assignments(self):
        agent, token = self.add_remote_collector()
        self.client.force_authenticate(None)
        response = self.client.get(
            "/api/v1/collectors/configuration/",
            HTTP_X_COLLECTOR_TOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["stations"][0]["station_id"], str(self.station.id)
        )
        self.assertEqual(
            response.data["stations"][0]["plcs"][0]["id"], str(self.plc.id)
        )

    def test_local_configuration_requires_loopback_and_local_agent(self):
        self.client.force_authenticate(None)
        CollectorAgent.objects.create(
            name="Local Development Collector", token_hash="local-mode-placeholder"
        )
        response = self.client.get(
            "/api/v1/collectors/configuration/",
            HTTP_X_COLLECTOR_MODE="local",
            REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(response.status_code, 200)
        denied = self.client.get(
            "/api/v1/collectors/configuration/",
            HTTP_X_COLLECTOR_MODE="local",
            REMOTE_ADDR="192.168.1.20",
        )
        self.assertEqual(denied.status_code, 401)

    def test_remote_ingestion_preserves_uuid_and_is_idempotent(self):
        agent, token = self.add_remote_collector()
        self.client.force_authenticate(None)
        event_id = str(uuid.uuid4())
        data = {
            "id": event_id,
            "station": str(self.station.id),
            "plc": str(self.plc.id),
            "occurred_at": "2026-01-01T10:00:00Z",
            "result_status": "PASS",
            "payload": {"Result": 1},
        }
        first = self.client.post(
            "/api/v1/production/ingest/",
            data,
            format="json",
            HTTP_X_COLLECTOR_TOKEN=token,
        )
        second = self.client.post(
            "/api/v1/production/ingest/",
            data,
            format="json",
            HTTP_X_COLLECTOR_TOKEN=token,
        )
        self.assertEqual(first.status_code, 202)
        self.assertEqual(first.data["event_id"], event_id)
        self.assertTrue(second.data["duplicate"])
