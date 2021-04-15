from flask import Blueprint,current_app, request
from flask_socketio import emit

from lib_service.extensions import socketio


socket_io_service_bp = Blueprint('socket_io_service', __name__)

@socketio.on('connect', namespace='/')
def connect():
    print(f"{request.sid} connected!!")
    current_app.logger.info("websocket connected.")

@socketio.on('disconnect', namespace='/')
def disconnect():
    print(f"{request.sid} disconnected!!")
    current_app.logger.info("websocket disconnected.")

@socketio.on('runner_message_event', namespace='/')
def runner_handleMessage(message):
    print("emit a msg!")
    emit('runner_message', message, broadcast=True, include_self=False)

@socketio.on('serial_message_event', namespace='/')
def serial_handleMessage(message):
    print("emit serial msg!")
    emit('serial_message', message, broadcast=True, include_self=False)