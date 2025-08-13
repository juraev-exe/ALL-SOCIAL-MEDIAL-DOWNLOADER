"""
Facebook Downloader using yt-dlp and facebook-scraper
Supports video and image downloads from Facebook posts
"""

import yt_dlp
import os
import tempfile
from datetime import datetime
import logging
import requests
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class FacebookDownloader:
    def __init__(self):
        self.downloads_dir = 'downloads'
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_info(self, url):
        """Get Facebook post information"""
        try:
            # Try to use yt-dlp to get info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Facebook Post'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:300] + '...' if info.get('description', '') else ''
                }
        except Exception as e:
            logger.error(f"Error getting Facebook info: {str(e)}")
            # Return basic info if extraction fails
            return {
                'title': 'Facebook Content',
                'uploader': 'Unknown',
                'duration': 0,
                'view_count': 0,
                'thumbnail': '',
                'description': 'Facebook content'
            }
    
    def download(self, url, format_type='best', download_id=None):
        """Download Facebook content"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 10
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': f'{self.downloads_dir}/facebook_%(title)s_{timestamp}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
            
            # Set format based on type
            if format_type == 'video':
                ydl_opts['format'] = 'best[ext=mp4]/best'
            elif format_type == 'audio':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['format'] = 'best'
            
            # Add progress hook
            if download_id:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            download_progress[download_id]['progress'] = min(progress, 90)
                    elif d['status'] == 'finished':
                        download_progress[download_id]['progress'] = 90
                        download_progress[download_id]['status'] = 'processing'
                
                ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Facebook Content')
                
                # Download
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.downloads_dir):
                    if timestamp in file and 'facebook' in file:
                        file_path = os.path.join(self.downloads_dir, file)
                        file_size = os.path.getsize(file_path)
                        
                        # Update progress
                        if download_id:
                            download_progress[download_id]['progress'] = 100
                        
                        return {
                            'success': True,
                            'title': title,
                            'file_path': file_path,
                            'filename': file,
                            'file_size': file_size,
                            'format': format_type
                        }
                
                raise Exception("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"Facebook download error: {str(e)}")
            # If yt-dlp fails, try alternative method for images
            if 'image' in format_type.lower() or 'photo' in url.lower():
                return self._download_facebook_image(url, download_id)
            else:
                raise Exception(f"Download failed: {str(e)}")
    
    def _download_facebook_image(self, url, download_id=None):
        """Alternative method to download Facebook images"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 20
            
            # Try to extract image URL from Facebook post
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 50
            
            # Simple regex to find image URLs (this is a basic implementation)
            import re
            img_pattern = r'https://[^"]*\.(?:jpg|jpeg|png|gif)'
            img_urls = re.findall(img_pattern, response.text)
            
            if not img_urls:
                raise Exception("No images found in Facebook post")
            
            # Download the first image found
            img_url = img_urls[0]
            img_response = requests.get(img_url, headers=headers)
            img_response.raise_for_status()
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 80
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facebook_image_{timestamp}.jpg"
            file_path = os.path.join(self.downloads_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 100
            
            return {
                'success': True,
                'title': 'Facebook Image',
                'file_path': file_path,
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'format': 'image'
            }
            
        except Exception as e:
            logger.error(f"Facebook image download error: {str(e)}")
            raise Exception(f"Image download failed: {str(e)}")