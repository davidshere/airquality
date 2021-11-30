from flask import Flask
from airquality import create_app

http_server = create_app(Flask)

if __name__ == "__main__":
    http_server.run()