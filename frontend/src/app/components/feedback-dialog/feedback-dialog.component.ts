import { Component, ElementRef, EventEmitter, Inject, Input, OnInit, Output, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-feedback-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './feedback-dialog.component.html',
  styleUrls: ['./feedback-dialog.component.css']
})
export class FeedbackDialogComponent implements OnInit {
  @Input() feedbackType: string = '';
  @Input() isOpen: boolean = false;
  @Output() close = new EventEmitter<void>();
  @Output() submit = new EventEmitter<string>();
  @ViewChild('feedbackTextarea') feedbackTextarea!: ElementRef<HTMLTextAreaElement>;

  feedbackText: string = '';
  private isBrowser: boolean;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  ngOnInit(): void {
    // Add event listener to close dialog when clicking outside
    if (this.isBrowser) {
      document.addEventListener('click', this.handleOutsideClick.bind(this));
    }
  }

  ngOnDestroy(): void {
    // Remove event listener when component is destroyed
    if (this.isBrowser) {
      document.removeEventListener('click', this.handleOutsideClick.bind(this));
    }
  }

  ngAfterViewInit(): void {
    // Focus the textarea when dialog opens
    if (this.isBrowser && this.isOpen && this.feedbackTextarea) {
      setTimeout(() => {
        this.feedbackTextarea.nativeElement.focus();
      }, 100);
    }
  }

  ngOnChanges(): void {
    // Focus the textarea when dialog opens
    if (this.isBrowser && this.isOpen && this.feedbackTextarea) {
      setTimeout(() => {
        this.feedbackTextarea.nativeElement.focus();
      }, 100);
    }
  }

  handleOutsideClick(event: MouseEvent): void {
    // Close dialog when clicking outside
    if (this.isBrowser && this.isOpen && event.target instanceof HTMLElement) {
      const dialogElement = document.querySelector('.feedback-dialog');
      if (dialogElement && !dialogElement.contains(event.target)) {
        this.closeDialog();
      }
    }
  }

  closeDialog(): void {
    this.isOpen = false;
    this.feedbackText = '';
    this.close.emit();
  }

  submitFeedback(): void {
    this.submit.emit(this.feedbackText);
    this.feedbackText = '';
  }

  getFeedbackTitle(): string {
    switch (this.feedbackType) {
      case 'unclear':
        return 'What was unclear about the summary?';
      case 'inaccurate':
        return 'What was inaccurate about the summary?';
      default:
        return 'Please provide your feedback';
    }
  }

  getFeedbackPlaceholder(): string {
    switch (this.feedbackType) {
      case 'unclear':
        return 'Please explain what aspects of the summary were unclear or confusing...';
      case 'inaccurate':
        return 'Please explain what information was incorrect or missing in the summary...';
      default:
        return 'Enter your feedback here...';
    }
  }
}
