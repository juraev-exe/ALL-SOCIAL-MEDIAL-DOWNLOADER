# 🚀 Social Media Downloader - All Platforms

A comprehensive Python web application for downloading content from all major social media platforms. Built with Flask and modern web technologies, this tool supports downloading videos, images, and audio from YouTube, Instagram, Facebook, Twitter/X, TikTok, and more.

## ✨ Features

- **🌐 Multi-Platform Support**: Download from YouTube, Instagram, Facebook, Twitter/X, TikTok, and more
- **📱 Multiple Formats**: Support for MP4, MP3, JPG, PNG, and various other formats
- **⚡ Real-time Progress**: Live download progress tracking with beautiful UI
- **📊 Content Information**: Get detailed information about content before downloading
- **🎨 Modern Interface**: Beautiful, responsive web interface that works on all devices
- **🔒 Privacy Focused**: No registration required, no data collection
- **⚙️ Easy Setup**: Simple installation and configuration process

## 🛠️ Supported Platforms

| Platform | Videos | Images | Audio | Stories/Reels |
|----------|--------|--------|-------|---------------|
| YouTube | ✅ | ✅ | ✅ | ❌ |
| Instagram | ✅ | ✅ | ✅ | ✅ |
| Facebook | ✅ | ✅ | ✅ | ❌ |
| Twitter/X | ✅ | ✅ | ✅ | ❌ |
| TikTok | ✅ | ❌ | ✅ | ❌ |

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (for video/audio processing)
- Modern web browser

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER.git
cd ALL-SOCIAL-MEDIAL-DOWNLOADER
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows:**
- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## 🎯 Usage

1. **Paste URL**: Copy and paste the social media URL into the input field
2. **Select Format**: Choose your preferred download format (Video, Audio, Image, etc.)
3. **Get Info** (Optional): Click "Get Info" to see content details before downloading
4. **Download**: Click "Download" to start the process
5. **Wait**: Monitor the real-time progress
6. **Save**: Download the file when complete

### Supported URL Formats

- **YouTube**: `https://youtube.com/watch?v=...` or `https://youtu.be/...`
- **Instagram**: `https://instagram.com/p/...` or `https://instagram.com/reel/...`
- **Facebook**: `https://facebook.com/...` or `https://fb.watch/...`
- **Twitter/X**: `https://twitter.com/.../status/...` or `https://x.com/.../status/...`
- **TikTok**: `https://tiktok.com/...`

## 🏗️ Project Structure

```
ALL-SOCIAL-MEDIAL-DOWNLOADER/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── downloaders/          # Platform-specific downloaders
│   ├── youtube_downloader.py
│   ├── instagram_downloader.py
│   ├── facebook_downloader.py
│   ├── twitter_downloader.py
│   └── tiktok_downloader.py
│
├── templates/            # HTML templates
│   ├── index.html
│   ├── 404.html
│   └── 500.html
│
├── static/              # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── downloads/           # Downloaded files (created automatically)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application settings
SECRET_KEY=your-secret-key-here
DEBUG=False
PORT=5000

# Download settings
DOWNLOAD_PATH=./downloads
MAX_FILE_SIZE=500MB
CONCURRENT_DOWNLOADS=5
```

### Advanced Configuration

You can modify the downloader settings in each platform's downloader file:

- **Quality Settings**: Adjust video/audio quality preferences
- **File Naming**: Customize downloaded file naming patterns
- **Timeout Settings**: Configure download timeout values
- **Format Preferences**: Set default format preferences

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t social-media-downloader .

# Run the container
docker run -p 5000:5000 -v $(pwd)/downloads:/app/downloads social-media-downloader
```

### Docker Compose

```yaml
version: '3.8'
services:
  downloader:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛡️ Security Considerations

- **Rate Limiting**: Implement rate limiting for production use
- **HTTPS**: Always use HTTPS in production
- **File Validation**: Downloaded files are automatically validated
- **Sandbox**: Consider running in a sandboxed environment
- **Resource Limits**: Set appropriate resource limits

## 🐛 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Install FFmpeg and ensure it's in your PATH
   - On Windows, restart your command prompt after installation

2. **"Download failed"**
   - Check if the URL is valid and accessible
   - Some content may be private or geo-restricted
   - Try a different format

3. **"Module not found"**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Permission errors**
   - Check write permissions in the downloads directory
   - Run with appropriate user permissions

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export DEBUG=True
python app.py
```

## 📄 API Documentation

### REST API Endpoints

- `POST /api/download` - Start a download
- `GET /api/progress/<download_id>` - Check download progress
- `GET /api/download_file/<download_id>` - Download the file
- `POST /api/info` - Get content information

### Example API Usage

```javascript
// Start download
const response = await fetch('/api/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        url: 'https://youtube.com/watch?v=example',
        format: 'best'
    })
});

const { download_id } = await response.json();

// Check progress
const progress = await fetch(`/api/progress/${download_id}`);
const { status, progress: percent } = await progress.json();
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER.git
cd ALL-SOCIAL-MEDIAL-DOWNLOADER

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export DEBUG=True
python app.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with:

- Platform Terms of Service
- Copyright laws
- Local regulations
- Content creator rights

Please respect content creators and platform policies. Do not use this tool for commercial purposes or copyright infringement.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube and video platform downloading
- [instaloader](https://github.com/instaloader/instaloader) - Instagram content downloading
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Font Awesome](https://fontawesome.com/) - Icons

## 🔗 Links

- **Repository**: [https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER](https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER)
- **Issues**: [Report bugs or request features](https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER/issues)
- **Documentation**: [Wiki](https://github.com/juraev-exe/ALL-SOCIAL-MEDIAL-DOWNLOADER/wiki)

---

⭐ **Star this repository if you find it useful!**