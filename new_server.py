from flask import Flask, request, jsonify, after_this_request
from detect import *
import requests

# '192.168.4.107'
URL = 'http://192.168.4.1/'
app = Flask(__name__)



@app.route("/image", methods = ['GET'])
def love():
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    if(dola):
        return 'done'
    else:
        return 'notdone'

@app.route("/image", methods = ['POST'])
def home():
    # confirm = True
    dola = False
    if(not dola):
        print('IN post req')
        data = request.json
        direction= main_prog(data['base64'])
        print(direction)
        if(dola):
            r = requests.get(url = URL+ direction)
            print(r)
        return 'done'
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    


    
if __name__ == "__main__":
    # confirm = 0
    app.run(host="0.0.0.0", port=5000, debug=True)
