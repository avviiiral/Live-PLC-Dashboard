import {Injectable,NgZone,inject} from '@angular/core';
import {Observable} from 'rxjs';
import {EventRow} from './api.service';
@Injectable({providedIn:'root'})
export class LiveService{
 private zone=inject(NgZone);
 connect(stationId:string):Observable<EventRow>{
  return new Observable(subscriber=>{
   const protocol=location.protocol==='https:'?'wss':'ws';
   const socket=new WebSocket(protocol+'://'+location.host+'/ws/stations/'+stationId+'/');
   socket.onmessage=(message:MessageEvent<string>)=>this.zone.run(()=>{
    try{const parsed=JSON.parse(message.data) as {type:string;data:EventRow};if(parsed.type==='production_event')subscriber.next(parsed.data)}
    catch(error){subscriber.error(error)}
   });
   socket.onerror=()=>this.zone.run(()=>subscriber.error(new Error('WebSocket connection failed')));
   socket.onclose=()=>this.zone.run(()=>subscriber.complete());
   return()=>socket.close();
  });
 }
}
