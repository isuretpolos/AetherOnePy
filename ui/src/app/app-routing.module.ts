import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {HttpClientModule} from "@angular/common/http";
import {HomeComponent} from "./components/home/home.component";

const routes: Routes = [
  {path: '', redirectTo: 'HOME', pathMatch: 'full'},
  {path: 'HOME', component: HomeComponent},
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes),
    HttpClientModule
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
