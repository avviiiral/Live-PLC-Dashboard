import re
from collector.core.types import PLCConfig,TagConfig
class SiemensS7Adapter:
 def __init__(self,cfg:PLCConfig):self.cfg=cfg;self.client=None
 def connect(self):
  try:import snap7
  except ImportError as exc:raise RuntimeError('Install python-snap7') from exc
  self.client=snap7.Client();self.client.connect(self.cfg.host,self.cfg.rack,self.cfg.slot,self.cfg.port)
  if not self.client.get_connected():raise ConnectionError('S7 connection failed')
 def disconnect(self):
  if self.client:self.client.disconnect();self.client=None
 def is_connected(self):return bool(self.client and self.client.get_connected())
 def read(self,tag:TagConfig):
  if not self.is_connected():raise ConnectionError('S7 is disconnected')
  import snap7.util
  m=re.fullmatch(r'DB(\d+)\.DB([XBWD])(\d+)(?:\.(\d+))?',tag.address.upper())
  if not m:raise ValueError(f'Unsupported address {tag.address}')
  db,area,offset,bit=m.groups();raw=self.client.db_read(int(db),int(offset),{'X':1,'B':1,'W':2,'D':4}[area])
  if area=='X':
   if bit is None or int(bit)>7:raise ValueError('DBX address requires bit 0..7')
   value=snap7.util.get_bool(raw,0,int(bit))
  elif tag.data_type in ('REAL','FLOAT'):value=snap7.util.get_real(raw,0)
  elif tag.data_type=='INT':value=snap7.util.get_int(raw,0)
  elif tag.data_type=='DINT':value=snap7.util.get_dint(raw,0)
  elif tag.data_type=='WORD':value=snap7.util.get_word(raw,0)
  elif tag.data_type=='DWORD':value=snap7.util.get_dword(raw,0)
  elif tag.data_type=='BOOL':value=snap7.util.get_bool(raw,0,0)
  else:raise ValueError(f'Unsupported S7 type {tag.data_type}')
  return value*tag.scale+tag.offset if isinstance(value,(int,float)) and not isinstance(value,bool) else value
