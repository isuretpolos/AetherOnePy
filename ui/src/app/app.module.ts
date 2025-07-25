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
import {environment} from "../environments/environment";
import { HotbitsComponent } from './components/hotbits/hotbits.component';
import { RadionicsDeviceBase44Component } from './components/radionics-device-base44/radionics-device-base44.component';
import { AppsComponent } from './components/apps/apps.component';
import { VersionComponent } from './components/version/version.component';
import {BroadcastComponent} from "./components/broadcast/broadcast.component";
import {LoadingInterceptor} from "./services/loadingInterceptor";
import {HTTP_INTERCEPTORS} from "@angular/common/http";

const socketHost = environment.socketHost || window.location.hostname;
const url = `http://${socketHost}:80`;
const config: SocketIoConfig = {
  url,
  options: {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 10, // Tries to reconnect 10 times
    reconnectionDelay: 5000    // Wait 5 seconds before retrying
  }
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
    AppsComponent,
    VersionComponent,
    BroadcastComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    ReactiveFormsModule,
    SocketIoModule.forRoot(config),
    ToastrModule.forRoot()
  ],
  providers: [
    {provide: LocationStrategy, useClass: HashLocationStrategy},
    {provide: HTTP_INTERCEPTORS,useClass: LoadingInterceptor,multi: true}
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
