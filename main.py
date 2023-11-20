from flask import Flask 
from env import Env
from services.router_service import RouterService
#import webview

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
    
    
    
