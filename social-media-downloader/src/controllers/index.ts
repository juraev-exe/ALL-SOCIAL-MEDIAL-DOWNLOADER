import { Request, Response } from 'express';
import FacebookDownloader from '../services/facebookDownloader';
import InstagramDownloader from '../services/instagramDownloader';
import TwitterDownloader from '../services/twitterDownloader';
import YoutubeDownloader from '../services/youtubeDownloader';

class IndexController {
    private facebookDownloader: FacebookDownloader;
    private instagramDownloader: InstagramDownloader;
    private twitterDownloader: TwitterDownloader;
    private youtubeDownloader: YoutubeDownloader;

    constructor() {
        this.facebookDownloader = new FacebookDownloader();
        this.instagramDownloader = new InstagramDownloader();
        this.twitterDownloader = new TwitterDownloader();
        this.youtubeDownloader = new YoutubeDownloader();
    }

    public async handleDownload(req: Request, res: Response): Promise<void> {
        const { platform, type, url } = req.body;

        try {
            let result;

            switch (platform) {
                case 'facebook':
                    if (type === 'video') {
                        result = await this.facebookDownloader.downloadVideo(url);
                    } else if (type === 'image') {
                        result = await this.facebookDownloader.downloadImage(url);
                    }
                    break;
                case 'instagram':
                    if (type === 'post') {
                        result = await this.instagramDownloader.downloadPost(url);
                    } else if (type === 'story') {
                        result = await this.instagramDownloader.downloadStory(url);
                    }
                    break;
                case 'twitter':
                    if (type === 'tweet') {
                        result = await this.twitterDownloader.downloadTweet(url);
                    } else if (type === 'media') {
                        result = await this.twitterDownloader.downloadMedia(url);
                    }
                    break;
                case 'youtube':
                    if (type === 'video') {
                        result = await this.youtubeDownloader.downloadVideo(url);
                    } else if (type === 'playlist') {
                        result = await this.youtubeDownloader.downloadPlaylist(url);
                    }
                    break;
                default:
                    res.status(400).json({ error: 'Unsupported platform or type' });
                    return;
            }

            res.status(200).json({ data: result });
        } catch (error) {
            res.status(500).json({ error: 'An error occurred while processing the request' });
        }
    }
}

export default IndexController;