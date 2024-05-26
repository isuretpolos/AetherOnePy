import { Injectable } from '@angular/core';
import {environment} from "../../environments/environment";
import {Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class AetherOneService {

  baseUrl:string = environment.baseUrl;

  constructor(private http:HttpClient) { }

  ping():Observable<any> {
    return this.http.get(`${this.baseUrl}ping`, {responseType: 'text'});
  }
}
