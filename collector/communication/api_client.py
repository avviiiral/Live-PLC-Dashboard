import requests
class BackendClient:
 def __init__(self,url,token,timeout=5):
  if not url or not token or token=='SET_AFTER_REGISTRATION':raise ValueError('Backend URL and provisioned collector token required')
  self.url=url.rstrip('/');self.session=requests.Session();self.session.headers.update({'X-Collector-Token':token});self.timeout=timeout
 def heartbeat(self,details=None):
  r=self.session.post(self.url+'/api/v1/collectors/heartbeat/',json={'status':'online','details':details or {}},timeout=self.timeout);r.raise_for_status()
 def send_event(self,event):
  r=self.session.post(self.url+'/api/v1/production/ingest/',json=event,timeout=self.timeout);r.raise_for_status();return bool(r.json().get('accepted'))
