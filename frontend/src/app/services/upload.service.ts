import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpResponse, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError, retry, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DocumentSummary {
  fileName: string;
  summaries: {
    original: string;
    [key: string]: string;  // For translated summaries with language code as key
  };
}

export interface UploadOptions {
  targetLanguage?: string;
  customPrompt?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = environment.apiUrl;
  private baseUrl = `${this.apiUrl}/upload`;

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
    } else {
      errorMessage = `Server error: ${error.status}. ${error.message}`;
    }
    
    console.error('Upload error:', error);
    return throwError(() => errorMessage);
  }

  uploadDocument(file: File, options: UploadOptions): Observable<{ progress: number; summary?: DocumentSummary }> {
    const formData = new FormData();
    formData.append('files', file);
    
    if (options.customPrompt) {
      formData.append('custom_prompt', options.customPrompt);
    }
    
    let params = new HttpParams();
    if (options.targetLanguage) {
      params = params.set('target_language', options.targetLanguage);
    }
    
    // Log request details
    console.log('Request Details:', {
      url: `${this.baseUrl}${params.toString() ? '?' + params.toString() : ''}`,
      params: params.toString(),
      body: {
        file: {
          name: file.name,
          type: file.type,
          size: file.size
        },
        options
      }
    });

    return this.http.post(this.baseUrl, formData, {
      params,
      reportProgress: true,
      observe: 'events'
    }).pipe(
      tap(event => {
        if (event.type === HttpEventType.Response) {
          console.log('Response received:', {
            status: event.status,
            statusText: event.statusText,
            headers: event.headers,
            body: event.body
          });
        }
      }),
      retry(1),
      map((event: HttpEvent<any>) => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            if (event.total) {
              return { progress: Math.round(100 * (event.loaded / event.total)) };
            }
            return { progress: 0 };
          case HttpEventType.Response:
            if (event instanceof HttpResponse) {
              const responseData = event.body;
              if (responseData.successful_files && responseData.successful_files.length > 0) {
                const fileResult = responseData.successful_files[0];
                return {
                  progress: 100,
                  summary: {
                    fileName: fileResult.filename,
                    summaries: fileResult.summaries
                  }
                };
              }
              // Handle failed uploads
              if (responseData.failed_files && responseData.failed_files.length > 0) {
                throw new Error(responseData.failed_files[0].error);
              }
            }
            return { progress: 100 };
          default:
            return { progress: 0 };
        }
      }),
      catchError(this.handleError)
    );
  }

  uploadFiles(formData: FormData, onProgress: (progress: number) => void) {
    return new Promise((resolve, reject) => {
      this.http.post(`${this.apiUrl}/upload`, formData, {
        reportProgress: true,
        observe: 'events'
      }).subscribe({
        next: (event: any) => {
          if (event.type === HttpEventType.UploadProgress) {
            const progress = Math.round((100 * event.loaded) / event.total);
            onProgress(progress);
          } else if (event.type === HttpEventType.Response) {
            resolve(event.body);
          }
        },
        error: (error) => reject(error)
      });
    });
  }

  uploadMultipleFiles(files: File[], targetLanguage?: string) {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });

    if (targetLanguage) {
      formData.append('target_language', targetLanguage);
    }

    return this.http.post(`${this.apiUrl}/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    });
  }
}