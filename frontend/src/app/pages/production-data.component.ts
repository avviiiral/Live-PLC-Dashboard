import {Component,OnInit,inject} from '@angular/core';
import {DatePipe,JsonPipe} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {ApiService,EventRow} from '../core/api.service';
@Component({standalone:true,selector:'app-production-data',imports:[DatePipe,JsonPipe,FormsModule],template:`
<div class="heading"><div><small>TRACEABILITY</small><h1>Production data</h1><p>Search and review station production records.</p></div><button (click)="load()">↻ Refresh</button></div>
<div class="panel">
 <div class="filters">
  <label>Station UUID<input [(ngModel)]="station" placeholder="Optional station identifier"></label>
  <label>Result<select [(ngModel)]="result"><option value="">All results</option><option value="PASS">PASS</option><option value="FAIL">FAIL</option></select></label>
  <button (click)="page=1;load()">Apply filters</button>
 </div>
 <div class="table-scroll"><table><thead><tr><th>TIMESTAMP</th><th>STATION</th><th>PLC</th><th>RESULT</th><th>TAG PAYLOAD</th></tr></thead><tbody>
 @for(event of events;track event.id){<tr><td>{{event.occurred_at|date:'yyyy-MM-dd HH:mm:ss'}}</td><td>{{event.station_name}}</td><td>{{event.plc_name}}</td><td><span class="status" [class.pass]="event.result_status==='PASS'" [class.fail]="event.result_status==='FAIL'">{{event.result_status}}</span></td><td><code>{{event.payload|json}}</code></td></tr>}
 </tbody></table></div>
 @if(!events.length){<div class="empty"><b>No matching production records</b><span>Change the filters or wait for new collector events.</span></div>}
 <footer><button class="secondary" [disabled]="page<=1" (click)="page--;load()">Previous</button><span>Page {{page}} · {{count}} records</span><button class="secondary" [disabled]="!hasNext" (click)="page++;load()">Next</button></footer>
</div>
`})
export class ProductionDataComponent implements OnInit{
 private api=inject(ApiService);events:EventRow[]=[];station='';result='';page=1;count=0;hasNext=false;
 ngOnInit(){this.load()}
 load(){this.api.events(this.page,this.station.trim()||undefined,this.result||undefined).subscribe({next:value=>{this.events=value.results;this.count=value.count;this.hasNext=!!value.next},error:()=>{this.events=[];this.count=0;this.hasNext=false}})}
}
