from flask import render_template
from flask.views import MethodView


class AddVideoController(MethodView):

    def get(self) -> str:
        return render_template('add-video.html')        