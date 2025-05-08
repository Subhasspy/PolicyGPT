import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <header class="site-header">
      <div class="header-content">
        <h1 class="site-title">PolicyGPT</h1>
        <nav class="site-nav">
          <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">Home</a>
        </nav>
      </div>
    </header>
  `,
  styles: [`
    .site-header {
      background-color: #2c3e50;
      color: white;
      padding: 1rem 0;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .site-title {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
    }

    .site-nav {
      display: flex;
      gap: 1.5rem;
    }

    .site-nav a {
      color: white;
      text-decoration: none;
      font-weight: 500;
      padding: 0.5rem 0;
      position: relative;
    }

    .site-nav a:after {
      content: '';
      position: absolute;
      width: 0;
      height: 2px;
      bottom: 0;
      left: 0;
      background-color: white;
      transition: width 0.3s;
    }

    .site-nav a:hover:after,
    .site-nav a.active:after {
      width: 100%;
    }
  `]
})
export class HeaderComponent {}