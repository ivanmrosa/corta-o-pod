from flask import Response, render_template, request
from flask.views import MethodView
from env import Env


class ConfigurationController(MethodView):
    def __init__(self) -> None:
        super().__init__()
        self.env = Env()
        self.dir = self.env.getEnvValue('VIDEOS_DIRECTORY')

    def get(self) -> Response:
        self.env.loadAttributes()
        return render_template('configuration.html', data=self.env.getKeyValueAttributes())
    
    def post(self) -> str:
        data = request.form
        print(data)
        self.env.saveConfig(data)        
        return render_template('configuration.html', data=self.env.getKeyValueAttributes())