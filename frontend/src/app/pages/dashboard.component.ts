import {Component,OnInit,inject} from '@angular/core';
import {DatePipe} from '@angular/common';
import {ApiService,Summary,EventRow} from '../core/api.service';
@Component({standalone:true,selector:'app-dashboard',imports:[DatePipe],template:`
<div class="heading"><div><small>LIVE OPERATIONS</small><h1>Production overview</h1><p>Monitor output, quality and recent station events.</p></div><button (click)="load()">↻ Refresh</button></div>
@if(error){<p class="error">{{error}}</p>}
<div class="cards">
 <article>Total events<strong>{{summary?.total ?? '—'}}</strong><small>Recorded production events</small></article>
 <article>PASS<strong class="good">{{summary?.passed ?? '—'}}</strong><small>Accepted production</small></article>
 <article>FAIL<strong class="bad">{{summary?.failed ?? '—'}}</strong><small>Rejected production</small></article>
 <article>Rejection rate<strong>{{summary?.rejection_percentage ?? '—'}}%</strong><small>Based on recorded events</small></article>
</div>
<div class="panel"><div class="panel-head"><div><h2>Latest production events</h2><p>Most recent events received by the backend</p></div></div>
<table><thead><tr><th>TIMESTAMP</th><th>STATION</th><th>PLC</th><th>RESULT</th></tr></thead><tbody>
@for(event of events;track event.id){<tr><td>{{event.occurred_at|date:'medium'}}</td><td>{{event.station_name}}</td><td>{{event.plc_name}}</td><td><span class="status" [class.pass]="event.result_status==='PASS'" [class.fail]="event.result_status==='FAIL'">{{event.result_status}}</span></td></tr>}
</tbody></table>
@if(!events.length){<div class="empty"><b>No production events yet</b><span>Connect a collector and send the first event to populate this dashboard.</span></div>}
</div>
<div class="panel resources"><h2>Configured infrastructure</h2><p>Active stations: <b>{{summary?.stations ?? '—'}}</b> &nbsp; Enabled PLCs: <b>{{summary?.plcs ?? '—'}}</b></p><small>Live machine state requires fresh collector telemetry; the dashboard does not fabricate values.</small></div>
`})
export class DashboardComponent implements OnInit{
 private api=inject(ApiService);summary:Summary|null=null;events:EventRow[]=[];error='';
 ngOnInit(){this.load()}
 load(){
  this.error='';
  this.api.summary().subscribe({next:value=>this.summary=value,error:()=>this.error='Could not load summary. Sign in and verify that the backend is running.'});
  this.api.events().subscribe({next:value=>this.events=value.results,error:()=>this.error='Could not load production events. Check API access.'});
 }
}
