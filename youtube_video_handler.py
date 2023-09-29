import os
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import logging
from env import Env
from google_api import GoogleApi
from youtube_transcript_api.formatters import SRTFormatter

class YouTubeVideoHandler:

    def __init__(self, videoLink: str, baseDirectory: str) -> None:
        self.__youtubeObject = YouTube(videoLink)
        self.__baseDirectory = baseDirectory
        self.__env = Env()
        self.__googleApi = GoogleApi()
    
    def getVideoTitle(self):
        return self.__youtubeObject.title

    def getVideoId(self):
        return self.__youtubeObject.video_id
    
    def chanceBaseDir(self, dir):
        self.__baseDirectory = dir

    def downloadAudio(self) -> AudioFileClip:
        audioFileName = os.path.join(
            self.__baseDirectory, f'{self.__youtubeObject.title}_audio.mp4')
        audio160Kbps = 140
        audioFiles = self.__youtubeObject.streams.filter(only_audio=True)
        audioFiles.get_by_itag(audio160Kbps).download(filename=audioFileName)
        return AudioFileClip(audioFileName)

    def downloadVideo(self, insertAudio: bool, saveFile: bool = True) -> VideoFileClip:
        fullHdTag = 137

        videoFileName = os.path.join(
            self.__baseDirectory, f'{self.__youtubeObject.title}.mp4')
        finalVideoFileName = os.path.join(
            self.__baseDirectory, f'{self.__youtubeObject.title}_final.mp4')
        
        self.__youtubeObject.streams.\
            filter(file_extension="mp4").\
            get_by_itag(fullHdTag).\
            download(filename=os.path.join(self.__baseDirectory,
                     f'{self.__youtubeObject.title}.mp4'))

        videoClip : VideoFileClip = VideoFileClip(videoFileName)
        finalVideoClip : VideoFileClip  = None;     
        audioClip : AudioFileClip = None 
        
        if insertAudio:
            audioClip : AudioFileClip = self.downloadAudio()            
            finalVideoClip = self.linkAudioToVideo(videoFileClip=videoClip, audioFileClip=audioClip)        
        else: 
            finalVideoClip = videoClip

        if saveFile:
            finalVideoClip.write_videofile(finalVideoFileName)

        if audioClip:
            self.removeAudioFile(audioClip)
                
        
        if saveFile:
            videoClip.close()
            os.remove(videoFileName)
            
        return finalVideoClip
    
    def removeAudioFile(self, audioFileClip: AudioFileClip):
        audioFileClip.close()
        os.remove(audioFileClip.filename)


    def linkAudioToVideo(self, videoFileClip: VideoFileClip, audioFileClip: AudioFileClip) -> VideoFileClip:
        result = videoFileClip.set_audio(audioFileClip)        
        return result


    def downloadCaption(self, languageCode='pt') ->str:
        '''
          return (filePathTxt, filePathSTR)
        '''
        try:

            filePathSTR: str = os.path.join(
                self.__baseDirectory, f'{self.__youtubeObject.title}.str'
            )
            
            caption = self.__googleApi.getVideoCaption(self.__youtubeObject.video_id, languageCode)
            strFormatter = SRTFormatter()
                        
            with open(filePathSTR, 'w') as fileStr:
                fileStr.writelines(strFormatter.format_transcript(caption))
            
            return filePathSTR
        except Exception as e:
            logging.error(e)
            return ""

    def cut(self, start: str, end: str, video: VideoFileClip, audio: AudioFileClip, fileName: str) -> None:
        #00:00:09,640
        hours, minutes, seconds = start.split(":")
        startInSeconds = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds.replace(",", "."))
        hours, minutes, seconds = end.split(":")
        endInSecodns = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds.replace(",", "."))
        videoClip: VideoFileClip = video.subclip(startInSeconds, endInSecodns)
        audioClip: AudioFileClip = audio.subclip(start, end)
        videoClipWithAudio: VideoFileClip = videoClip.set_audio(audioClip)
        videoClipWithAudio.write_videofile(os.path.join(os.path.dirname(videoClip.filename), fileName)) 
        