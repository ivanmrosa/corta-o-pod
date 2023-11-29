import json
from flask import render_template, request
from flask.views import MethodView
from services.metadata_service import MetadataService
from services.cuts_handler import CutsHandler
from env import Env


class VideoEditingController(MethodView):
    
    def __init__(self) -> None:
        super().__init__()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')        

    def get(self) -> str:
        return render_template('video-editing.html')


class VideoEditingRestController(MethodView):
    def __init__(self) -> None:
        super().__init__()
        self.metadataService = MetadataService()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')
    
    def getYoutubeVideos(self):        
        return json.dumps(self.metadataService.getVideos())

    def getYoutubeCuts(self):
        return json.dumps(self.metadataService.getCuts(request.args["link"]))

    def get(self) -> str:
        method = request.args['method']
        return self.__getattribute__(method)()
    