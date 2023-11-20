import datetime
import json
from pathlib import Path
import shutil
from flask import Response, render_template, request
from flask.views import MethodView
from services.cuts_handler import CutsHandler
from env import Env


class DownloadController(MethodView):

    def __init__(self) -> None:
        super().__init__()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def get(self) -> str:
        return render_template('download-video.html')
                
    
    def post(self) -> Response:
        data = json.loads(request.data)      
        handler = CutsHandler(self.dir, data["link"])
        
        alreadySavedMeta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
        if len(alreadySavedMeta.keys()) > 0:
            return alreadySavedMeta

        handler.downloadVideo()    
        handler.savePreparedCuts([])    
        meta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
        return Response(json.dumps(meta), content_type="application/json")


