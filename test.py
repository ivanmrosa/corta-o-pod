import os
import sys
import json
import shutil
from caption_formatter import CaptionFormatter
from youtube_video_handler import YouTubeVideoHandler



dir = os.path.join(os.path.dirname(__file__), 'test')

captionFormatter = CaptionFormatter()
youTubeVideoHandler = YouTubeVideoHandler('https://www.youtube.com/watch?v=V7kgsvdZ0SU', dir)

youTubeVideoHandler.downloadCaption()
fileName = os.path.join(dir, f'{youTubeVideoHandler.getVideoTitle()}.str')
destFileName = os.path.join(dir, f'new_{youTubeVideoHandler.getVideoTitle()}.str')
mappedFile = os.path.join(dir, f'mapped_{youTubeVideoHandler.getVideoTitle()}.json')
cutsFile = os.path.join(dir, f'cuts_{youTubeVideoHandler.getVideoTitle()}.json')
shutil.copy(fileName,  destFileName)

captionFormatter.normalizeStrCaption(filePathToStr=fileName)
mapped = captionFormatter.mapCaption(filePathToStr=fileName, maximumCharactersPerTextBlock=10_000)
with open(mappedFile, 'w') as f:
    f.writelines(json.dumps(mapped, indent=4))

cuts = captionFormatter.getCuts(filePathToStr=fileName)

with open(cutsFile, 'w') as f:
    f.writelines(json.dumps(cuts, indent=4))
