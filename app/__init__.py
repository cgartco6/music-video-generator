from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from app import main
