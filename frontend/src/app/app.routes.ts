import {Routes} from '@angular/router';
import {DashboardComponent} from './pages/dashboard.component';
import {ProductionDataComponent} from './pages/production-data.component';
import {SettingsComponent} from './pages/settings.component';
export const routes:Routes=[{path:'',component:DashboardComponent},{path:'production',component:ProductionDataComponent},{path:'settings',component:SettingsComponent},{path:'**',redirectTo:''}];
