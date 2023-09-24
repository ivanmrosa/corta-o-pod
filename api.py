import json 
import ssl
import urllib
import gzip
from urllib import request
from abc import ABC



class IRequest(ABC):
    def post(self, endpoint: str, data: dict) -> [str | dict | list]:
        pass
    
    def put(self, endpoint: str, id: int, data: dict) -> [str | dict | list]:
        pass

    def delete(self, endpoint: str, id: int) -> [str | dict | list] :
        pass

    def getMany(self, endpoint: str, limit=None) -> list:
        pass
    
    def getOne(self, endpoint: str, id : int) -> dict:
        pass
    
    def addHeader(self, name: str, value: any):
        pass

class RequestApi(IRequest):
    def __init__(self, baseUrl: str, contentType: str = 'application/json') -> None:
        print("Starting proccess RequestApi...")
        self.baseUrl = baseUrl
        self.headers = {}
        self.contentType = contentType
    
    def addHeader(self, name: str, value: any):
        print("Adding header {name}".format(name=name))
        self.headers.update({name: value})
        
    def removeHeader(self, name):
        del self.headers[name]
        
    def __getHeaders(self):
        header = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                    'Content-Type': self.contentType
                 }

        for key in self.headers:
            header.update({key: self.headers[key]})
        print("Header {header}".format(header=self.headers))
        return header
    
    def get_full_url(self, endpoint, limit=None):
        if limit is not None:
            return self.baseUrl + endpoint + '?rows_limit={limit}'.format(limit=limit) 
        else:
            return self.baseUrl + endpoint

    def __do_request(self, url, method, data, limit=None) -> [str | dict]:        
        headers = self.__getHeaders()
        #PROTOCOL_TLSv1
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        https_handler = request.HTTPSHandler(context=gcontext)
        opener = request.build_opener(https_handler)
        request.install_opener(opener)
        print(self.get_full_url(url, limit))
        if data is not None:
            req = request.Request(url=self.get_full_url(url, limit), headers=headers,\
                method=method, data=json.dumps(data).encode('utf-8')) 
        else:
            req = request.Request(url=self.get_full_url(url, limit), headers=headers, method=method)         
        
        with request.urlopen(req) as f:                        
            if f.info().get('Content-Encoding') == 'gzip':
                data: bytes = f.read()
                text = gzip.decompress(data) 
                text = text.decode('utf-8')                               
            else:
                text = f.read().decode('utf-8')                
                        
        if self.contentType == 'application/json':
            return json.loads(text)
            
        
        return text
    
    def __getEndpointWithId(self, endpoint, id: str):
        return endpoint + '/' + id
    
    def post(self, endpoint: str, data: dict) -> [str | dict]:
        return self.__do_request(endpoint, 'POST', data)
    
    def put(self, endpoint: str, id: int, data: dict) -> [str | dict]:
        url = self.__getEndpointWithId(endpoint, id)
        return self.__do_request(url, 'PUT', data)

    def delete(self, endpoint: str, id: int) -> [str | dict]:
        url = self.__getEndpointWithId(endpoint, id)
        return self.__do_request(url, 'DELETE', None)

    def getMany(self, endpoint: str, limit=None) -> [str | dict]:
        return self.__do_request(endpoint, 'GET', None, limit)
    
    def getOne(self, endpoint: str, id : str) -> dict:
        url = self.__getEndpointWithId(endpoint, id)
        return self.__do_request(url, 'GET', None)
