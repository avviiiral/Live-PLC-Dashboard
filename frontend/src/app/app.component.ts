import {Component} from '@angular/core';
import {RouterLink,RouterLinkActive,RouterOutlet} from '@angular/router';
@Component({selector:'app-root',standalone:true,imports:[RouterLink,RouterLinkActive,RouterOutlet],template:`
<div class="layout">
 <aside><div class="brand"><b>LP</b><span>LIVE PLC<small>INDUSTRIAL INTELLIGENCE</small></span></div>
 <p>WORKSPACE</p><a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">▦ Overview</a><a routerLink="/production" routerLinkActive="active">▤ Production data</a>
 <p>CONFIGURATION</p><a routerLink="/settings" routerLinkActive="active">⚙ System settings</a>
 <div class="sidefoot">Platform interface · Development</div></aside>
 <main><header><span>MANUFACTURING OPERATIONS<br><strong>Plant monitoring</strong></span><span>IIoT PLATFORM</span></header><section><router-outlet/></section></main>
</div>`})
export class AppComponent{}
