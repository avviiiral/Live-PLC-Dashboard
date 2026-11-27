from django.contrib import admin
from .models import Company,Plant,ProductionLine,Station,PLCDevice,PLCTag,CollectorAgent,CollectorHeartbeat,TagReading,ProductionEvent,AlarmEvent,AuditLog
for model in (Company,Plant,ProductionLine,Station,PLCDevice,PLCTag,CollectorAgent,CollectorHeartbeat,TagReading,ProductionEvent,AlarmEvent,AuditLog):admin.site.register(model)
