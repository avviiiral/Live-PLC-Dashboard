import json,logging,os,signal,threading
from pathlib import Path
from dotenv import load_dotenv
from collector.adapters.mock_plc import MockPLCAdapter
from collector.adapters.siemens_s7 import SiemensS7Adapter
from collector.adapters.modbus_tcp import ModbusTCPAdapter
from collector.communication.api_client import BackendClient
from collector.core.types import PLCConfig,TagConfig
from collector.storage.queue import PersistentEventQueue
from collector.services.runner import StationRunner
def main():
 load_dotenv();logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'))
 path=Path(os.getenv('COLLECTOR_CONFIG_PATH','collector/config/example.json'))
 if not path.exists():raise RuntimeError(f'Collector config missing: {path}')
 cfg=json.loads(path.read_text(encoding='utf-8'))
 api=BackendClient(os.getenv('COLLECTOR_API_BASE_URL') or cfg.get('backend_url'),os.getenv('COLLECTOR_TOKEN') or cfg.get('collector_token'))
 queue=PersistentEventQueue(os.getenv('COLLECTOR_QUEUE_PATH',cfg.get('queue_path','collector/data/queue.sqlite3')))
 if not cfg.get('stations'):raise RuntimeError('No stations configured; refusing to start')
 stop=threading.Event()
 def shutdown(sig,frame):stop.set()
 signal.signal(signal.SIGINT,shutdown);signal.signal(signal.SIGTERM,shutdown)
 runners=[]
 for station in cfg['stations']:
  p=station['plc'];pc=PLCConfig(p['protocol'],p['host'],int(p.get('port',102)),int(p.get('rack',0)),int(p.get('slot',1)),int(p.get('unit_id',1)))
  adapters={'mock':lambda:MockPLCAdapter(),'s7':lambda:SiemensS7Adapter(pc),'modbus_tcp':lambda:ModbusTCPAdapter(pc)}
  if pc.protocol not in adapters:raise ValueError(f'Unsupported protocol {pc.protocol}')
  tags=[TagConfig(**t) for t in station['tags']]
  runners.append(StationRunner(station['station_id'],p['id'],adapters[pc.protocol](),tags,station['event'],api,queue,cfg.get('poll_interval_seconds',.25)))
 threads=[threading.Thread(target=r.run,args=(stop,),daemon=True) for r in runners]
 for t in threads:t.start()
 while not stop.wait(30):
  try:api.heartbeat({'queue_size':queue.size(),'stations':len(runners)})
  except Exception:logging.exception('Collector heartbeat failed')
 for r in runners:r.adapter.disconnect()
 for t in threads:t.join(timeout=5)
if __name__=='__main__':main()
