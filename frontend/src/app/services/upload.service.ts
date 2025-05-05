import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DocumentSummary {
  fileName: string;
  summaries: {
    original: string;
    [key: string]: string;
  };
}

export interface UploadOptions {
  targetLanguage?: string;
  customPrompt?: string;
}

interface UploadResponse {
  results: Array<{
    filename: string;
    summaries: {
      original: string;
      [key: string]: string;
    };
    error?: string;
  }>;
  metadata: {
    processing_timestamp: string;
    total_files_processed: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred during the upload.';
    
    if (error.status === 0) {
      errorMessage = 'Unable to connect to the server. Please check if the server is running and accessible.';
    } else if (error.status === 422) {
      errorMessage = 'Invalid file or parameters provided.';
    } else if (error.status === 400) {
      errorMessage = error.error?.detail || 'Bad request. Please check your input.';
    } else if (error.error instanceof ErrorEvent) {
      errorMessage = `Client-side error: ${error.error.message}`;
    } else if (error.error?.error) {
      // Handle structured error responses from the backend
      errorMessage = error.error.error;
    } else {
      errorMessage = `Server error: ${error.status}. ${error.error?.message || error.message}`;
    }
    
    console.error('Upload error:', error);
    return throwError(() => errorMessage);
  }

  uploadFiles(formData: FormData): Observable<UploadResponse> {
    return this.http.post<UploadResponse>(`${this.apiUrl}/upload`, formData)
      .pipe(
        catchError(this.handleError)
      );
  }

  getSupportedLanguages(): Observable<any> {
    return this.http.get(`${this.apiUrl}/languages`);
  }

  submitFeedback(feedback: { summary_id: string; feedback_type: string }): Observable<any> {
    const formData = new FormData();
    formData.append('summary_id', feedback.summary_id);
    formData.append('feedback_type', feedback.feedback_type);
    return this.http.post(`${this.apiUrl}/feedback`, formData);
  }
}