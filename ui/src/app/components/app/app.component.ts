import {Component, OnDestroy, OnInit, ElementRef} from '@angular/core';
import {Link} from "../../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";
import {NavigationService} from "../../services/navigation.service";
import {Case} from "../../domains/Case";
import {AetherOneService} from "../../services/aether-one.service";
import {FormControl} from "@angular/forms";
import {SocketService} from "../../services/socket.service";
import {ToastrService} from "ngx-toastr";
import * as THREE from 'three'

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
    standalone: false
})
export class AppComponent implements OnInit, OnDestroy  {

  serverOnline:boolean = false;
  links: Link[] = [];
  case:Case = new Case()
  theme:string = "dark"
  searchText = new FormControl('');
  mobileMode:boolean = false
  hotbitsCount: number = 0
  webCamRunning: boolean = false
  version: string = ''
  remoteVersion: string = ''
  cpuCount:string = ''
  broadcastingData:any
  intervalBroadcastingId: any;
  intervalPing: any;
  systemInfo: any;

  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private cube!: THREE.Mesh;
  private animationFrameId!: number;

  constructor(private router: Router,
              private route: ActivatedRoute,
              private navigationService:NavigationService,
              private aetherOne: AetherOneService,
              private socketService: SocketService,
              private toastr: ToastrService,
              private el: ElementRef) {
  }

  ngOnInit() {

    this.initThreeJs();
    this.animate();

    if (this.intervalPing) clearInterval(this.intervalPing);
    if (this.intervalBroadcastingId) clearInterval(this.intervalBroadcastingId);

    // Listen for server updates
    this.socketService.getServerUpdates().subscribe((data) => {
      console.log(data)
      this.toastr.info(data.message);
    });

    this.socketService.getBroadcastInfo().subscribe((data) => {
      console.log(data)
      this.toastr.info(data.message);
    });

    this.intervalPing = setInterval(() => {
      this.socketService.ping();
    }, 3000);

    this.intervalBroadcastingId = setInterval(() => {
      this.aetherOne.getCurrentBroadcastTasks().subscribe(b => {
        this.broadcastingData = b
      })
    }, 3000)

    this.aetherOne.cpuCount().subscribe( c => this.cpuCount = c)

    // this.theme = localStorage.getItem('theme') ?? 'light';
    // document.documentElement.setAttribute('data-bs-theme',this.theme)
    document.documentElement.setAttribute('data-bs-theme','light')

    if (this.isMobileDevice()) {
      console.log('mobile device')
      this.mobileMode = true
      this.navigate('MOBILE')
    } else {
      console.log('desktop or laptop device')
      this.mobileMode = false
    }

    this.ping()
    this.initLinks()
    this.checkVersion()
    this.navigationService.navigate.subscribe( (url:string) => {
      this.navigate(url);
    });
    // @ts-ignore
    this.theme = localStorage.getItem('theme')
    this.aetherOne.case$.subscribe(value => {
      this.case = value
    })

    this.countHotbits()
  }

  /**
   * Checks the current version of the application and compares it with the remote version.
   * It schedules another check after 60 seconds.
   */
  checkVersion() {
    this.aetherOne.version().subscribe( v => {
      this.version = v
      this.aetherOne.remoteVersion().subscribe( v => {
        this.remoteVersion = v
        setTimeout(()=>{this.checkVersion()}, 60000)
      })
    })
  }

  countHotbits() {
    this.aetherOne.countHotbits().subscribe( c => this.hotbitsCount = c.count)
    this.aetherOne.isWebCamHotRunning().subscribe( r => this.webCamRunning = r['running'])
    setTimeout(()=>{this.countHotbits()}, 10000)
  }

  navigate(navigationPath: string) {
    this.activateCurrentLink(navigationPath);
    this.router.navigate([navigationPath], {relativeTo: this.route});
  }

  private activateCurrentLink(navigationPath?: string) {

    if (navigationPath?.length === 0) {
      navigationPath = 'DASHBOARD';
    }

    this.links.forEach(link => {
      link.active = false;

      if (link.name === navigationPath) {
        link.active = true;
      }
    });
  }

  private initLinks() {
    this.addLink("BROADCAST", false, "#0c7e05", "#fff");
    this.addLink("APPS", false, "#282086", "#fff");
    this.addLink("MANUAL", false, "#133185", "#fff");
    this.addLink("SETTINGS", false, "#ff9520", "#000");
  }

  private addLink(name: string, active: boolean, backgroundColor:string, color: string) {
    let link:Link = new Link();
    link.name = name;
    link.active = active;
    link.backgroundColor = backgroundColor;
    link.color = color;
    this.links.push(link)
  }

  isMobileDevice(): boolean {
    // @ts-ignore
    const userAgent = navigator.userAgent || navigator.vendor || window['opera'];
    const mobileRegex = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i;

    return mobileRegex.test(userAgent);
  }


  switchTheme() {
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
      document.documentElement.setAttribute('data-bs-theme','light')
      localStorage.setItem('theme', 'light')
      this.theme = "light"
    }
    else {
      document.documentElement.setAttribute('data-bs-theme','dark')
      localStorage.setItem('theme', 'dark')
      this.theme = "dark"
    }
  }

  search() {

  }

  private ping() {
    this.aetherOne.ping().subscribe({
      next: (info) => {
        this.serverOnline = true
        this.systemInfo = info
        localStorage.setItem('systemInfo', JSON.stringify(info));
      },
      error: () => {
        this.serverOnline = false;
        this.toastr.error('Server is offline!', 'AetherOnePy');
      }
    });

    setTimeout(() => {
      this.ping();
    }, 5000);
  }

  protected readonly length = length;

  ngOnDestroy(): void {
    clearInterval(this.intervalPing);
    clearInterval(this.intervalBroadcastingId);
    // Cancel the animation frame on destroy
    cancelAnimationFrame(this.animationFrameId);
    this.renderer.dispose();
  }

  stopAllBroadcasting() {
    this.aetherOne.stopAllBroadcasts().subscribe(()=>this.toastr.info("All broadcasts stopped!"))
  }

  private initThreeJs(): void {
    // Create the scene
    this.scene = new THREE.Scene();

    // Create the camera
    this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.camera.position.z = 5;

    // Create the renderer
    this.renderer = new THREE.WebGLRenderer();
    //this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setSize(300, 200);
    this.el.nativeElement.querySelector('#broadcastingGraphic').appendChild(this.renderer.domElement);

    // Create a cube
    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    this.cube = new THREE.Mesh(geometry, material);

    // Add the cube to the scene
    this.scene.add(this.cube);
  }

  private animate = (): void => {
    // Rotation logic
    this.cube.rotation.x += 0.01;
    this.cube.rotation.y += 0.01;

    // Render the scene
    this.renderer.render(this.scene, this.camera);

    // Request the next frame
    this.animationFrameId = requestAnimationFrame(this.animate);
  };

  shutDown() {
    if (!confirm('Are you sure you want to shutdown AetherOnePy?')) return
    this.aetherOne.shutdown().subscribe( ()=> {
      this.toastr.info("Shutting down AetherOnePy...")
      console.log("Shutting down AetherOnePy...")
    })
  }

  protected readonly confirm = confirm;

  restartServer() {
    if (!confirm('Are you sure you want to restart AetherOnePy?')) return
    this.aetherOne.restart().subscribe( ()=> {
      this.toastr.info("Restarting AetherOnePy...")
      console.log("Restarting AetherOnePy...")
    })
  }
}
