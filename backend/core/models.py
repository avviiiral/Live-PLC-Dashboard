import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
class Timestamped(models.Model):
 created_at=models.DateTimeField(default=timezone.now,editable=False);updated_at=models.DateTimeField(auto_now=True)
 class Meta:abstract=True
class Company(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);name=models.CharField(max_length=160,unique=True);code=models.SlugField(max_length=80,unique=True);is_active=models.BooleanField(default=True)
 def __str__(self):return self.name
class Plant(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);company=models.ForeignKey(Company,on_delete=models.PROTECT,related_name='plants');name=models.CharField(max_length=160);code=models.SlugField(max_length=80);timezone=models.CharField(max_length=64,default='Asia/Kolkata');is_active=models.BooleanField(default=True)
 class Meta:constraints=[models.UniqueConstraint(fields=['company','code'],name='uq_plant_company_code')]
class ProductionLine(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);plant=models.ForeignKey(Plant,on_delete=models.PROTECT,related_name='lines');name=models.CharField(max_length=160);code=models.SlugField(max_length=80);is_active=models.BooleanField(default=True)
 class Meta:constraints=[models.UniqueConstraint(fields=['plant','code'],name='uq_line_plant_code')]
class Station(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);line=models.ForeignKey(ProductionLine,on_delete=models.PROTECT,related_name='stations');name=models.CharField(max_length=160);code=models.SlugField(max_length=80);event_config=models.JSONField(default=dict,blank=True);is_active=models.BooleanField(default=True)
 class Meta:constraints=[models.UniqueConstraint(fields=['line','code'],name='uq_station_line_code')];indexes=[models.Index(fields=['line','is_active'])]
class PLCDevice(Timestamped):
 PROTOCOLS=[('s7','Siemens S7'),('modbus_tcp','Modbus TCP'),('mock','Mock')]
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);station=models.ForeignKey(Station,on_delete=models.PROTECT,related_name='plcs');name=models.CharField(max_length=160);protocol=models.CharField(max_length=20,choices=PROTOCOLS);host=models.GenericIPAddressField(protocol='IPv4');port=models.PositiveIntegerField(default=102);rack=models.PositiveSmallIntegerField(default=0);slot=models.PositiveSmallIntegerField(default=1);unit_id=models.PositiveSmallIntegerField(default=1);is_enabled=models.BooleanField(default=True);last_seen_at=models.DateTimeField(null=True,blank=True)
class PLCTag(Timestamped):
 TYPES=[(x,x) for x in ('BOOL','INT','DINT','REAL','FLOAT','WORD','DWORD','STRING')];ROLES=[(x,x) for x in ('normal','trigger','result','counter')]
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);plc=models.ForeignKey(PLCDevice,on_delete=models.CASCADE,related_name='tags');name=models.CharField(max_length=120);address=models.CharField(max_length=160);data_type=models.CharField(max_length=12,choices=TYPES);role=models.CharField(max_length=16,choices=ROLES,default='normal');unit=models.CharField(max_length=32,blank=True);description=models.TextField(blank=True);polling_interval_ms=models.PositiveIntegerField(default=250);scale=models.FloatField(default=1);offset=models.FloatField(default=0);is_enabled=models.BooleanField(default=True);allow_write=models.BooleanField(default=False)
 class Meta:constraints=[models.UniqueConstraint(fields=['plc','name'],name='uq_tag_plc_name')];indexes=[models.Index(fields=['plc','is_enabled'])]
 def clean(self):
  super().clean()
  if self.polling_interval_ms<20:raise ValidationError({'polling_interval_ms':'Minimum polling interval is 20 ms'})
  if self.allow_write:raise ValidationError({'allow_write':'PLC writes are disabled'})
class CollectorAgent(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);name=models.CharField(max_length=120);token_hash=models.CharField(max_length=128);assigned_stations=models.ManyToManyField(Station,related_name='collectors',blank=True);is_active=models.BooleanField(default=True);last_seen_at=models.DateTimeField(null=True,blank=True)
class CollectorHeartbeat(Timestamped):
 collector=models.ForeignKey(CollectorAgent,on_delete=models.CASCADE,related_name='heartbeats');status=models.CharField(max_length=24,default='online');details=models.JSONField(default=dict,blank=True)
 class Meta:indexes=[models.Index(fields=['collector','-created_at'])]
class TagReading(models.Model):
 id=models.BigAutoField(primary_key=True);station=models.ForeignKey(Station,on_delete=models.PROTECT,related_name='readings');plc=models.ForeignKey(PLCDevice,on_delete=models.PROTECT,related_name='readings');tag=models.ForeignKey(PLCTag,on_delete=models.PROTECT,related_name='readings');value=models.JSONField();recorded_at=models.DateTimeField();received_at=models.DateTimeField(default=timezone.now)
 class Meta:indexes=[models.Index(fields=['station','-recorded_at']),models.Index(fields=['tag','-recorded_at'])]
class ProductionEvent(models.Model):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);station=models.ForeignKey(Station,on_delete=models.PROTECT,related_name='production_events');plc=models.ForeignKey(PLCDevice,on_delete=models.PROTECT,related_name='production_events');collector=models.ForeignKey(CollectorAgent,on_delete=models.PROTECT,related_name='production_events');occurred_at=models.DateTimeField();result_status=models.CharField(max_length=16);payload=models.JSONField(default=dict);received_at=models.DateTimeField(default=timezone.now)
 class Meta:indexes=[models.Index(fields=['station','-occurred_at']),models.Index(fields=['result_status','-occurred_at'])]
class AlarmEvent(Timestamped):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False);station=models.ForeignKey(Station,on_delete=models.PROTECT,related_name='alarms');severity=models.CharField(max_length=16,default='warning');message=models.CharField(max_length=255);details=models.JSONField(default=dict,blank=True);occurred_at=models.DateTimeField(default=timezone.now);acknowledged_at=models.DateTimeField(null=True,blank=True);acknowledged_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
class AuditLog(models.Model):
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL);action=models.CharField(max_length=80);entity_type=models.CharField(max_length=80);entity_id=models.CharField(max_length=80,blank=True);details=models.JSONField(default=dict,blank=True);created_at=models.DateTimeField(default=timezone.now,db_index=True)
