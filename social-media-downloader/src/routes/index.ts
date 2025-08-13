import { Router } from 'express';
import IndexController from '../controllers/index';

const router = Router();
const indexController = new IndexController();

export function setRoutes(app) {
    app.use('/download', router);
    router.post('/facebook', indexController.handleDownload.bind(indexController));
    router.post('/instagram', indexController.handleDownload.bind(indexController));
    router.post('/twitter', indexController.handleDownload.bind(indexController));
    router.post('/youtube', indexController.handleDownload.bind(indexController));
}