from env import Env
from services.api import RequestApi
from youtube_transcript_api import YouTubeTranscriptApi



class GoogleApi:
    def __init__(self) -> None:
        self.__env = Env()
        self.__baseUrl : str = self.__env.getEnvValue("YOUTUBE_API_BASE_URL")
        self.__apiKey : str = self.__env.getEnvValue("YOUTUBE_API_KEY")
        self.__api = RequestApi(baseUrl=self.__baseUrl)
        
    
    def getPreparedEndpoint(self, endpoint: str, params : dict = {}):
        newEndpoint = f"{endpoint}?key={self.__apiKey}"
        if len(params.keys()) > 0:
            for key in params.keys():
                newEndpoint += f'&{key}={params[key]}'
        print(newEndpoint)
        return newEndpoint
        
        
    def getCaptionId(self, videoId: str) -> str:
        captionData =  self.__api.getMany(self.getPreparedEndpoint('/captions', {"videoId": videoId}))
        if not captionData: return ""
        captions = captionData["items"]
        if len(captions) > 0:
           return captions[0]["id"]
           
        return ""
    
    def getVideoCaption(self, videoId: str, language : str = 'pt'):    
        return YouTubeTranscriptApi.get_transcript(videoId, languages=(language, ))
