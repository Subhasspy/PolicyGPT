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
    }

    .site-title {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
    }
  `]
})
export class HeaderComponent {}