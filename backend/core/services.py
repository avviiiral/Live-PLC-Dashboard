import hashlib,secrets
from django.db import transaction
from django.utils import timezone
from .models import CollectorAgent,CollectorHeartbeat,ProductionEvent
def token_hash(value):return hashlib.sha256(value.encode()).hexdigest()
def register_collector(name):
 raw=secrets.token_urlsafe(40);obj=CollectorAgent.objects.create(name=name,token_hash=token_hash(raw));return obj,raw
def authenticate_collector(raw):
 if not raw:return None
 return CollectorAgent.objects.filter(token_hash=token_hash(raw),is_active=True).first()
@transaction.atomic
def ingest_event(data):
 return ProductionEvent.objects.get_or_create(id=data['id'],defaults={'station_id':data['station_id'],'plc_id':data['plc_id'],'collector':data['collector'],'occurred_at':data['occurred_at'],'result_status':data['result_status'],'payload':data.get('payload',{})})
def record_heartbeat(agent,status,details):
 CollectorHeartbeat.objects.create(collector=agent,status=status,details=details);agent.last_seen_at=timezone.now();agent.save(update_fields=['last_seen_at','updated_at'])
