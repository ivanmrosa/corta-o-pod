import os
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import logging


class YouTubeVideHandler:

    def __init__(self, videoLink: str, baseDirectory: str) -> None:
        self.__youtubeObject = YouTube(videoLink)
        self.__baseDirectory = baseDirectory

    def downloadAudio(self) -> AudioFileClip:
        audioFileName = os.path.join(
            self.__baseDirectory, f'{self.__youtubeObject.title}_audio.mp4')
        audio160Kbps = 140
        audioFiles = self.__youtubeObject.streams.filter(only_audio=True)
        audioFiles.get_by_itag(audio160Kbps).download(filename=audioFileName)
        return AudioFileClip(audioFileName)

    def downloadVideo(self) -> str:
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

        videoClip = VideoFileClip(videoFileName)
        audioClip = self.downloadAudio()

        finalVideoClip: VideoFileClip = videoClip.set_audio(audioClip)
        finalVideoClip.write_videofile(finalVideoFileName)

        audioFilename = audioClip.filename
        audioClip.close()
        os.remove(audioFilename)
        videoClip.close()
        os.remove(videoFileName)

    def downloadCaption(self, languageCode='pt-br') -> str:
        try:
            filePath: str = os.path.join(
                self.__baseDirectory, f'{self.__youtubeObject.title}.str'
            )
            print(self.__youtubeObject.captions)
            caption = self.__youtubeObject.captions.\
                get_by_language_code(languageCode).\
                generate_srt_captions()
            with open(filePath, 'w') as file:
                file.writelines(caption)
            return filePath
        except Exception as e:
            logging.error(e)
            return ""

