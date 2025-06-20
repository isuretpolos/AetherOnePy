import {Component, OnInit} from '@angular/core';
import {FormControl} from "@angular/forms";
import {AetherOneService} from "../../services/aether-one.service";
import {ToastrService} from "ngx-toastr";
import {ActivatedRoute, Router} from "@angular/router";
import {BroadCastData} from "../../domains/BroadCastData";

@Component({
  selector: 'app-broadcast',
  templateUrl: './broadcast.component.html',
  styleUrl: './broadcast.component.scss',
  standalone: false
})
export class BroadcastComponent implements OnInit {

  signature = new FormControl('', { nonNullable: true })
  potency = new FormControl('', { nonNullable: true })
  target = new FormControl('', { nonNullable: true })
  level = new FormControl('', { nonNullable: true })

  constructor(
    private aetherOne:AetherOneService,
    private toastr:ToastrService,
    private router: Router,
    private route: ActivatedRoute) {}

  ngOnInit(): void {
  }


  broadcast() {
    const broadcastData : BroadCastData = new BroadCastData()
    broadcastData.signature = this.signature.value;
    broadcastData.potency = this.potency.value;
    broadcastData.target = this.target.value;
    broadcastData.level = this.level.value;

    this.aetherOne.broadcast(broadcastData).subscribe(d => {
      this.toastr.success('Broadcast started successfully', 'Success');
    })
  }
}
