from flask import Flask
from app import create_app

http_server = create_app(Flask)

if __name__ == "__main__":
    http_server.run()