import {Component, OnInit} from '@angular/core';
import {Link} from "../../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";
import {NavigationService} from "../../services/navigation.service";
import {Case} from "../../domains/Case";
import {AetherOneService} from "../../services/aether-one.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  serverOnline:boolean = false;
  links: Link[] = [];
  case:Case = new Case()
  theme:string = "dark"

  constructor(private router: Router,
              private route: ActivatedRoute,
              private navigationService:NavigationService,
              private aetherOne: AetherOneService) {
  }

  ngOnInit() {
    this.ping()
    this.initLinks()
    this.navigationService.navigate.subscribe( (url:string) => {
      this.navigate(url);
    });
    // @ts-ignore
    this.theme = localStorage.getItem('theme')
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
    this.addLink("HOME", true, "#d3d3d3");
    this.addLink("CASES", false, "#a1a1a1");
    this.addLink("ANALYSIS", false, "#a1a1a1");
    this.addLink("MAP", false, "#a1a1a1");
    this.addLink("WEAVER", false, "#a1a1a1");
    this.addLink("BROADCAST", false, "#a1a1a1");
    this.addLink("SETTINGS", false, "#ffd19d");
  }

  private addLink(name: string, active: boolean, color: string) {
    let link = new Link();
    link.name = name;
    link.active = active;
    link.color = color;
    this.links.push(link)
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

  private ping() {
    this.aetherOne.ping().subscribe({
      next: () => {this.serverOnline = true},
      error: () => {this.serverOnline = false}
    });

    setTimeout(() => {
      this.ping();
    }, 5000);
  }
}
