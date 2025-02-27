import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Injectable({
  providedIn: 'root'
})
export class SocketService {

  constructor(private socket: Socket) {
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason);
      if (reason === 'io server disconnect') {
        // The disconnection was initiated by the server, reconnect manually
        this.socket.connect();
      }
    });

    this.socket.on('reconnect_attempt', () => {
      console.log('Attempting to reconnect to WebSocket server');
    });
  }

  getServerUpdates() {
    return this.socket.fromEvent<{ message: string }>('server_update');
  }

  getBroadcastInfo() {
    return this.socket.fromEvent<{ message: string }>('broadcast_info');
  }

  ping() {
    this.socket.emit("ping", {})
  }
}
