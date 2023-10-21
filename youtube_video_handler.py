import os
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, vfx
import logging
from env import Env
from google_api import GoogleApi
from youtube_transcript_api.formatters import SRTFormatter
from moviepy.audio.fx import all as afx

class YouTubeVideoHandler:

    def __init__(self, videoLink: str, baseDirectory: str) -> None:
        self.__youtubeObject = YouTube(videoLink)
        self.__baseDirectory = baseDirectory
        self.__env = Env()
        self.finalInsertionVideoPath = self.__env.getEnvValue('VIDEO_ENDING_INSERTION_PATH')
        self.thumbsUpInsertionVideoPath = self.__env.getEnvValue('VIDEO_THUMBS_UP_INSERTION_PATH')
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
                     f'{self.__youtubeObject.title}.mp4'), max_retries=3)

        videoClip : VideoFileClip = VideoFileClip(videoFileName)
        finalVideoClip : VideoFileClip  = None;     
        audioClip : AudioFileClip = None 
        
        if insertAudio:
            audioClip : AudioFileClip = self.downloadAudio()            
            finalVideoClip = self.linkAudioToVideo(videoFileClip=videoClip, audioFileClip=audioClip)        
        else: 
            finalVideoClip = videoClip

        if saveFile:
            finalVideoClip.write_videofile(finalVideoFileName, audio_codec='libvorbis')

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
    
    def preview(self, start: int, end: int, video: VideoFileClip, audio: AudioFileClip) -> VideoFileClip:
        subVideo = video.subclip(start, end)
        subAudio = audio.subclip(start, end)
        subVideo: VideoFileClip = subVideo.set_audio(subAudio)
        subVideo.preview()
        return subVideo

    def cut(self, start: str, end: str, video: VideoFileClip, audio: AudioFileClip, fileName: str, isShort: bool = False) -> None:
        #00:00:09,640
        hours, minutes, seconds = start.split(":")
        startInSeconds = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds.replace(",", "."))
        hours, minutes, seconds = end.split(":")
        endInSecodns = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds.replace(",", "."))
        videoClip: VideoFileClip = video.subclip(startInSeconds, endInSecodns)
        audioClip: AudioFileClip = audio.subclip(start, end)
        audioClip = audioClip.fx(afx.audio_fadeout, 3)
        videoClipWithAudio: VideoFileClip = videoClip.set_audio(audioClip)  
        if self.finalInsertionVideoPath and not isShort:
            finalInsertionVideo = VideoFileClip(self.finalInsertionVideoPath)
            finalVideo = concatenate_videoclips([videoClipWithAudio, finalInsertionVideo])
        else:
            finalVideo = videoClipWithAudio

        if self.thumbsUpInsertionVideoPath and not isShort:
            thumbsUpInsertionVideo = VideoFileClip(self.thumbsUpInsertionVideoPath, has_mask=True, target_resolution=(360, 640))
            thumbsUpInsertionVideo = thumbsUpInsertionVideo.set_position(("center", "bottom"))
            #(50, 720)
            thumbsUpInsertionVideo = thumbsUpInsertionVideo.set_start(10)
            thumbsUpInsertionVideo = thumbsUpInsertionVideo.fx(vfx.mask_color, color=[0,188,0], thr=100, s=5)    
            finalVideo = CompositeVideoClip([finalVideo, thumbsUpInsertionVideo])

        videoClipDir = os.path.join(os.path.dirname(videoClip.filename), fileName.split('.')[0])
        if not os.path.exists(videoClipDir):
            os.makedirs(videoClipDir)
        finalVideo.write_videofile(os.path.join(videoClipDir, fileName), audio_codec='libvorbis')        
        