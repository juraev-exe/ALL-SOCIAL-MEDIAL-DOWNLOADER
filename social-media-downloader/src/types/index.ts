export interface DownloadRequest {
    platform: 'facebook' | 'instagram' | 'twitter' | 'youtube';
    url: string;
    options?: Record<string, any>;
}

export interface DownloadResponse {
    success: boolean;
    message: string;
    data?: any;
}