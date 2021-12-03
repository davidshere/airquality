from flask_lambda import FlaskLambda
from flask import Flask
from app import create_app

import os

class MyFlask(Flask):
    def __call__(self)

os.environ['wsgi.url_scheme'] = 'http'

http_server = create_app(FlaskLambda)

if __name__ == "__main__":
    http_server.run()