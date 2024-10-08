import {Injectable} from '@angular/core';
import {environment} from "../../environments/environment";
import {BehaviorSubject, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {Case} from "../domains/Case";

@Injectable({
  providedIn: 'root'
})
export class AetherOneService {

  baseUrl:string = environment.baseUrl
  case$ = new BehaviorSubject<Case|undefined>(undefined);

  constructor(private http:HttpClient) { }

  ping():Observable<any> {
    return this.http.get(`${this.baseUrl}ping`, {responseType: 'text'})
  }


}
