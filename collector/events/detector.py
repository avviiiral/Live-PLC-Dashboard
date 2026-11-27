import time,uuid
from datetime import datetime,timezone
class ProductionEventDetector:
 def __init__(self,trigger_tag,active_value=True,debounce_ms=100,result_tag=None,result_mapping=None):
  self.tag=trigger_tag;self.active_value=active_value;self.debounce=max(0,debounce_ms)/1000;self.result_tag=result_tag;self.mapping=result_mapping or {'true':'PASS','false':'FAIL'};self.active=False;self.started=None;self.emitted=False
 def update(self,values):
  if self.tag not in values:return None
  active=values[self.tag]==self.active_value;now=time.monotonic()
  if active and not self.active:self.active=True;self.started=now;self.emitted=False;return None
  if not active:self.active=False;self.started=None;self.emitted=False;return None
  if not self.emitted and self.started is not None and now-self.started>=self.debounce:
   self.emitted=True;result=values.get(self.result_tag) if self.result_tag else None
   return {'id':str(uuid.uuid4()),'occurred_at':datetime.now(timezone.utc).isoformat(),'result_status':self.mapping.get(str(result).lower(),'UNKNOWN'),'payload':values}
  return None
