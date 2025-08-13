"""
Twitter/X Downloader using yt-dlp
Supports video and image downloads from Twitter/X posts
"""

import yt_dlp
import os
import tempfile
from datetime import datetime
import logging
import requests
import re

logger = logging.getLogger(__name__)

class TwitterDownloader:
    def __init__(self):
        self.downloads_dir = 'downloads'
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_info(self, url):
        """Get Twitter post information"""
        try:
            # Try to use yt-dlp to get info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Twitter Post'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:280] + '...' if info.get('description', '') else ''
                }
        except Exception as e:
            logger.error(f"Error getting Twitter info: {str(e)}")
            # Return basic info if extraction fails
            return {
                'title': 'Twitter Post',
                'uploader': 'Unknown',
                'duration': 0,
                'view_count': 0,
                'thumbnail': '',
                'description': 'Twitter content'
            }
    
    def download(self, url, format_type='best', download_id=None):
        """Download Twitter content"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 10
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': f'{self.downloads_dir}/twitter_%(title)s_{timestamp}.%(ext)s',
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
                title = info.get('title', 'Twitter Content')
                
                # Download
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.downloads_dir):
                    if timestamp in file and 'twitter' in file:
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
            logger.error(f"Twitter download error: {str(e)}")
            # If yt-dlp fails, try alternative method for images
            if 'image' in format_type.lower():
                return self._download_twitter_images(url, download_id)
            else:
                raise Exception(f"Download failed: {str(e)}")
    
    def _download_twitter_images(self, url, download_id=None):
        """Alternative method to download Twitter images"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 20
            
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id(url)
            if not tweet_id:
                raise Exception("Could not extract tweet ID from URL")
            
            # Try to get tweet content (this is a simplified approach)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 40
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Simple regex to find image URLs
            img_pattern = r'https://pbs\.twimg\.com/media/[^"]*\.(?:jpg|jpeg|png|gif)'
            img_urls = re.findall(img_pattern, response.text)
            
            if not img_urls:
                raise Exception("No images found in Twitter post")
            
            # Download the first image found
            img_url = img_urls[0]
            # Remove any URL parameters and get high quality version
            img_url = img_url.split('?')[0] + '?format=jpg&name=large'
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 70
            
            img_response = requests.get(img_url, headers=headers)
            img_response.raise_for_status()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_image_{tweet_id}_{timestamp}.jpg"
            file_path = os.path.join(self.downloads_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 100
            
            return {
                'success': True,
                'title': f'Twitter Image from Tweet {tweet_id}',
                'file_path': file_path,
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'format': 'image'
            }
            
        except Exception as e:
            logger.error(f"Twitter image download error: {str(e)}")
            raise Exception(f"Image download failed: {str(e)}")
    
    def _extract_tweet_id(self, url):
        """Extract tweet ID from Twitter URL"""
        patterns = [
            r'twitter\.com/[^/]+/status/(\d+)',
            r'x\.com/[^/]+/status/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None