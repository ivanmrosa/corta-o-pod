# import os
# import sys
# import json
# import shutil
# #from services.caption_formatter import CaptionFormatter
# #from services.youtube_video_handler import YouTubeVideoHandler
# import pydub

# import speech_recognition as sr

# dir = os.path.join(os.path.dirname(__file__), 'test')

# AUDIO_FILE_OLD = os.path.join(dir, 'MARTHA GABRIEL - Venus Podcast #521_audio.mp3')
# AUDIO_FILE = os.path.join(dir, 'MARTHA GABRIEL - Venus Podcast #521_audio.wav')


# sound = pydub.AudioSegment.from_mp3(AUDIO_FILE_OLD)
# sound.export(AUDIO_FILE, format="wav")


# # AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
# # AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")

# # use the audio file as the audio source
# r = sr.Recognizer()
# with sr.AudioFile(AUDIO_FILE) as source:
#     audio = r.record(source)  # read the entire audio file

# # recognize speech using Sphinx
# try:
#     print("Sphinx thinks you said " + r.recognize_sphinx(audio))
# except sr.UnknownValueError:
#     print("Sphinx could not understand audio")
# except sr.RequestError as e:
#     print("Sphinx error; {0}".format(e))


# # captionFormatter = CaptionFormatter()
# # youTubeVideoHandler = YouTubeVideoHandler('https://www.youtube.com/watch?v=V7kgsvdZ0SU', dir)

# # youTubeVideoHandler.downloadCaption()
# # fileName = os.path.join(dir, f'{youTubeVideoHandler.getVideoTitle()}.str')
# # destFileName = os.path.join(dir, f'new_{youTubeVideoHandler.getVideoTitle()}.str')
# # mappedFile = os.path.join(dir, f'mapped_{youTubeVideoHandler.getVideoTitle()}.json')
# # cutsFile = os.path.join(dir, f'cuts_{youTubeVideoHandler.getVideoTitle()}.json')
# # shutil.copy(fileName, destFileName)

# # captionFormatter.normalizeStrCaption(filePathToStr=fileName)
# #mapped = captionFormatter.mapCaption(filePathToStr=fileName, maximumCharactersPerTextBlock=10_000)
# #with open(mappedFile, 'w') as f:
# #    f.writelines(json.dumps(mapped, indent=4))

# #cuts = captionFormatter.getCuts(filePathToStr=fileName)

# #with open(cutsFile, 'w') as f:
# #    f.writelines(json.dumps(cuts, indent=4))

import os
from moviepy.editor import *


def remove_video_clip(videoPath: str, parts_to_keep: list[tuple[str, str]]):
    clip = VideoFileClip(videoPath)  
    clips = []
    # getting only first 5 seconds  
    # cutting out some part from the clip     
    for cl in parts_to_keep:        
        clips.append(clip.subclip(cl[0], cl[1]))   
    newpath = f"{videoPath.split('.')[0]}_new.mp4"
    oldPath = f"{videoPath.split('.')[0]}_old.mp4"
    new_clip = concatenate_videoclips(clips)
    new_clip.write_videofile(os.path.join(newpath), audio_codec='aac')
    os.rename(videoPath, oldPath)
    os.rename(newpath, videoPath)



remove_video_clip("/Users/ivanmuniz/Documents/youtube/corta o pod/videos/MARIA PAULA - Inteligência Ltda. Podcast #1081_tUGJheE2d1E/SOBRENATURAL ou CONICIDÊNCIA?/SOBRENATURAL ou CONICIDÊNCIA?.mp4", 
                  [('00:00:00,000', '00:00:57,500')])
    
