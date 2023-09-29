import json
from env import Env
from api import RequestApi


class ChatGpt:
    def __init__(self) -> None:
        self.__env = Env()
        self.__chatGptKey = self.__env.getEnvValue("CHAT_GPT_API_KEY")
        self.__chatGptPhraseToRequestCuts = self.__env.getEnvValue("CHAT_GPT_PHRASE_TO_REQUEST_CUTS")
        self.__chatGptBaseUrl = self.__env.getEnvValue("CHAT_GPT_BASE_URL")
        self.__chatGptModel = self.__env.getEnvValue("CHAT_GPT_MODEL")
        self.__api = RequestApi(self.__chatGptBaseUrl)
        self.__api.addHeader("Authorization", f"Bearer {self.__chatGptKey}")
        self.__api.addHeader("Content-Type", f"application/json; charset=utf-8")
            
    
    def requireCuts(self, captionText: str) -> dict:
        chatMessages : list = []
        chatMessages.append({"role": "user", "content": f'{self.__chatGptPhraseToRequestCuts} "{captionText[0: 10_000]}"'})
        request =  {
                "model": self.__chatGptModel,
                "messages": chatMessages
            }
        try:
            response = self.__api.post('/chat/completions', request)["choices"][0]["message"]["content"]
        except Exception as e:
            print(e)
            response=""
        print(response)
        try:    
            data =  json.loads(response)
        except Exception as e:
            print(e)
            return []

        return data
        