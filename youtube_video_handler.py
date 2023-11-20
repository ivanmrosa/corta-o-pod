import os
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, vfx
import logging
from env import Env
from services.google_api import GoogleApi
from youtube_transcript_api.formatters import SRTFormatter
from moviepy.audio.fx import all as afx
import moviepy.editor as mpy
from moviepy.video.fx.all import crop

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
        #audio160Kbps = 251
        audio160Kbps = 140

        audioFileName = os.path.join(
            self.__baseDirectory, f'{self.__youtubeObject.title}_audio.mp3')
        
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
                     f'{self.__youtubeObject.title}.mp4'), max_retries=5)

        videoClip : VideoFileClip = VideoFileClip(videoFileName)
        finalVideoClip : VideoFileClip  = None;     
        audioClip : AudioFileClip = None 
        
        if insertAudio:
            audioClip : AudioFileClip = self.downloadAudio()            
            finalVideoClip = self.linkAudioToVideo(videoFileClip=videoClip, audioFileClip=audioClip)        
        else: 
            finalVideoClip = videoClip

        if saveFile:
            finalVideoClip.write_videofile(finalVideoFileName, audio_codec='libmp3lame')

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

    def makeShortAspectRatio(self, originalVideoClip: VideoFileClip) -> VideoFileClip:

        clip = originalVideoClip
        (w, h) = clip.size

        crop_width = h * 9/16
        # x1,y1 is the top left corner, and x2, y2 is the lower right corner of the cropped area.

        x1, x2 = (w - crop_width)//2, (w+crop_width)//2
        y1, y2 = 0, h
        return crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)
        # or you can specify center point and cropped width/height
        # cropped_clip = crop(clip, width=crop_width, height=h, x_center=w/2, y_center=h/2)
        #cropped_clip.write_videofile('path/to/cropped/video.mp4')        

    def cut(self, start: str, end: str, video: VideoFileClip, audio: AudioFileClip, fileName: str, isShort: bool = False, speedUp: int = 1) -> None:
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
        
        if speedUp > 1:
            finalVideo = finalVideo.fx(vfx.speedx, speedUp) 

        videoClipDir = os.path.join(os.path.dirname(videoClip.filename), fileName.split('.')[0])
        if not os.path.exists(videoClipDir):
            os.makedirs(videoClipDir)
        
        if isShort:
            shortVideo = self.makeShortAspectRatio(finalVideo)
            name, ext = fileName.split('.')
            shortName = f'{name}_short.{ext}'
            shortVideo.write_videofile(os.path.join(videoClipDir, shortName), audio_codec='aac')        

        finalVideo.write_videofile(os.path.join(videoClipDir, fileName), audio_codec='aac')        
        