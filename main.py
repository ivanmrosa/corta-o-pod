import os
import json
import shutil
import re
import sys
import functools
from datetime import datetime
from pathlib import Path
from threading import Thread
import threading
from flask import Flask, request, render_template, Response
from env import Env
from cuts_handler import CutsHandler
from flask import render_template, request
#import webview

dir = Env().getEnvValue('VIDEOS_DIRECTORY')
app = Flask( __name__)


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

@app.route('/download-video', methods=['POST'])
def downloadVideo():        
    data = json.loads(request.data)      
    handler = CutsHandler(dir, data["link"])
    
    alreadySavedMeta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
    if len(alreadySavedMeta.keys()) > 0:
        return alreadySavedMeta

    handler.downloadVideo()    
    handler.savePreparedCuts([])    
    meta = CutsHandler.retriveMetadatas(handler.getVideoDirectory())
    return Response(json.dumps(meta), content_type="application/json")



@app.route('/generate-video-cuts', methods=['POST'])
def generateVideoCuts():
    data = json.loads(request.data)    
    selectedIds = [ int(id) for id in data["ids"]]
    #speedUps = [ float(id) for id in data["speedUps"]]
    handler = CutsHandler(dir, data["videoLink"])  
      
    handler.generateCutsFromVideo(selectedIds=selectedIds, speedUps=data["speedUps"])
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

@app.route('/donwload-video-page')
def downloadVideoPage():
    return render_template('download-video.html')

# @app.route('/preview-cut', methods=['GET'])
# def preview():
#     link = request.args['link']        
#     #data = json.loads(request.data)    
#     handler = CutsHandler(dir, link)
#     handler.getPreview(10, 30)
#     return {"message": "Preview executed."}

# @app.route("/preview-video", methods=["GET"])
# def previewVideo():
#     link = request.args['link']        
#     return render_template('preview-video.html', link=link)



@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def get_chunk(byte1=None, byte2=None, path=""):

    full_path = path
    file_size = os.stat(full_path).st_size
    start = 0
    
    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
         f.seek(start)
         chunk = f.read(length)
    
    return chunk, start, length, file_size


@app.route('/stream-video')
def get_file():
    link = request.args.get('link') 
    cutId = request.args.get('id') 
    handler = CutsHandler(dir, link)    
    cuts = handler.retrievePreparedCuts()
    cut = list(filter(lambda cut: cut["id"] == int(cutId), cuts))[0]
    path = os.path.join(handler.getVideoDirectory(), cut["cutPath"].split('/')[-2], os.path.basename(cut["cutPath"]))     

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])
       
    chunk, start, length, file_size = get_chunk(byte1, byte2, path)
    resp = Response(chunk, 206, mimetype='video/mp4',
                      content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

def start_server():
    app.run(host='0.0.0.0', debug=False, port=8080)
    #app.run()





if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)        
    
    # t = threading.Thread(target=start_server)
    # t.daemon = True
    # t.start()
  
    # webview.create_window("Corta o Pod", "http://127.0.0.1:8080", width=1080, height=1024)
    # webview.start(gui='qt')
    # sys.exit()    
    
    
    
