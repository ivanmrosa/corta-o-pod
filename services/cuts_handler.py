import os
import json
from datetime import datetime
from services.youtube_video_handler import YouTubeVideoHandler
from services.caption_formatter import CaptionFormatter
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
                metas.update({keyValue[0]: keyValue[1].replace('\n', '')})
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
        self.__savedataOnMetadata('uploadDate', datetime.now())
    
    def downloadVideo(self) -> str:
        self.saveMetadatas()        
        self.__youtubeHandler.chanceBaseDir(self.__videoDir)
        self.__youtubeHandler.downloadVideo(False, False)
        #self.__youtubeHandler.downloadAudio()
        return self.__youtubeHandler.downloadCaption()

    def prepareCuts(self):  
        #self.saveMetadatas()        
        # self.__youtubeHandler.chanceBaseDir(self.__videoDir)
        # self.__youtubeHandler.downloadVideo(False, False)
        # self.__youtubeHandler.downloadAudio()        
        # captionPath = self.__youtubeHandler.downloadCaption()
        captionPath = self.downloadVideo()        
        captionFormatter = CaptionFormatter()        
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
        path = os.path.join(self.__videoDir, f'{self.__youtubeHandler.getVideoTitle()}_audio.mp3')
        if not os.path.exists(path=path):
            path = os.path.join(self.__videoDir, f'{self.__youtubeHandler.getVideoTitle()}_audio.mp4')
            if not os.path.exists(path=path):           
                path = os.path.join(self.__videoDir, f'{self.__youtubeHandler.getVideoTitle()}_audio.webm')
                            
        return AudioFileClip(path)

    def retrieveVideoFromLocalStorage(self) -> VideoFileClip:
        return VideoFileClip(os.path.join(self.__videoDir, f'{self.__youtubeHandler.getVideoTitle()}.mp4'))
    
    def selectVideos(self, selectedIds : dict):
        cuts = self.retrievePreparedCuts()
        for index in range(len(cuts)):
            cuts[index]["selected"] = False
            if cuts[index]["id"] in selectedIds:
                cuts[index]["selected"] = True
                cuts[index]["cutPath"] =  os.path.join(self.getVideoDirectory(), cuts[index]["title"], f'{cuts[index]["title"]}.mp4' ) 
        
        self.savePreparedCuts(cuts=cuts)

    def getPreview(self, start, end) -> VideoFileClip:
        audio = self.retrieveAudioFromLocalStorage()
        video = self.retrieveVideoFromLocalStorage()
        return self.__youtubeHandler.preview(start, end, video, audio)
        
    def generateCutsFromVideo(self, selectedIds : dict, speedUps: list[dict[int, float]]):
        self.selectVideos(selectedIds=selectedIds)
        #audioFileClip = self.retrieveAudioFromLocalStorage()
        videoFileClip = self.retrieveVideoFromLocalStorage()
        preparedCutsJson: list[dict] = self.retrievePreparedCuts()
        #pegar os cortes
        filteredList = list(filter(lambda item: item["selected"], preparedCutsJson))
        for cut in filteredList:
            isShort = "short" in cut and cut["short"]

            filteredSpeedUps: list[dict[int, float]] = list(filter(lambda item: int(list(item.keys())[0]) == cut["id"], speedUps))
            speedUpValue = 1 if len(filteredSpeedUps) == 0 else list(filteredSpeedUps[0].values())[0]

            self.__youtubeHandler.cut(
                cut["startTime"], 
                cut["endTime"], 
                videoFileClip, 
                None, 
                f'{cut["title"]}.mp4',
                isShort=isShort,
                speedUp=speedUpValue,                
            )
