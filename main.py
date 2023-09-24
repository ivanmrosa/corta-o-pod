import os
import json
from youtube_video_handler import YouTubeVideoHandler
from env import Env
from caption_formatter import CaptionFormatter
from chat_gpt import ChatGpt

dir = os.path.dirname(__file__)
link = "https://www.youtube.com/watch?v=-roK1JndcBY&t=24s"
#https://www.youtube.com/watch?v=1A54-XyDffE
youtubeHandler : YouTubeVideoHandler = YouTubeVideoHandler(link, dir)
youtubeHandler.downloadVideo(True)


# captionFormatter = CaptionFormatter()
# data = captionFormatter.mapCaption(os.path.join(dir, 'texto_teste.txt'), 10_000)

#with open(os.path.join(dir, 'mapping.json'), 'w') as f:
#    f.writelines(json.dumps(data))

#with open(os.path.join(dir, 'texto_teste.txt'), 'r') as f:
#    text: str = f.read()

#text = text[0: 10_0000]
#chatGpt = ChatGpt()
#cuts = chatGpt.requireCuts(text)
#print(cuts)

#captionFormatter = CaptionFormatter()
#captionsPath = "/Users/ivanmuniz/Documents/dev/corta-o-pod/TIAGO LEIFERT - Flow #268.str"
#print(captionFormatter.getCuts(captionsPath))
