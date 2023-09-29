import os
import json
from youtube_video_handler import YouTubeVideoHandler
from caption_formatter import CaptionFormatter
from moviepy.editor import VideoFileClip, AudioFileClip

class CutsHandler:

    def __init__(self, baseDir: str, youtubeVideoLink: str) -> None:
        self.__baseDir = baseDir     
        self.__link = youtubeVideoLink
        self.__youtubeHandler : YouTubeVideoHandler = YouTubeVideoHandler(youtubeVideoLink, self.__baseDir)    
        self.__videoDir = os.path.join(
            self.__baseDir, 
            f'{self.__youtubeHandler.getVideoTitle()}_{self.__youtubeHandler.getVideoId()}',
        )
    
    def __savedataOnMetadata(self, name, value):
        with open(os.path.join(self.__videoDir, 'metadata'), 'a') as f:
            f.write(f'{name}==>{value}\n')
    
    def getVideoDirectory(self):
        return self.__videoDir

    @classmethod
    def retriveMetadatas(cls, videoDirectory: str) -> dict:
        try:
            with open(os.path.join(videoDirectory, 'metadata'), 'r') as f:
                lines = f.readlines()
            
            metas = {}
            for line in lines:
                keyValue = line.split("==>")
                metas.update({keyValue[0]: keyValue[1]})
            return metas
        except Exception as e:
            print(e)
            return {}


    def saveMetadatas(self):
        if not os.path.exists(self.__videoDir):
            os.mkdir(self.__videoDir)
        self.__savedataOnMetadata('link', self.__link)
        self.__savedataOnMetadata('title', self.__youtubeHandler.getVideoTitle())
        self.__savedataOnMetadata('id', self.__youtubeHandler.getVideoId())

    def prepareCuts(self):  
        self.saveMetadatas()
        self.__savedataOnMetadata('link', self.__link)
        self.__youtubeHandler.chanceBaseDir(self.__videoDir)
        self.__youtubeHandler.downloadVideo(False, False)
        self.__youtubeHandler.downloadAudio()
        captionFormatter = CaptionFormatter()
        captionPath = self.__youtubeHandler.downloadCaption()
        cuts = captionFormatter.getCuts(captionPath)        
        self.savePreparedCuts(cuts)
            
    def retrievePreparedCuts(self) -> list[dict]:        
        path = os.path.join(self.__videoDir, 'cutsdb.json')
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            data = f.read()        
        return json.loads(data)
    
    def savePreparedCuts(self, cuts: list[dict]):
        with open(os.path.join(self.__videoDir, 'cutsdb.json'), 'w') as f:
            f.write(json.dumps(cuts))

    def retrieveAudioFromLocalStorage(self) -> AudioFileClip:
        return AudioFileClip(os.path.join(self.__videoDir, self.__youtubeHandler.getVideoTitle(), '_audio.mp4'))

    def retrieveVideoFromLocalStorage(self) -> VideoFileClip:
        return VideoFileClip(os.path.join(self.__videoDir, self.__youtubeHandler.getVideoTitle(), '.mp4'))

    def generateCutsFromVideo(self):
        audioFileClip = self.retrieveAudioFromLocalStorage()
        videoFileClip = self.retrieveVideoFromLocalStorage()
        preparedCutsJson: list[dict] = self.retrievePreparedCuts()
        #pegar os cortes
        filteredList = list(filter(lambda item: item["selected"], preparedCutsJson))
        for cut in filteredList:
            self.__youtubeHandler.cut(cut["startTime"], cut["endTime"], videoFileClip, audioFileClip, f'{cut["title"]}.mp4')
        