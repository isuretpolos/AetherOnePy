import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Injectable({
  providedIn: 'root'
})
export class SocketService {

  constructor(private socket: Socket) {}

  getServerUpdates() {
    return this.socket.fromEvent<{ message: string }>('server_update');
  }

  getBroadcastInfo() {
    return this.socket.fromEvent<{ message: string }>('broadcast_info');
  }
}
