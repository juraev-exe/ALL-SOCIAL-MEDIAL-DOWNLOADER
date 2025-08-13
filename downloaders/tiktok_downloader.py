"""
TikTok Downloader using yt-dlp
Supports video downloads from TikTok
"""

import yt_dlp
import os
import tempfile
from datetime import datetime
import logging
import requests
import re

logger = logging.getLogger(__name__)

class TikTokDownloader:
    def __init__(self):
        self.downloads_dir = 'downloads'
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_info(self, url):
        """Get TikTok video information"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:200] + '...' if info.get('description', '') else ''
                }
        except Exception as e:
            logger.error(f"Error getting TikTok info: {str(e)}")
            # Return basic info if extraction fails
            return {
                'title': 'TikTok Video',
                'uploader': 'Unknown',
                'duration': 0,
                'view_count': 0,
                'like_count': 0,
                'thumbnail': '',
                'description': 'TikTok content'
            }
    
    def download(self, url, format_type='best', download_id=None):
        """Download TikTok video"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 10
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': f'{self.downloads_dir}/tiktok_%(title)s_{timestamp}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
            
            # Set format based on type
            if format_type == 'video_mp4':
                ydl_opts['format'] = 'best[ext=mp4]/best'
            elif format_type == 'audio':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:  # best
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
                title = info.get('title', 'TikTok Video')
                
                # Download
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.downloads_dir):
                    if timestamp in file and 'tiktok' in file:
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
            logger.error(f"TikTok download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
    
    def download_without_watermark(self, url, download_id=None):
        """Attempt to download TikTok video without watermark"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 10
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Configure yt-dlp with specific options for watermark removal
            ydl_opts = {
                'outtmpl': f'{self.downloads_dir}/tiktok_nowm_%(title)s_{timestamp}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'format': 'best[ext=mp4]/best',
                # Try to get version without watermark
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            }
            
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
                title = info.get('title', 'TikTok Video')
                
                # Download
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.downloads_dir):
                    if timestamp in file and 'tiktok_nowm' in file:
                        file_path = os.path.join(self.downloads_dir, file)
                        file_size = os.path.getsize(file_path)
                        
                        # Update progress
                        if download_id:
                            download_progress[download_id]['progress'] = 100
                        
                        return {
                            'success': True,
                            'title': title + ' (No Watermark)',
                            'file_path': file_path,
                            'filename': file,
                            'file_size': file_size,
                            'format': 'video_no_watermark'
                        }
                
                raise Exception("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"TikTok no-watermark download error: {str(e)}")
            # Fallback to regular download
            return self.download(url, 'best', download_id)