import os
import re
from flask import Response, request
from flask.views import MethodView
from services.cuts_handler import CutsHandler
from env import Env


class StreamController(MethodView):

    def __init__(self) -> None:        
        super().__init__() 
        self.dir = Env().getEnvValue('VIDEOS_DIRECTORY')

    def get(self) -> str:
        link = request.args.get('link') 
        cutId = request.args.get('id') 
        handler = CutsHandler(self.dir, link)    
        cuts = handler.retrievePreparedCuts()
        cut = list(filter(lambda cut: cut["id"] == int(cutId), cuts))[0]
        path = os.path.join(handler.getVideoDirectory(), cut["cutPath"].split('/')[-2], os.path.basename(cut["cutPath"]))     

        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None
        if range_header:
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]:
                byte1 = int(groups[0])
            if groups[1]:
                byte2 = int(groups[1])
        
        chunk, start, length, file_size = self.get_chunk(byte1, byte2, path)
        resp = Response(chunk, 206, mimetype='video/mp4',
                        content_type='video/mp4', direct_passthrough=True)
        resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
        return resp
    
    def get_chunk(self, byte1=None, byte2=None, path=""):

        full_path = path
        file_size = os.stat(full_path).st_size
        start = 0
        
        if byte1 < file_size:
            start = byte1
        if byte2:
            length = byte2 + 1 - byte1
        else:
            length = file_size - start

        with open(full_path, 'rb') as f:
            f.seek(start)
            chunk = f.read(length)
        
        return chunk, start, length, file_size

    def after_request(self, response):
        response.headers.add('Accept-Ranges', 'bytes')
        return response
    