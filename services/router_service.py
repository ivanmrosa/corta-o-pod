from flask import Flask
from controllers.add_video_controller import AddVideoController
from controllers.cuts_controller import PreCutsController, VideoCutsController
from controllers.download_controller import DownloadController
from controllers.home_controller import HomeController
from controllers.stream_controller import StreamController
from controllers.video_detail_controller import VideoDetailController

class RouterService:
    def configure_routes(self, app: Flask):
        app.add_url_rule('/', view_func=HomeController.as_view(name='home'))
        app.add_url_rule('/video-detail', view_func=VideoDetailController.as_view(name='video-detail'))
        app.add_url_rule('/add-video', view_func=AddVideoController.as_view(name='add-video'))
        app.add_url_rule('/generate-cuts', view_func=PreCutsController.as_view(name='generate-cuts'))
        app.add_url_rule('/generate-video-cuts', view_func=VideoCutsController.as_view(name='generate-video-cuts'))
        app.add_url_rule('/download', view_func=DownloadController.as_view(name='download'))
        app.add_url_rule('/stream-video', view_func=StreamController.as_view(name='stream'))
        
       