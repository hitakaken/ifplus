# -*- coding: utf-8 -*-
from flask import Flask
import settings
from flask_cors import CORS
from ifplus import Application

app = Flask(__name__)
app.config.from_object(settings)
cors = CORS(app=app)
server = Application(app=app)


@app.before_first_request
def start():
    app.tokens.init_mongodb()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
