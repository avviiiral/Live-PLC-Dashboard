from dataclasses import dataclass
from typing import Any,Protocol
@dataclass(frozen=True)
class PLCConfig:
 protocol:str
 host:str
 port:int
 rack:int=0
 slot:int=1
 unit_id:int=1
@dataclass(frozen=True)
class TagConfig:
 id:str
 name:str
 address:str
 data_type:str
 role:str='normal'
 scale:float=1
 offset:float=0
class PLCAdapter(Protocol):
 def connect(self)->None:...
 def disconnect(self)->None:...
 def read(self,tag:TagConfig)->Any:...
 def is_connected(self)->bool:...
