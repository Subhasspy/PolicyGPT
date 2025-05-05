import { Component, OnInit, SecurityContext, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadService } from '../services/upload.service';
import { SkeletonLoaderComponent } from '../components/skeleton-loader/skeleton-loader.component';
import { MarkdownModule, MarkdownService, SECURITY_CONTEXT } from 'ngx-markdown';

interface DocumentResult {
  filename: string;
  summaries: {
    original: string;
    [key: string]: string;
  };
  error?: string;
}

interface FeedbackStatus {
  status: 'none' | 'submitting' | 'success' | 'error';
  message?: string;
  feedbackType?: string;
}

@Component({
  selector: 'app-document-upload',
  standalone: true,
  imports: [CommonModule, FormsModule, SkeletonLoaderComponent, MarkdownModule],
  templateUrl: './document-upload.component.html',
  styleUrls: ['./document-upload.component.css'],
  providers: [
    { provide: SECURITY_CONTEXT, useValue: SecurityContext.HTML }
  ]
})
export class DocumentUploadComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;
  selectedFiles: File[] = [];
  selectedLanguage: string = '';
  results: DocumentResult[] = [];
  languages: { code: string; name: string; }[] = [];
  isProcessing: boolean = false;
  errorMessage: string = '';
  isDragging: boolean = false;
  feedbackStatus: { [key: string]: FeedbackStatus } = {};

  constructor(
    private uploadService: UploadService,
    private markdownService: MarkdownService
  ) {
    this.markdownService.renderer.heading = ({ tokens, depth }: { tokens: any; depth: number }) => {
      const text = tokens.map((token: any) => token.text).join('');
      return `<h${depth} class="markdown-heading">${text}</h${depth}>`;
    };
  }

  ngOnInit() {
    this.loadLanguages();
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
    
    const files = event.dataTransfer?.files;
    if (files) {
      this.handleFiles(Array.from(files));
    }
  }

  onFileSelected(event: any): void {
    const files: FileList = event.target.files;
    if (files && files.length > 0) {
      this.handleFiles(Array.from(files));
    }
  }

  handleFiles(files: File[]): void {
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    if (pdfFiles.length === 0) {
      this.errorMessage = 'Please select PDF files only';
      return;
    }
    this.selectedFiles = [...this.selectedFiles, ...pdfFiles];
    this.errorMessage = '';
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  clearFiles(): void {
    this.selectedFiles = [];
    this.errorMessage = '';
    this.results = [];
    this.isProcessing = false;
  }

  async uploadFiles(): Promise<void> {
    if (this.selectedFiles.length === 0) return;

    this.results = [];
    this.isProcessing = true;
    this.errorMessage = '';

    try {
      const formData = new FormData();
      this.selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      if (this.selectedLanguage) {
        formData.append('target_language', this.selectedLanguage);
      }

      this.uploadService.uploadFiles(formData).subscribe({
        next: (response) => {
          if (response) {
            // Check for per-file errors
            const hasErrors = response.results.some(result => result.error);
            if (hasErrors) {
              this.errorMessage = response.results
                .filter(result => result.error)
                .map(result => `${result.filename}: ${result.error}`)
                .join('\n');
            }
            this.results = response.results;
          }
        },
        error: (error) => {
          this.errorMessage = error;
          console.error('Upload error:', error);
          this.isProcessing = false;
        },
        complete: () => {
          this.isProcessing = false;
        }
      });

    } catch (err: any) {
      this.errorMessage = err.message || 'Error processing files. Please try again.';
      console.error('Upload error:', err);
      this.isProcessing = false;
    }
  }

  private async loadLanguages(): Promise<void> {
    try {
      const response = await this.uploadService.getSupportedLanguages().toPromise();
      this.languages = Object.entries(response.supported_languages).map(([code, name]) => ({
        code,
        name: name as string
      }));
    } catch (err) {
      console.error('Error loading languages:', err);
      this.errorMessage = 'Error loading supported languages';
    }
  }

  private setFeedbackType(filename: string, type: string): void {
    this.feedbackStatus[filename] = this.feedbackStatus[filename] || { status: 'none' };
    this.feedbackStatus[filename].feedbackType = type;
  }

  getFeedbackType(filename: string): string {
    return this.feedbackStatus[filename]?.feedbackType || '';
  }

  submitFeedback(result: DocumentResult, feedbackType: string): void {
    this.setFeedbackType(result.filename, feedbackType);
    this.feedbackStatus[result.filename] = { 
      status: 'submitting',
      feedbackType
    };

    this.uploadService.submitFeedback({
      summary_id: result.filename,
      feedback_type: feedbackType
    }).subscribe({
      next: () => {
        this.feedbackStatus[result.filename] = { 
          status: 'success',
          message: `Thank you! Your "${feedbackType}" feedback has been recorded.`,
          feedbackType
        };
        setTimeout(() => {
          if (this.feedbackStatus[result.filename]?.status === 'success') {
            delete this.feedbackStatus[result.filename];
          }
        }, 3000);
      },
      error: (error) => {
        console.error('Error submitting feedback:', error);
        this.feedbackStatus[result.filename] = {
          status: 'error',
          message: 'Failed to submit feedback. Please try again.',
          feedbackType
        };
      }
    });
  }

  openFileSelector(): void {
    this.fileInput.nativeElement.click();
  }

  isFeedbackSubmitting(filename: string, type: string): boolean {
    const status = this.feedbackStatus[filename];
    return status?.status === 'submitting' && status?.feedbackType === type;
  }

  getFeedbackStatus(filename: string): FeedbackStatus | null {
    return this.feedbackStatus[filename] || null;
  }

  isFeedbackSuccess(filename: string): boolean {
    return this.feedbackStatus[filename]?.status === 'success';
  }

  isFeedbackError(filename: string): boolean {
    return this.feedbackStatus[filename]?.status === 'error';
  }

  getFeedbackMessage(filename: string): string {
    return this.feedbackStatus[filename]?.message || '';
  }
}
