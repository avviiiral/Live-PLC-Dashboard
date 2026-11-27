from collector.core.types import PLCConfig,TagConfig
class ModbusTCPAdapter:
 def __init__(self,cfg:PLCConfig):self.cfg=cfg;self.client=None
 def connect(self):
  try:from pymodbus.client import ModbusTcpClient
  except ImportError as exc:raise RuntimeError('Install pymodbus') from exc
  self.client=ModbusTcpClient(self.cfg.host,port=self.cfg.port)
  if not self.client.connect():raise ConnectionError('Modbus TCP connection failed')
 def disconnect(self):
  if self.client:self.client.close();self.client=None
 def is_connected(self):return bool(self.client and self.client.connected)
 def read(self,tag:TagConfig):
  if not self.is_connected():raise ConnectionError('Modbus client disconnected')
  area,sep,num=tag.address.partition(':');bases={'holding':40001,'input':30001,'coil':1,'discrete':10001}
  if not sep or not num.isdigit() or area not in bases:raise ValueError('Use holding:40001, input:30001, coil:00001, discrete:10001')
  addr=int(num)-bases[area];unit=self.cfg.unit_id
  if area in ('holding','input'):
   fn=self.client.read_holding_registers if area=='holding' else self.client.read_input_registers;result=fn(addr,count=1,device_id=unit)
   if result.isError():raise IOError(str(result))
   value=result.registers[0]
  else:
   fn=self.client.read_coils if area=='coil' else self.client.read_discrete_inputs;result=fn(addr,count=1,device_id=unit)
   if result.isError():raise IOError(str(result))
   value=result.bits[0]
  return value*tag.scale+tag.offset if isinstance(value,(int,float)) and not isinstance(value,bool) else value
