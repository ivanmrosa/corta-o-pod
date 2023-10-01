from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.audio.fx import all as afx

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


if __name__ == '__main__':    
    prepareVideoEndingIsertion()