import os
import sys
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, vfx
from moviepy.audio.fx import all as afx
from pytube import YouTube


def prepareVideoEndingIsertion():
    audio = AudioFileClip('/Users/ivanmuniz/Documents/youtube/corta o pod/video-finishing/Lawrence - TrackTribe.mp3')
    video = VideoFileClip('/Users/ivanmuniz/Documents/youtube/corta o pod/video-finishing/corta o pod final.mp4')
    cutedVideo = video.subclip(2, 7)
    cutedAudio = audio.subclip(0, 15)
    cutedAudio = cutedAudio.fx(afx.audio_fadein, 1)
    cutedAudio = cutedAudio.fx(afx.audio_fadeout, 2)

    concatVideos = concatenate_videoclips([video, cutedVideo])
    newVideo: VideoFileClip = concatVideos.set_audio(cutedAudio)
    
    newVideo.write_videofile('/Users/ivanmuniz/Documents/youtube/corta o pod/video-finishing/final_insertion.mp4')



def downloadLikeTheVideo():
    dir = os.getcwd()
    yt : YouTube  = YouTube("https://www.youtube.com/watch?app=desktop&v=N_blEXNSps4") #YouTube('https://www.youtube.com/watch?v=haJr4dW11YQ')
    
    videoFilename = os.path.join(dir,
                    f'{yt.title}.mp4')
    videoFilenameNew = os.path.join(dir,
                    f'{yt.title}_new.mp4')
    yt.streams.\
        filter(file_extension="mp4").\
        get_by_itag(136).\
        download(filename=videoFilename, max_retries=3)
    
    audioFileName = os.path.join(
        dir, f'{yt.title}_audio.mp4')
    audio160Kbps = 140
    audioFiles = yt.streams.filter(only_audio=True)
    audioFiles.get_by_itag(audio160Kbps).download(filename=audioFileName)
    acl = AudioFileClip(audioFileName)
    vcl = VideoFileClip(videoFilename)
    vcl2 : VideoFileClip = vcl.set_audio(acl)
    vcl2.write_videofile(videoFilenameNew)


def insertThumbsUpTest():
    dir = os.getcwd()
    videoPath = '/Users/ivanmuniz/Documents/dev/corta-o-pod/videos/A VERDADE QUE NINGUÉM TE CONTA SOBRE OS ALIMENTOS ORGÂNICOS • Física e Afins_o4guj5nRkq8/Alimentos Orgânicos no Brasil 2/Alimentos Orgânicos no Brasil 2.mp4'
    videoInsertionPath = '/Users/ivanmuniz/Documents/dev/corta-o-pod/ANIMAÇÃO DE INSCREVA-SE LIKE E SININHO E NOTIFICAÇÃO CHROMA KEY_new.mp4'
    
    vcl = VideoFileClip(videoPath)
    ivcl = VideoFileClip(videoInsertionPath, has_mask=True, target_resolution=(360, 640))
    ivcl = ivcl.set_position(("center", "bottom"))
    #(50, 720)
    ivcl = ivcl.set_start(10)
    ivcl = ivcl.fx(vfx.mask_color, color=[0,188,0], thr=100, s=5)    
    final = CompositeVideoClip([vcl, ivcl])
    videoFilenameNew = os.path.join(dir,
                    f'teste_new.mp4')
    final.write_videofile(videoFilenameNew)


if __name__ == '__main__':    
    ...
    #insertThumbsUpTest()
    #downloadLikeTheVideo()