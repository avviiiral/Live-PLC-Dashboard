from rest_framework import serializers

from .models import (
    AlarmEvent,
    Company,
    PLCDevice,
    PLCTag,
    Plant,
    ProductionEvent,
    ProductionLine,
    Station,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = "__all__"


class ProductionLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLine
        fields = "__all__"


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"


class PLCDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLCDevice
        fields = "__all__"


class PLCTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PLCTag
        fields = "__all__"


class ProductionEventSerializer(serializers.ModelSerializer):
    # Preserve the collector-generated UUID across retry attempts.
    id = serializers.UUIDField(required=True)
    station_name = serializers.CharField(source="station.name", read_only=True)
    plc_name = serializers.CharField(source="plc.name", read_only=True)

    class Meta:
        model = ProductionEvent
        fields = [
            "id",
            "station",
            "station_name",
            "plc",
            "plc_name",
            "collector",
            "occurred_at",
            "result_status",
            "payload",
            "received_at",
        ]
        read_only_fields = ["received_at"]


class AlarmEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmEvent
        fields = "__all__"
