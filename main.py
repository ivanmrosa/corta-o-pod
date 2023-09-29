import os
import json
from pathlib import Path
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
    paths = sorted(Path(dir).iterdir(), key=os.path.getmtime)
    videos = []
    
    for path in paths:
        meta = CutsHandler.retriveMetadatas(path)
        print(meta)
        if len(meta.keys()) > 0:
            videos.append(meta)

    return render_template('home.html', videos=videos)


@app.route('/video-detail')
def videoDetail():
    link = request.args['link']
    handler = CutsHandler(dir, link)
    cuts = handler.retrievePreparedCuts()    
    return render_template('video-detail.html', cuts=cuts)

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
    return Response(json.dumps
    (meta), content_type="application/json")





#/Users/ivanmuniz/Documents/dev/corta-o-pod/cortaopod/lib/python3.11/site-packages/pytube/cipher.py
#chanched line 411 -> transform_plan_raw = js #find_object_from_startpoint(raw_code, match.span()[1] - 1)
#unkown error happened and that change solved it

#
#link = "https://www.youtube.com/watch?v=-roK1JndcBY&t=24s"
#handler = CutsHandler(dir)
#handler.saveCuts(link)





#youtubeHandler : YouTubeVideoHandler = YouTubeVideoHandler(link, dir)
#videoFileClip = youtubeHandler.downloadVideo(False, False)
#audioFileClip = youtubeHandler.downloadAudio()
#youtubeHandler.cut("00:05:16,58", "00:06:17,00", video=videoFileClip, audio=audioFileClip, fileName='clip1.mp4')

#pegar os cortes
#captionFormatter = CaptionFormatter()
#captionPath = youtubeHandler.downloadCaption()
#cuts = captionFormatter.getCuts(captionPath)
#for cut in cuts:
#    youtubeHandler.cut(cut["startTime"], cut["endTime"], videoFileClip, audioFileClip, f'{cut["title"]}.mp4')



#cortar os pedacos


# captionFormatter = CaptionFormatter()
# data = captionFormatter.mapCaption(os.path.join(dir, 'texto_teste.txt'), 10_000)

#with open(os.path.join(dir, 'mapping.json'), 'w') as f:
#    f.writelines(json.dumps(data))

#with open(os.path.join(dir, 'TIAGO LEIFERT - Flow #268', 'TIAGO LEIFERT - Flow #268.str'), 'r') as f:
#   text: str = f.read()

#text = text[0: 10_0000]
#chatGpt = ChatGpt()
#cuts = chatGpt.requireCuts(text)
#print(cuts)

#captionFormatter = CaptionFormatter()
#captionsPath = "/Users/ivanmuniz/Documents/dev/corta-o-pod/TIAGO LEIFERT - Flow #268.str"
#print(captionFormatter.getCuts(captionsPath))
