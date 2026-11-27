from django.urls import re_path
from .consumers import StationConsumer
websocket_urlpatterns=[re_path(r'ws/stations/(?P<station_id>[0-9a-f-]+)/$',StationConsumer.as_asgi())]
