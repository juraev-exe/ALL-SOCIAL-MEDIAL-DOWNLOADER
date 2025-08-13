"""
YouTube Downloader using yt-dlp
Supports video and audio downloads in various formats
"""

import yt_dlp
import os
import tempfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self):
        self.downloads_dir = 'downloads'
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_info(self, url):
        """Get video information without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:500] + '...' if info.get('description', '') else '',
                    'formats': self._get_available_formats(info)
                }
            except Exception as e:
                logger.error(f"Error getting YouTube info: {str(e)}")
                raise
    
    def _get_available_formats(self, info):
        """Extract available formats from video info"""
        formats = []
        
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'quality': fmt.get('format_note', ''),
                        'filesize': fmt.get('filesize'),
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec')
                    })
        
        return formats
    
    def download(self, url, format_type='best', download_id=None):
        """Download YouTube video/audio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configure yt-dlp options based on format
        if format_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.downloads_dir}/%(title)s_{timestamp}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        elif format_type == 'video_mp4':
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': f'{self.downloads_dir}/%(title)s_{timestamp}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
        else:  # best quality
            ydl_opts = {
                'format': 'best',
                'outtmpl': f'{self.downloads_dir}/%(title)s_{timestamp}.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
        
        # Add progress hook if download_id provided
        if download_id:
            def progress_hook(d):
                from app import download_progress
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        download_progress[download_id]['progress'] = progress
                        download_progress[download_id]['status'] = 'downloading'
                elif d['status'] == 'finished':
                    download_progress[download_id]['progress'] = 100
                    download_progress[download_id]['status'] = 'processing'
            
            ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get info first to get the title
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.downloads_dir):
                    if timestamp in file and (title[:20] in file or file.startswith(title[:20])):
                        file_path = os.path.join(self.downloads_dir, file)
                        file_size = os.path.getsize(file_path)
                        
                        return {
                            'success': True,
                            'title': title,
                            'file_path': file_path,
                            'filename': file,
                            'file_size': file_size,
                            'format': format_type
                        }
                
                # If we can't find the file, return the latest file in downloads
                files = [f for f in os.listdir(self.downloads_dir) if timestamp in f]
                if files:
                    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.downloads_dir, x)))
                    file_path = os.path.join(self.downloads_dir, latest_file)
                    file_size = os.path.getsize(file_path)
                    
                    return {
                        'success': True,
                        'title': title,
                        'file_path': file_path,
                        'filename': latest_file,
                        'file_size': file_size,
                        'format': format_type
                    }
                
                raise Exception("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")