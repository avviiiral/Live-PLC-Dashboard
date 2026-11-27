import threading
from collector.core.types import TagConfig
class MockPLCAdapter:
 def __init__(self,values=None):self.values=dict(values or {'Output':False,'Result':True,'Torque':10.5});self.connected=False;self.lock=threading.Lock()
 def connect(self):self.connected=True
 def disconnect(self):self.connected=False
 def is_connected(self):return self.connected
 def read(self,tag:TagConfig):
  if not self.connected:raise ConnectionError('Mock PLC disconnected')
  with self.lock:
   if tag.name not in self.values:raise KeyError(tag.name)
   value=self.values[tag.name]
  return value*tag.scale+tag.offset if isinstance(value,(int,float)) and not isinstance(value,bool) else value
 def set_value(self,name,value):
  with self.lock:self.values[name]=value
