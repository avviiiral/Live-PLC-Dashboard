import {Injectable,inject} from '@angular/core';
import {HttpClient,HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
export interface Summary{total:number;passed:number;failed:number;rejection_percentage:number;stations:number;plcs:number}
export interface EventRow{id:string;station:string;station_name:string;plc:string;plc_name:string;occurred_at:string;result_status:string;payload:Record<string,unknown>}
export interface Page<T>{count:number;next:string|null;previous:string|null;results:T[]}
@Injectable({providedIn:'root'})
export class ApiService{
 private http=inject(HttpClient);
 summary():Observable<Summary>{return this.http.get<Summary>('/api/v1/dashboard/summary/')}
 events(page=1,station?:string,result?:string):Observable<Page<EventRow>>{
  let params=new HttpParams().set('page',page);
  if(station)params=params.set('station',station);
  if(result)params=params.set('result',result);
  return this.http.get<Page<EventRow>>('/api/v1/production-events/',{params});
 }
}
