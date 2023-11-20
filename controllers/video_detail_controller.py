import functools
import json
from flask import render_template, request
from flask.views import MethodView
from services.cuts_handler import CutsHandler
from env import Env


class VideoDetailController(MethodView):
    
    def __init__(self) -> None:
        super().__init__()
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def get(self) -> str:
        link = request.args['link']
        handler = CutsHandler(self.dir, link)
        metaData = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
        cuts = handler.retrievePreparedCuts()    
        return render_template('video-detail.html', cuts=cuts, link=link, videoTitle=metaData["title"])
    
    def put(self) -> str:
        data = json.loads(request.data)    
        handler = CutsHandler(self.dir, data["link"])    
        id = int(data["cut"]["id"]) if data["cut"]["id"] else None
        cuts = handler.retrievePreparedCuts()    
        saved = False
        if id:
            for index, c in enumerate(cuts):
                if c["id"] == id:
                    cuts[index] = data["cut"]
                    cuts[index]["id"] = id
                    saved = True
                    break
        else:
            if not cuts:
                cuts = []
                id = 0
            else:
                row = functools.reduce(lambda a, b: a if a["id"] > b["id"] else b, cuts)
                id  = row["id"] + 1 if row else 0

            cut = data["cut"]
            cut["id"] = id
            cuts.append(cut)
            saved = True

        handler.savePreparedCuts(cuts=cuts)
        return {"message": "Cut saved!" if saved else "Cut was not found."}
