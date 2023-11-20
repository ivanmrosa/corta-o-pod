from datetime import datetime
import json
from pathlib import Path
import shutil
from flask import render_template, request
from flask.views import MethodView
from cuts_handler import CutsHandler
from env import Env


class HomeController(MethodView):

    def __init__(self) -> None:        
        super().__init__() 
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def get(self) -> str:
        
        paths = Path(self.dir).iterdir()
        videos = []
        
        for path in paths:
            meta = CutsHandler.retriveMetadatas(path)
            if len(meta.keys()) > 0:
                videos.append(meta)    
        videos = sorted(videos, 
            key=lambda video: datetime.strptime(video["uploadDate"].split('.')[0], 
                                                '%Y-%m-%d %H:%M:%S'), reverse=True)
                
        return render_template('home.html', videos=videos)
    
    def delete(self)->str:
        data = json.loads(request.data)    
        handler = CutsHandler(dir, data["link"])
        videoDir = handler.getVideoDirectory()
        shutil.rmtree(videoDir)
        return {"message": "Video deleted!"}
