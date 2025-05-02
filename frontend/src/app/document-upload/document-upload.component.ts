import { Component, SecurityContext } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadService } from '../services/upload.service';
import { SkeletonLoaderComponent } from '../components/skeleton-loader/skeleton-loader.component';
import { MarkdownModule, MarkdownService, SECURITY_CONTEXT } from 'ngx-markdown';
import { HttpEventType } from '@angular/common/http';

interface UploadResponse {
  successful_files: Array<{
    filename: string;
    summaries: {
      original: string;
      [key: string]: string;
    };
  }>;
  failed_files?: Array<{
    filename: string;
    error: string;
  }>;
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
export class DocumentUploadComponent {
  selectedFiles: File[] = [];
  uploadProgress: number = 0;
  isUploading: boolean = false;
  isProcessing: boolean = false;
  errorMessage: string = '';
  isDragging: boolean = false;
  selectedLanguage: string = '';
  uploadResults: any[] = [];

  constructor(
    private uploadService: UploadService,
    private markdownService: MarkdownService
  ) {
    this.markdownService.renderer.heading = ({ tokens, depth }: { tokens: any; depth: number }) => {
      const text = tokens.map((token: any) => token.text).join('');
      return `<h${depth} class="markdown-heading">${text}</h${depth}>`;
    };
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

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.handleFiles(Array.from(input.files));
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
    this.uploadProgress = 0;
  }

  async uploadFiles(): Promise<void> {
    if (this.selectedFiles.length === 0) return;

    this.isUploading = true;
    this.isProcessing = true;
    this.errorMessage = '';
    this.uploadResults = [];

    try {
      const formData = new FormData();
      this.selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      if (this.selectedLanguage) {
        formData.append('target_language', this.selectedLanguage);
      }

      this.uploadService.uploadMultipleFiles(this.selectedFiles, this.selectedLanguage)
        .subscribe({
          next: (event: any) => {
            if (event.type === HttpEventType.UploadProgress) {
              this.uploadProgress = Math.round((100 * event.loaded) / event.total);
            } else if (event.type === HttpEventType.Response) {
              this.uploadResults = event.body.successful_files;
              if (event.body.failed_files?.length > 0) {
                this.errorMessage = `Failed to process ${event.body.failed_files.length} file(s)`;
              }
              this.isUploading = false;
              this.selectedFiles = [];
            }
          },
          error: (error) => {
            this.errorMessage = error.message || 'Upload failed';
            this.isUploading = false;
          },
          complete: () => {
            this.isProcessing = false;
            this.uploadProgress = 0;
          }
        });

    } catch (error: any) {
      this.errorMessage = error.message || 'Failed to upload files';
      this.isUploading = false;
      this.isProcessing = false;
    }
  }

  onLanguageChange(): void {
    console.log('Language changed to:', this.selectedLanguage);
    
    if (!this.uploadResults.length || !this.selectedLanguage) {
      return;
    }

    const needsTranslation = this.uploadResults.some(
      result => !result.summaries[this.selectedLanguage]
    );

    if (needsTranslation) {
      console.log('Requesting translation for language:', this.selectedLanguage);
      this.isProcessing = true;
      this.errorMessage = '';

      // Create a deep copy of the results to send for translation
      const summariesToTranslate = this.uploadResults.map(result => ({
        filename: result.filename,
        summaries: { ...result.summaries }
      }));
      
      this.uploadService.uploadMultipleFiles([], this.selectedLanguage, summariesToTranslate)
        .subscribe({
          next: (event: any) => {
            if (event.type === HttpEventType.Response) {
              console.log('Translation response received:', event.body);
              
              if (event.body?.successful_files?.length > 0) {
                // Update the results with new translations
                this.uploadResults = event.body.successful_files;
                console.log('Updated results with translations:', this.uploadResults);
              } else {
                this.errorMessage = 'No translation results received';
              }
              
              if (event.body?.failed_files?.length > 0) {
                this.errorMessage = `Failed to translate ${event.body.failed_files.length} file(s). Please try again.`;
                console.error('Translation failures:', event.body.failed_files);
              }
            }
          },
          error: (error) => {
            console.error('Translation error:', error);
            this.errorMessage = error.message || 'Translation failed. Please try again.';
            this.isProcessing = false;
          },
          complete: () => {
            console.log('Translation request complete');
            this.isProcessing = false;
          }
        });
    } else {
      console.log('Translation already exists for:', this.selectedLanguage);
    }
  }
}
