from datetime import datetime
from pathlib import Path
from env import Env
from services.cuts_handler import CutsHandler

class MetadataService:
    def __init__(self) -> None:        
        super().__init__() 
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')
    
    def getVideos(self):
        paths = Path(self.dir).iterdir()
        videos = []
        
        for path in paths:
            meta = CutsHandler.retriveMetadatas(path)
            if len(meta.keys()) > 0:
                videos.append(meta)    

        return sorted(videos, 
            key=lambda video: datetime.strptime(video["uploadDate"].split('.')[0], 
                                                '%Y-%m-%d %H:%M:%S'), reverse=True)
    
    def getCuts(self, link):        
        handler = CutsHandler(self.dir, link)
        return handler.retrievePreparedCuts()
    