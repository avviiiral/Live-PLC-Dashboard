from django.urls import include,path
from rest_framework.routers import DefaultRouter
from . import views
router=DefaultRouter()
router.register('companies',views.CompanyViewSet);router.register('plants',views.PlantViewSet);router.register('lines',views.LineViewSet);router.register('stations',views.StationViewSet);router.register('plcs',views.PLCViewSet);router.register('tags',views.TagViewSet);router.register('production-events',views.EventViewSet,basename='events');router.register('alarms',views.AlarmViewSet)
urlpatterns=[path('',include(router.urls)),path('health/',views.health),path('collectors/register/',views.collector_register),path('collectors/heartbeat/',views.collector_heartbeat),path('production/ingest/',views.production_ingest),path('dashboard/summary/',views.dashboard_summary)]
