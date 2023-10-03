import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template, Response
from env import Env
from cuts_handler import CutsHandler

dir = Env().getEnvValue('VIDEOS_DIRECTORY') #os.path.join(os.path.dirname(__file__), 'videos')
app = Flask(__name__)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)


@app.route('/')
def home():    
    paths = Path(dir).iterdir()
    videos = []
    
    for path in paths:
        meta = CutsHandler.retriveMetadatas(path)
        if len(meta.keys()) > 0:
            videos.append(meta)    
    videos = sorted(videos, 
        key=lambda video: datetime.strptime(video["uploadDate"].split('.')[0], 
                                            '%Y-%m-%d %H:%M:%S'), reverse=True)
    
    
    return render_template('home.html', videos=videos)


@app.route('/video-detail')
def videoDetail():
    link = request.args['link']
    handler = CutsHandler(dir, link)
    metaData = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
    cuts = handler.retrievePreparedCuts()    
    return render_template('video-detail.html', cuts=cuts, link=link, videoTitle=metaData["title"])

@app.route('/add-video')
def addVideo():
    return render_template('add-video.html')

@app.route('/generate-cuts', methods=['POST'])
def generateCuts():        
    data = json.loads(request.data)    
    handler = CutsHandler(dir, data["link"])
    
    alreadySavedMeta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
    if len(alreadySavedMeta.keys()) > 0:
        return alreadySavedMeta
        
    handler.prepareCuts()    
    meta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
    return Response(json.dumps(meta), content_type="application/json")

@app.route('/generate-video-cuts', methods=['POST'])
def generateVideoCuts():
    data = json.loads(request.data)    
    selectedIds = [ int(id) for id in data["ids"]]
    handler = CutsHandler(dir, data["videoLink"])    
    handler.generateCutsFromVideo(selectedIds=selectedIds)
    return Response(json.dumps({"message": "Video clips generated successfully!"}), content_type="application/json")

@app.route('/delete-youtube-video', methods=['POST'])
def deleteYoutubeVideo():
    data = json.loads(request.data)    
    handler = CutsHandler(dir, data["link"])
    videoDir = handler.getVideoDirectory()
    shutil.rmtree(videoDir)
    return {"message": "Video deleted!"}

@app.route('/edit-cut', methods=['POST'])
def editCut():
    data = json.loads(request.data)    
    handler = CutsHandler(dir, data["link"])
    id = int(data["cut"]["id"])    
    cuts = handler.retrievePreparedCuts()    
    saved = False
    for index, c in enumerate(cuts):
        if c["id"] == id:
            cuts[index] = data["cut"]
            cuts[index]["id"] = id
            saved = True
            break
    handler.savePreparedCuts(cuts=cuts)
    return {"message": "Cut saved!" if saved else "Cut was not found."}

@app.route('/preview-cut', methods=['POST'])
def preview():
    data = json.loads(request.data)    
    handler = CutsHandler(dir, data["link"])
    handler.runPreview(data["cut"])
    return {"message": "Preview executed."}
    