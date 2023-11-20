import json
from flask import Response, request
from flask.views import MethodView
from services.cuts_handler import CutsHandler
from env import Env


class PreCutsController(MethodView):
    def __init__(self) -> None:
        super().__init__()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def post(self) -> Response:
        data = json.loads(request.data)    
        handler = CutsHandler(self.dir, data["link"])
        
        alreadySavedMeta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
        if len(alreadySavedMeta.keys()) > 0:
            return alreadySavedMeta
            
        handler.prepareCuts()    
        meta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
        return Response(json.dumps(meta), content_type="application/json")


class VideoCutsController(MethodView):

    def __init__(self) -> None:
        super().__init__()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def post(self) -> Response:
        data = json.loads(request.data)    
        selectedIds = [ int(id) for id in data["ids"]]
        #speedUps = [ float(id) for id in data["speedUps"]]
        handler = CutsHandler(self.dir, data["videoLink"])  
        
        handler.generateCutsFromVideo(selectedIds=selectedIds, speedUps=data["speedUps"])
        return Response(json.dumps({"message": "Video clips generated successfully!"}), content_type="application/json")
