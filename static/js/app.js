// Social Media Downloader JavaScript

class SocialMediaDownloader {
    constructor() {
        this.currentDownloadId = null;
        this.progressInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const downloadForm = document.getElementById('downloadForm');
        const getInfoBtn = document.getElementById('getInfoBtn');
        const urlInput = document.getElementById('urlInput');

        downloadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startDownload();
        });

        getInfoBtn.addEventListener('click', () => {
            this.getContentInfo();
        });

        // Auto-detect platform when URL is entered
        urlInput.addEventListener('input', () => {
            this.detectPlatform();
        });
    }

    detectPlatform() {
        const url = document.getElementById('urlInput').value.trim();
        if (!url) return;

        const platforms = document.querySelectorAll('.platform-icon');
        platforms.forEach(platform => platform.classList.remove('active'));

        if (url.includes('youtube.com') || url.includes('youtu.be')) {
            this.highlightPlatform('youtube');
        } else if (url.includes('instagram.com')) {
            this.highlightPlatform('instagram');
        } else if (url.includes('facebook.com') || url.includes('fb.watch')) {
            this.highlightPlatform('facebook');
        } else if (url.includes('twitter.com') || url.includes('x.com')) {
            this.highlightPlatform('twitter');
        } else if (url.includes('tiktok.com')) {
            this.highlightPlatform('tiktok');
        }
    }

    highlightPlatform(platformName) {
        const platform = document.querySelector(`.platform-icon.${platformName}`);
        if (platform) {
            platform.style.transform = 'scale(1.1)';
            platform.style.boxShadow = '0 5px 20px rgba(0,0,0,0.3)';
            setTimeout(() => {
                platform.style.transform = '';
                platform.style.boxShadow = '';
            }, 2000);
        }
    }

    async getContentInfo() {
        const url = document.getElementById('urlInput').value.trim();
        if (!url) {
            this.showAlert('Please enter a valid URL', 'warning');
            return;
        }

        const getInfoBtn = document.getElementById('getInfoBtn');
        const originalText = getInfoBtn.innerHTML;
        getInfoBtn.innerHTML = '<div class="loading"></div> Getting Info...';
        getInfoBtn.disabled = true;

        try {
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok) {
                this.displayContentInfo(data);
            } else {
                this.showAlert(data.error || 'Failed to get content information', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error occurred', 'danger');
        } finally {
            getInfoBtn.innerHTML = originalText;
            getInfoBtn.disabled = false;
        }
    }

    displayContentInfo(data) {
        const contentInfo = document.getElementById('contentInfo');
        const contentInfoBody = document.getElementById('contentInfoBody');

        let infoHtml = `
            <div class="row">
                <div class="col-md-8">
                    <div class="content-info-item">
                        <span class="content-info-label">Platform:</span>
                        <span class="content-info-value">
                            <i class="fab fa-${data.platform}"></i> ${data.platform.charAt(0).toUpperCase() + data.platform.slice(1)}
                        </span>
                    </div>
                    <div class="content-info-item">
                        <span class="content-info-label">Title:</span>
                        <span class="content-info-value">${data.info.title}</span>
                    </div>
                    <div class="content-info-item">
                        <span class="content-info-label">Author:</span>
                        <span class="content-info-value">${data.info.uploader || data.info.username || 'Unknown'}</span>
                    </div>
        `;

        if (data.info.duration) {
            infoHtml += `
                <div class="content-info-item">
                    <span class="content-info-label">Duration:</span>
                    <span class="content-info-value">${this.formatDuration(data.info.duration)}</span>
                </div>
            `;
        }

        if (data.info.view_count) {
            infoHtml += `
                <div class="content-info-item">
                    <span class="content-info-label">Views:</span>
                    <span class="content-info-value">${this.formatNumber(data.info.view_count)}</span>
                </div>
            `;
        }

        if (data.info.likes || data.info.like_count) {
            infoHtml += `
                <div class="content-info-item">
                    <span class="content-info-label">Likes:</span>
                    <span class="content-info-value">${this.formatNumber(data.info.likes || data.info.like_count)}</span>
                </div>
            `;
        }

        infoHtml += '</div>';

        if (data.info.thumbnail) {
            infoHtml += `
                <div class="col-md-4 text-center">
                    <img src="${data.info.thumbnail}" alt="Thumbnail" class="thumbnail-preview">
                </div>
            `;
        }

        infoHtml += '</div>';

        if (data.info.description) {
            infoHtml += `
                <div class="mt-3">
                    <strong>Description:</strong>
                    <p class="mt-2 text-muted">${data.info.description}</p>
                </div>
            `;
        }

        contentInfoBody.innerHTML = infoHtml;
        contentInfo.style.display = 'block';
        contentInfo.classList.add('fade-in');
    }

    async startDownload() {
        const url = document.getElementById('urlInput').value.trim();
        const format = document.getElementById('formatSelect').value;

        if (!url) {
            this.showAlert('Please enter a valid URL', 'warning');
            return;
        }

        const downloadBtn = document.getElementById('downloadBtn');
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<div class="loading"></div> Starting...';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    format: format 
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentDownloadId = data.download_id;
                this.showDownloadProgress();
                this.startProgressTracking();
            } else {
                this.showAlert(data.error || 'Failed to start download', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error occurred', 'danger');
        } finally {
            downloadBtn.innerHTML = originalText;
            downloadBtn.disabled = false;
        }
    }

    showDownloadProgress() {
        const progressCard = document.getElementById('downloadProgress');
        progressCard.style.display = 'block';
        progressCard.classList.add('fade-in');
        
        // Scroll to progress card
        progressCard.scrollIntoView({ behavior: 'smooth' });
    }

    startProgressTracking() {
        this.progressInterval = setInterval(() => {
            this.checkProgress();
        }, 1000);
    }

    async checkProgress() {
        if (!this.currentDownloadId) return;

        try {
            const response = await fetch(`/api/progress/${this.currentDownloadId}`);
            const data = await response.json();

            if (response.ok) {
                this.updateProgress(data);
                
                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(this.progressInterval);
                    this.progressInterval = null;
                }
            }
        } catch (error) {
            console.error('Progress check error:', error);
        }
    }

    updateProgress(data) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const downloadResult = document.getElementById('downloadResult');

        progressBar.style.width = `${data.progress || 0}%`;
        progressBar.setAttribute('aria-valuenow', data.progress || 0);

        if (data.status === 'starting') {
            progressText.textContent = 'Initializing download...';
        } else if (data.status === 'downloading') {
            progressText.textContent = `Downloading... ${Math.round(data.progress || 0)}%`;
        } else if (data.status === 'processing') {
            progressText.textContent = 'Processing file...';
        } else if (data.status === 'completed') {
            progressText.textContent = 'Download completed!';
            this.showDownloadResult(data.result);
        } else if (data.status === 'error') {
            progressText.textContent = 'Download failed!';
            this.showDownloadError(data.error);
        }
    }

    showDownloadResult(result) {
        const downloadResult = document.getElementById('downloadResult');
        
        const fileSize = this.formatFileSize(result.file_size);
        
        downloadResult.innerHTML = `
            <div class="download-success">
                <i class="fas fa-check-circle fa-2x mb-3"></i>
                <h5>Download Successful!</h5>
                <div class="file-info">
                    <strong>Title:</strong> ${result.title}<br>
                    <strong>File:</strong> ${result.filename}<br>
                    <strong>Size:</strong> ${fileSize}<br>
                    <strong>Format:</strong> ${result.format}
                </div>
                <a href="/api/download_file/${this.currentDownloadId}" 
                   class="btn btn-light btn-lg mt-3" download>
                    <i class="fas fa-download"></i> Download File
                </a>
            </div>
        `;
        
        downloadResult.style.display = 'block';
        downloadResult.classList.add('fade-in');
    }

    showDownloadError(error) {
        const downloadResult = document.getElementById('downloadResult');
        
        downloadResult.innerHTML = `
            <div class="download-error">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <h5>Download Failed</h5>
                <p>${error}</p>
                <button class="btn btn-light mt-3" onclick="location.reload()">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
        
        downloadResult.style.display = 'block';
        downloadResult.classList.add('fade-in');
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.col-lg-8');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SocialMediaDownloader();
});