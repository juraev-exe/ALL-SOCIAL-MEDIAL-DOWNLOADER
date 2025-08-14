"""
Instagram Downloader using instaloader
Supports posts, stories, reels, and IGTV downloads
"""

import instaloader
import os
import tempfile
from datetime import datetime
import logging
import requests
import json

logger = logging.getLogger(__name__)

class InstagramDownloader:
    def __init__(self):
        self.downloads_dir = 'downloads'
        os.makedirs(self.downloads_dir, exist_ok=True)
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
    
    def get_info(self, url):
        """Get Instagram post information"""
        try:
            # Extract shortcode from URL
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                raise ValueError("Invalid Instagram URL")
            
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            return {
                'title': post.caption[:100] + '...' if post.caption else 'Instagram Post',
                'username': post.owner_username,
                'likes': post.likes,
                'comments': post.comments,
                'is_video': post.is_video,
                'date': post.date_utc.isoformat(),
                'url': post.url,
                'media_count': post.mediacount if hasattr(post, 'mediacount') else 1
            }
        except Exception as e:
            logger.error(f"Error getting Instagram info: {str(e)}")
            raise
    
    def _extract_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        import re
        
        # Handle different Instagram URL formats
        patterns = [
            r'instagram\.com/p/([^/?]+)',
            r'instagram\.com/reel/([^/?]+)',
            r'instagram\.com/tv/([^/?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download(self, url, format_type='best', download_id=None):
        """Download Instagram content"""
        try:
            # Update progress
            if download_id:
                from app import download_progress
                download_progress[download_id]['status'] = 'downloading'
                download_progress[download_id]['progress'] = 10
            
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                raise ValueError("Invalid Instagram URL")
            
            # Get post info
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            # Update progress
            if download_id:
                download_progress[download_id]['progress'] = 30
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Set the download directory
                self.loader.dirname_pattern = temp_dir
                
                # Download the post
                self.loader.download_post(post, target=temp_dir)
                
                # Update progress
                if download_id:
                    download_progress[download_id]['progress'] = 80
                
                # Find downloaded files and move them to downloads directory
                downloaded_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov')):
                            src_path = os.path.join(root, file)
                            # Create a meaningful filename
                            ext = os.path.splitext(file)[1]
                            new_filename = f"instagram_{post.owner_username}_{shortcode}_{timestamp}{ext}"
                            dst_path = os.path.join(self.downloads_dir, new_filename)
                            
                            # Copy file to downloads directory
                            import shutil
                            shutil.copy2(src_path, dst_path)
                            downloaded_files.append({
                                'path': dst_path,
                                'filename': new_filename,
                                'size': os.path.getsize(dst_path)
                            })
                
                if not downloaded_files:
                    raise Exception("No media files found in post")
                
                # Update progress
                if download_id:
                    download_progress[download_id]['progress'] = 100
                
                # Return info about the first/main file
                main_file = downloaded_files[0]
                
                return {
                    'success': True,
                    'title': f"Instagram post by @{post.owner_username}",
                    'file_path': main_file['path'],
                    'filename': main_file['filename'],
                    'file_size': main_file['size'],
                    'format': format_type,
                    'all_files': downloaded_files
                }
                
            finally:
                # Clean up temp directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
    
    def download_profile_pic(self, username):
        """Download profile picture"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_profile_{username}_{timestamp}.jpg"
            file_path = os.path.join(self.downloads_dir, filename)
            
            # Download profile picture
            response = requests.get(profile.profile_pic_url)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'title': f"Profile picture of @{username}",
                'file_path': file_path,
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'format': 'image'
            }
            
        except Exception as e:
            logger.error(f"Instagram profile pic download error: {str(e)}")
            raise Exception(f"Profile picture download failed: {str(e)}")