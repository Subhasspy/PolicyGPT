import { Component, OnInit, SecurityContext, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UploadService } from '../services/upload.service';
import { HttpClient } from '@angular/common/http';
import { CustomerInterest } from '../models/customer-profile.model';
import { SkeletonLoaderComponent } from '../components/skeleton-loader/skeleton-loader.component';
import { FeedbackDialogComponent } from '../components/feedback-dialog/feedback-dialog.component';
import { MarkdownModule, MarkdownService, SECURITY_CONTEXT } from 'ngx-markdown';
import { environment } from '../../environments/environment';

interface DocumentResult {
  filename: string;
  summaries: {
    original: string;
    [key: string]: string;
  };
  originalText?: string;
  personalized?: boolean;
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
  imports: [CommonModule, FormsModule, SkeletonLoaderComponent, FeedbackDialogComponent, MarkdownModule],
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

  // Personalization options
  readingLevel: string = 'intermediate';
  selectedInterests: string[] = [];
  ageGroup: string = '';

  // Available options for personalization
  customerInterests: CustomerInterest[] = [];
  readingLevels = [
    { code: 'basic', name: 'Basic' },
    { code: 'intermediate', name: 'Intermediate' },
    { code: 'advanced', name: 'Advanced' }
  ];
  ageGroups = [
    { code: '18-25', name: '18-25' },
    { code: '26-35', name: '26-35' },
    { code: '36-50', name: '36-50' },
    { code: '51+', name: '51+' }
  ];

  // Feedback dialog properties
  showFeedbackDialog: boolean = false;
  currentFeedbackType: string = '';
  currentFeedbackResult: DocumentResult | null = null;


  constructor(
    private uploadService: UploadService,
    private http: HttpClient,
    private markdownService: MarkdownService
  ) {
    // Configure markdown renderer for better display of long content
    this.markdownService.renderer.heading = ({ tokens, depth }: { tokens: any; depth: number }) => {
      const text = tokens.map((token: any) => token.text).join('');
      return `<h${depth} class="markdown-heading">${text}</h${depth}>`;
    };

    // Ensure paragraphs are properly rendered
    this.markdownService.renderer.paragraph = (paragraph: any) => {
      return `<p class="markdown-paragraph">${paragraph.text}</p>`;
    };

    // Configure options to handle long content
    this.markdownService.options = {
      ...this.markdownService.options,
      breaks: true,  // Add line breaks on single line breaks
      gfm: true,     // Enable GitHub Flavored Markdown
    };
  }

  ngOnInit() {
    this.loadLanguages();
    this.loadCustomerInterests();
  }

  loadCustomerInterests(): void {
    this.http.get<{ customer_interests: CustomerInterest[] }>(`${environment.apiUrl}/customer-interests`).subscribe({
      next: (response) => {
        this.customerInterests = response.customer_interests;
      },
      error: (error) => {
        console.error('Error loading customer interests:', error);
      }
    });
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

      // Add personalization parameters
      // Add reading level
      if (this.readingLevel) {
        formData.append('reading_level', this.readingLevel);
      }

      // Add interests as comma-separated list
      if (this.selectedInterests.length > 0) {
        formData.append('interests', this.selectedInterests.join(','));
      }

      // Add age group if provided
      if (this.ageGroup) {
        formData.append('age_group', this.ageGroup);
      }

      // Check if personalization is being used
      const isPersonalized = this.isPersonalizationUsed();

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

            // Log summary lengths for debugging
            response.results.forEach(result => {
              if (result.summaries && result.summaries.original) {
                console.log(`Received summary for ${result.filename} - Length: ${result.summaries.original.length} characters`);
              }
            });

            this.results = response.results.map(result => ({
              ...result,
              originalText: result.originalText || '',
              personalized: isPersonalized
            }));
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

  private loadLanguages(): void {
    this.uploadService.getSupportedLanguages().subscribe({
      next: (response) => {
        this.languages = Object.entries(response.supported_languages).map(([code, name]) => ({
          code,
          name: name as string
        }));
      },
      error: (err) => {
        console.error('Error loading languages:', err);
        this.errorMessage = 'Error loading supported languages';
      }
    });
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

    // For helpful feedback, submit directly
    if (feedbackType === 'helpful') {
      this.processFeedback(result, feedbackType, '');
    } else {
      // For unclear or inaccurate feedback, show the dialog to get more details
      this.currentFeedbackResult = result;
      this.currentFeedbackType = feedbackType;
      this.showFeedbackDialog = true;
    }
  }

  closeFeedbackDialog(): void {
    this.showFeedbackDialog = false;

    // Reset feedback status if dialog was closed without submitting
    if (this.currentFeedbackResult) {
      delete this.feedbackStatus[this.currentFeedbackResult.filename];
    }

    this.currentFeedbackResult = null;
    this.currentFeedbackType = '';
  }

  submitFeedbackWithText(feedbackText: string): void {
    if (!this.currentFeedbackResult || !this.currentFeedbackType) return;

    // Close the dialog
    this.showFeedbackDialog = false;

    // Process the feedback with the text
    this.processFeedback(this.currentFeedbackResult, this.currentFeedbackType, feedbackText);

    // Reset current feedback
    this.currentFeedbackResult = null;
    this.currentFeedbackType = '';
  }

  private processFeedback(result: DocumentResult, feedbackType: string, feedbackText: string): void {
    // Set status to submitting
    this.feedbackStatus[result.filename] = {
      status: 'submitting',
      feedbackType
    };

    // Only send original text and summary for unclear/inaccurate feedback
    const needsRefinement = feedbackType === 'unclear' || feedbackType === 'inaccurate';

    this.uploadService.submitFeedback({
      summary_id: result.filename,
      feedback_type: feedbackType,
      original_text: needsRefinement ? result.originalText : undefined,
      original_summary: needsRefinement ? result.summaries.original : undefined,
      feedback_text: feedbackText || undefined
    }).subscribe({
      next: (response) => {
        // If we got a refined summary, update the result
        if (response.summaries && response.summaries.original && needsRefinement) {
          // Log the refined summary length for debugging
          console.log(`Received refined summary - Length: ${response.summaries.original.length} characters`);

          // Update the summary with the refined version
          result.summaries.original = response.summaries.original;

          this.feedbackStatus[result.filename] = {
            status: 'success',
            message: `Thank you! The summary has been refined based on your feedback.`,
            feedbackType
          };
        } else {
          this.feedbackStatus[result.filename] = {
            status: 'success',
            message: `Thank you! Your "${feedbackType}" feedback has been recorded.`,
            feedbackType
          };
        }

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



  updateInterests(interestCode: string, event: any): void {
    const checked = event.target.checked;
    if (checked) {
      if (!this.selectedInterests.includes(interestCode)) {
        this.selectedInterests.push(interestCode);
      }
    } else {
      this.selectedInterests = this.selectedInterests.filter(i => i !== interestCode);
    }
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

  // Helper method to determine if personalization is being used
  isPersonalizationUsed(): boolean {
    return this.readingLevel !== '' ||
           this.selectedInterests.length > 0 ||
           this.ageGroup !== '';
  }
}
