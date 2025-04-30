import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-skeleton-loader',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="skeleton-loader" [ngStyle]="{'height.px': height, 'width': width}">
      <div class="shimmer"></div>
    </div>
  `,
  styles: [`
    .skeleton-loader {
      background: #eee;
      border-radius: 4px;
      position: relative;
      overflow: hidden;
    }

    .shimmer {
      width: 100%;
      height: 100%;
      background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.2) 50%,
        rgba(255, 255, 255, 0) 100%
      );
      position: absolute;
      top: 0;
      left: 0;
      animation: loading 1.5s infinite;
    }

    @keyframes loading {
      0% {
        transform: translateX(-100%);
      }
      100% {
        transform: translateX(100%);
      }
    }
  `]
})
export class SkeletonLoaderComponent {
  @Input() width: string = '100%';
  @Input() height: number = 20;
}