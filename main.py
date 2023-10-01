import os
import json
from datetime import datetime
from pathlib import Path
import shutil
from flask import Flask, request, render_template, Response

from youtube_video_handler import YouTubeVideoHandler
from env import Env
from caption_formatter import CaptionFormatter
from chat_gpt import ChatGpt
from cuts_handler import CutsHandler

dir = os.path.join(os.path.dirname(__file__), 'videos')
app = Flask(__name__)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)


@app.route('/')
def home():
    #paths = sorted(Path(dir).iterdir(), key=os.path.getatime)    
    paths = Path(dir).iterdir()
    videos = []
    
    for path in paths:
        meta = CutsHandler.retriveMetadatas(path)
        print(meta)
        if len(meta.keys()) > 0:
            videos.append(meta)
    print(videos)
    videos = sorted(videos, 
        key=lambda video: datetime.strptime(video["uploadDate"].split('.')[0], 
                                            '%Y-%m-%d %H:%M:%S'), reverse=True)
    
    
    return render_template('home.html', videos=videos)


@app.route('/video-detail')
def videoDetail():
    link = request.args['link']
    handler = CutsHandler(dir, link)
    cuts = handler.retrievePreparedCuts()    
    return render_template('video-detail.html', cuts=cuts, link=link)

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
    print(data)
    selectedIds = [ int(id) for id in data["ids"]]
    handler = CutsHandler(dir, data["videoLink"])
    cuts = handler.retrievePreparedCuts()
    for index in range(len(cuts)):
        cuts[index]["selected"] = False
        if cuts[index]["id"] in selectedIds:
            cuts[index]["selected"] = True
            cuts[index]["cutPath"] =  os.path.join(handler.getVideoDirectory(), f'{cuts[index]["title"]}.mp4' ) 
    
    handler.savePreparedCuts(cuts=cuts)
    handler.generateCutsFromVideo()
    return Response(json.dumps({"message": "Video clips generated successfully!"}), content_type="application/json")

@app.route('/delete-youtube-video', methods=['POST'])
def deleteYoutubeVideo():
    data = json.loads(request.data)    
    handler = CutsHandler(dir, data["link"])
    videoDir = handler.getVideoDirectory()
    shutil.rmtree(videoDir)
    return {"message": "Video deleted!"}