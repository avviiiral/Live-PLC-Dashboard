from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count, Q
from django.utils.dateparse import parse_datetime
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import AlarmEvent, Company, PLCDevice, PLCTag, Plant, ProductionEvent, ProductionLine, Station
from .serializers import AlarmEventSerializer, CompanySerializer, PLCDeviceSerializer, PLCTagSerializer, PlantSerializer, ProductionEventSerializer, ProductionLineSerializer, StationSerializer
from .services import authenticate_collector, ingest_event, record_heartbeat, register_collector, serialize_collector_configuration


class ManagedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ["-created_at"]

    def get_permissions(self):
        return [IsAdminUser() if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsAuthenticated()]


class CompanyViewSet(ManagedViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ["name", "code"]


class PlantViewSet(ManagedViewSet):
    queryset = Plant.objects.select_related("company")
    serializer_class = PlantSerializer
    search_fields = ["name", "code"]


class LineViewSet(ManagedViewSet):
    queryset = ProductionLine.objects.select_related("plant")
    serializer_class = ProductionLineSerializer
    search_fields = ["name", "code"]


class StationViewSet(ManagedViewSet):
    queryset = Station.objects.select_related("line")
    serializer_class = StationSerializer
    search_fields = ["name", "code"]


class PLCViewSet(ManagedViewSet):
    queryset = PLCDevice.objects.select_related("station")
    serializer_class = PLCDeviceSerializer
    search_fields = ["name", "host"]


class TagViewSet(ManagedViewSet):
    queryset = PLCTag.objects.select_related("plc", "plc__station")
    serializer_class = PLCTagSerializer
    search_fields = ["name", "address"]


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductionEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["occurred_at", "result_status"]
    ordering = ["-occurred_at"]

    def get_queryset(self):
        q = ProductionEvent.objects.select_related("station", "plc", "collector")
        params = self.request.query_params
        if params.get("station"):
            q = q.filter(station_id=params["station"])
        if params.get("result"):
            q = q.filter(result_status=params["result"].upper())
        if params.get("start"):
            q = q.filter(occurred_at__gte=parse_datetime(params["start"]))
        if params.get("end"):
            q = q.filter(occurred_at__lte=parse_datetime(params["end"]))
        return q


class AlarmViewSet(ManagedViewSet):
    queryset = AlarmEvent.objects.select_related("station", "acknowledged_by")
    serializer_class = AlarmEventSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "live-plc-backend"})


def collector_authorized(request):
    if request.headers.get("X-Collector-Mode", "").lower() == "local":
        # Only trust a direct loopback peer. Never trust X-Forwarded-For.
        if request.META.get("REMOTE_ADDR") not in {"127.0.0.1", "::1"}:
            return None
        from .models import CollectorAgent
        return CollectorAgent.objects.filter(
            is_active=True, name="Local Development Collector"
        ).first()
    return authenticate_collector(request.headers.get("X-Collector-Token", ""))


@api_view(["POST"])
@permission_classes([IsAdminUser])
def collector_register(request):
    name = str(request.data.get("name", "")).strip()
    if not name:
        return Response({"detail": "name is required"}, status=400)
    agent, raw = register_collector(name)
    return Response({"collector_id": str(agent.id), "token": raw}, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def collector_configuration(request):
    agent = collector_authorized(request)
    if agent is None:
        return Response({"detail": "Collector authentication failed"}, status=401)
    return Response(serialize_collector_configuration(agent))


@api_view(["POST"])
@permission_classes([AllowAny])
def collector_heartbeat(request):
    agent = collector_authorized(request)
    if agent is None:
        return Response({"detail": "Collector authentication failed"}, status=401)
    record_heartbeat(agent, str(request.data.get("status", "online")), request.data.get("details", {}))
    return Response({"accepted": True})


@api_view(["POST"])
@permission_classes([AllowAny])
def production_ingest(request):
    agent = collector_authorized(request)
    if agent is None:
        return Response({"detail": "Collector authentication failed"}, status=401)
    serializer = ProductionEventSerializer(data={**request.data, "collector": str(agent.id)})
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    station = serializer.validated_data["station"]
    plc = serializer.validated_data["plc"]
    if plc.station_id != station.id:
        return Response({"detail": "PLC does not belong to station"}, status=400)
    if not agent.assigned_stations.filter(id=station.id).exists():
        return Response({"detail": "Collector is not assigned to station"}, status=403)
    event, created = ingest_event({
        "id": serializer.validated_data["id"],
        "station_id": station.id,
        "plc_id": plc.id,
        "collector": agent,
        "occurred_at": serializer.validated_data["occurred_at"],
        "result_status": serializer.validated_data["result_status"],
        "payload": serializer.validated_data.get("payload", {}),
    })
    if created:
        async_to_sync(get_channel_layer().group_send)(
            f"station_{event.station_id}",
            {"type": "production.event", "event": ProductionEventSerializer(event).data},
        )
    return Response(
        {"accepted": True, "duplicate": not created, "event_id": str(event.id)},
        status=202,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    q = ProductionEvent.objects.all()
    station_id = request.query_params.get("station")
    if station_id:
        q = q.filter(station_id=station_id)
    counts = q.aggregate(
        total=Count("id"),
        passed=Count("id", filter=Q(result_status="PASS")),
        failed=Count("id", filter=Q(result_status="FAIL")),
    )
    total = counts["total"] or 0
    counts["rejection_percentage"] = round(counts["failed"] / total * 100, 2) if total else 0
    counts["stations"] = Station.objects.filter(is_active=True).count()
    counts["plcs"] = PLCDevice.objects.filter(is_enabled=True).count()
    return Response(counts)
