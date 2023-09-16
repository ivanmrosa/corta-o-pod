import os
from youtube_video_handler import YouTubeVideHandler

dir = os.path.dirname(__file__)
link = "https://www.youtube.com/watch?v=-roK1JndcBY&t=24s"
#https://www.youtube.com/watch?v=1A54-XyDffE
youtubeHandler : YouTubeVideHandler = YouTubeVideHandler(link, dir)
#youtubeHandler.downloadVideo()
youtubeHandler.downloadCaption()
