import hashlib
import secrets

from django.db import transaction
from django.utils import timezone

from .models import CollectorAgent, CollectorHeartbeat, ProductionEvent


def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def register_collector(name):
    raw = secrets.token_urlsafe(40)
    obj = CollectorAgent.objects.create(name=name, token_hash=token_hash(raw))
    return obj, raw


def authenticate_collector(raw):
    if not raw:
        return None
    return CollectorAgent.objects.filter(
        token_hash=token_hash(raw), is_active=True
    ).first()


@transaction.atomic
def ingest_event(data):
    return ProductionEvent.objects.get_or_create(
        id=data["id"],
        defaults={
            "station_id": data["station_id"],
            "plc_id": data["plc_id"],
            "collector": data["collector"],
            "occurred_at": data["occurred_at"],
            "result_status": data["result_status"],
            "payload": data.get("payload", {}),
        },
    )


def record_heartbeat(agent, status, details):
    CollectorHeartbeat.objects.create(collector=agent, status=status, details=details)
    agent.last_seen_at = timezone.now()
    agent.save(update_fields=["last_seen_at", "updated_at"])


def serialize_collector_configuration(agent):
    """Build active assigned station/PLC/tag configuration from database rows."""
    stations = []
    assigned = (
        agent.assigned_stations.filter(is_active=True)
        .select_related("line", "line__plant")
        .prefetch_related("plcs__tags")
        .order_by("name")
    )
    for station in assigned:
        station_plcs = []
        all_tags = []
        for plc in station.plcs.filter(is_enabled=True).order_by("name"):
            tags = list(plc.tags.filter(is_enabled=True).order_by("name"))
            all_tags.extend(tags)
            station_plcs.append(
                {
                    "id": str(plc.id),
                    "name": plc.name,
                    "protocol": plc.protocol,
                    "host": plc.host,
                    "port": plc.port,
                    "rack": plc.rack,
                    "slot": plc.slot,
                    "unit_id": plc.unit_id,
                }
            )
        if not station_plcs:
            continue

        event_config = dict(station.event_config or {})
        if not event_config.get("trigger_tag"):
            result_tag = next((tag for tag in all_tags if tag.role == "result"), None)
            if result_tag:
                event_config = {
                    "trigger_tag": result_tag.name,
                    "result_tag": result_tag.name,
                    "active_values": [1, 2],
                    "rearm_value": 0,
                    "result_mapping": {
                        "0": "NOTHING",
                        "1": "PASS",
                        "2": "FAIL",
                        "3": "IN_PROGRESS",
                    },
                }
        if not event_config.get("trigger_tag"):
            continue

        stations.append(
            {
                "station_id": str(station.id),
                "station_name": station.name,
                "plant_name": station.line.plant.name,
                "line_name": station.line.name,
                "poll_interval_seconds": 1.0,
                "tags": [
                    {
                        "id": str(tag.id),
                        "name": tag.name,
                        "address": tag.address,
                        "data_type": tag.data_type,
                        "role": tag.role,
                        "scale": tag.scale,
                        "offset": tag.offset,
                    }
                    for tag in all_tags
                ],
                "event": event_config,
                "plcs": station_plcs,
            }
        )
    return {"stations": stations}
