import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './components/app/app.component';
import {HashLocationStrategy, LocationStrategy} from "@angular/common";
import { HomeComponent } from './components/home/home.component';
import { DocumentationComponent } from './components/documentation/documentation.component';
import { SettingsComponent } from './components/settings/settings.component';
import {ReactiveFormsModule} from "@angular/forms";
import { MobileComponent } from './components/mobile/mobile.component';
import { CaseComponent } from './components/case/case.component';
import { RateCardsComponent } from './components/rate-cards/rate-cards.component';
import {SocketIoConfig, SocketIoModule} from "ngx-socket-io";
import {ToastrModule} from "ngx-toastr";
import { HotbitsComponent } from './components/hotbits/hotbits.component';
import { RadionicsDeviceBase44Component } from './components/radionics-device-base44/radionics-device-base44.component';
import { AppsComponent } from './components/apps/apps.component';

const config: SocketIoConfig = {
  url: 'http://localhost:80', // Replace with your Flask server's URL
  options: {}
};

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    DocumentationComponent,
    SettingsComponent,
    MobileComponent,
    CaseComponent,
    RateCardsComponent,
    HotbitsComponent,
    RadionicsDeviceBase44Component,
    AppsComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    ReactiveFormsModule,
    SocketIoModule.forRoot(config),
    ToastrModule.forRoot()
  ],
  providers: [{provide: LocationStrategy, useClass: HashLocationStrategy}],
  bootstrap: [AppComponent]
})
export class AppModule { }
