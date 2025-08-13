#!/usr/bin/env python3
"""
Social Media Downloader - A comprehensive web application for downloading
content from various social media platforms.

Supports: YouTube, Instagram, Facebook, Twitter/X, TikTok, and more.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import tempfile
import shutil
from datetime import datetime
import logging
from urllib.parse import urlparse
import threading
import uuid

# Import our custom downloaders
from downloaders.youtube_downloader import YouTubeDownloader
from downloaders.instagram_downloader import InstagramDownloader
from downloaders.facebook_downloader import FacebookDownloader
from downloaders.twitter_downloader import TwitterDownloader
from downloaders.tiktok_downloader import TikTokDownloader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global download progress tracking
download_progress = {}

class SocialMediaDownloader:
    def __init__(self):
        self.youtube_dl = YouTubeDownloader()
        self.instagram_dl = InstagramDownloader()
        self.facebook_dl = FacebookDownloader()
        self.twitter_dl = TwitterDownloader()
        self.tiktok_dl = TikTokDownloader()
        
    def detect_platform(self, url):
        """Detect social media platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'facebook.com' in domain or 'fb.watch' in domain:
            return 'facebook'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'tiktok.com' in domain:
            return 'tiktok'
        else:
            return 'unknown'
    
    def download_content(self, url, format_type='best', download_id=None):
        """Download content from any supported platform"""
        platform = self.detect_platform(url)
        
        try:
            if platform == 'youtube':
                return self.youtube_dl.download(url, format_type, download_id)
            elif platform == 'instagram':
                return self.instagram_dl.download(url, format_type, download_id)
            elif platform == 'facebook':
                return self.facebook_dl.download(url, format_type, download_id)
            elif platform == 'twitter':
                return self.twitter_dl.download(url, format_type, download_id)
            elif platform == 'tiktok':
                return self.tiktok_dl.download(url, format_type, download_id)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
        except Exception as e:
            logger.error(f"Download failed for {url}: {str(e)}")
            raise

# Initialize downloader
downloader = SocialMediaDownloader()

@app.route('/')
def index():
    """Main page with download interface"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    """API endpoint for downloading content"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        download_progress[download_id] = {
            'status': 'starting',
            'progress': 0,
            'url': url,
            'format': format_type
        }
        
        # Start download in background thread
        def download_task():
            try:
                result = downloader.download_content(url, format_type, download_id)
                download_progress[download_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'result': result
                })
            except Exception as e:
                download_progress[download_id].update({
                    'status': 'error',
                    'error': str(e)
                })
        
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'download_id': download_id,
            'status': 'started'
        })
        
    except Exception as e:
        logger.error(f"Download API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<download_id>')
def api_progress(download_id):
    """Get download progress"""
    if download_id in download_progress:
        return jsonify(download_progress[download_id])
    else:
        return jsonify({'error': 'Download not found'}), 404

@app.route('/api/download_file/<download_id>')
def api_download_file(download_id):
    """Download the actual file"""
    if download_id not in download_progress:
        return jsonify({'error': 'Download not found'}), 404
    
    progress = download_progress[download_id]
    if progress['status'] != 'completed':
        return jsonify({'error': 'Download not completed'}), 400
    
    file_path = progress['result']['file_path']
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/api/info', methods=['POST'])
def api_info():
    """Get video/content information without downloading"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        platform = downloader.detect_platform(url)
        
        if platform == 'youtube':
            info = downloader.youtube_dl.get_info(url)
        elif platform == 'instagram':
            info = downloader.instagram_dl.get_info(url)
        elif platform == 'facebook':
            info = downloader.facebook_dl.get_info(url)
        elif platform == 'twitter':
            info = downloader.twitter_dl.get_info(url)
        elif platform == 'tiktok':
            info = downloader.tiktok_dl.get_info(url)
        else:
            return jsonify({'error': f'Unsupported platform: {platform}'}), 400
        
        return jsonify({
            'platform': platform,
            'info': info
        })
        
    except Exception as e:
        logger.error(f"Info API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create downloads directory
    os.makedirs('downloads', exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)