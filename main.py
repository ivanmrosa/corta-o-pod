from flask import Flask 
from env import Env
from services.router_service import RouterService

#sometimes is needed to change cipher.py to another regex

from pytube. innertube import _default_clients

_default_clients[ "ANDROID"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients[ "ANDROID_EMBED"][ "context"][ "client"]["clientVersion"] = "19.08.35"
_default_clients[ "IOS_EMBED"][ "context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"][ "context"]["client"]["clientVersion"] = "6.41"
_default_clients[ "ANDROID_MUSIC"] = _default_clients[ "ANDROID_CREATOR" ]


dir = Env().getEnvValue('VIDEOS_DIRECTORY')
app = Flask(__name__, template_folder='views')

router = RouterService()
router.configure_routes(app)


def start_server():
    app.run(host='0.0.0.0', debug=False, port=8080)
    #app.run()



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)        
    
    # t = threading.Thread(target=start_server)
    # t.daemon = True
    # t.start()
  
    # webview.create_window("Corta o Pod", "http://127.0.0.1:8080", width=1080, height=1024)
    # webview.start(gui='qt')
    # sys.exit()    
    
    
    
