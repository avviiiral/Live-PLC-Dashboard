import {Component} from '@angular/core';
@Component({standalone:true,selector:'app-settings',template:`
<div class="heading"><div><small>PLATFORM CONFIGURATION</small><h1>System settings</h1><p>Environment and integration guidance for this deployment.</p></div></div>
<div class="panel settings">
 <h2>Database</h2><p>Use <code>DB_ENGINE=sqlite</code> for local development or <code>DB_ENGINE=postgresql</code> in production. Database credentials belong in environment variables.</p>
 <h2>Collector security</h2><p>Register collectors through the staff-only provisioning endpoint and assign only their authorized stations. Never expose collector tokens or factory PLC addresses to browser clients.</p>
 <h2>Real-time delivery</h2><p>The dashboard WebSocket client expects an authenticated Django session and the station WebSocket route. Production deployments need Redis Channels and station-level authorization.</p>
 <h2>Hardware validation</h2><p>Siemens S7 and Modbus TCP adapter configuration must be tested against the target PLC, firmware, address map and factory network before production use.</p>
</div>`})
export class SettingsComponent{}
