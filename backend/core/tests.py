import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Company,Plant,ProductionLine,Station,PLCDevice
from .services import register_collector
class PlatformTests(TestCase):
 def setUp(self):
  self.client=APIClient();user=get_user_model().objects.create_superuser('admin','admin@example.invalid','test-only-password');self.client.force_authenticate(user)
  company=Company.objects.create(name='Demo',code='demo');plant=Plant.objects.create(company=company,name='Plant',code='plant');line=ProductionLine.objects.create(plant=plant,name='Line',code='line');self.station=Station.objects.create(line=line,name='Station',code='station');self.plc=PLCDevice.objects.create(station=self.station,name='Mock PLC',protocol='mock',host='127.0.0.1')
 def test_station_list(self):self.assertEqual(self.client.get('/api/v1/stations/').status_code,200)
 def test_public_health(self):self.client.force_authenticate(None);self.assertEqual(self.client.get('/api/v1/health/').status_code,200)
 def test_event_is_idempotent(self):
  agent,token=register_collector('agent');agent.assigned_stations.add(self.station);self.client.force_authenticate(None);data={'id':str(uuid.uuid4()),'station':str(self.station.id),'plc':str(self.plc.id),'occurred_at':'2026-01-01T10:00:00Z','result_status':'PASS','payload':{'Output':1}}
  one=self.client.post('/api/v1/production/ingest/',data,format='json',HTTP_X_COLLECTOR_TOKEN=token);two=self.client.post('/api/v1/production/ingest/',data,format='json',HTTP_X_COLLECTOR_TOKEN=token)
  self.assertEqual(one.status_code,202);self.assertTrue(two.data['duplicate'])
