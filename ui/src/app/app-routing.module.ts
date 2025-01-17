import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {HttpClientModule} from "@angular/common/http";
import {HomeComponent} from "./components/home/home.component";
import {DocumentationComponent} from "./components/documentation/documentation.component";
import {SettingsComponent} from "./components/settings/settings.component";
import {MobileComponent} from "./components/mobile/mobile.component";
import {CaseComponent} from "./components/case/case.component";
import {RateCardsComponent} from "./components/rate-cards/rate-cards.component";

const routes: Routes = [
  {path: '', redirectTo: 'HOME', pathMatch: 'full'},
  {path: 'HOME', component: HomeComponent},
  {path: 'CARDS', component: RateCardsComponent},
  {path: 'MANUAL', component: DocumentationComponent},
  {path: 'SETTINGS', component: SettingsComponent},
  {path: 'MOBILE', component: MobileComponent},
  {path: 'CASE', component: CaseComponent},
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes),
    HttpClientModule
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
