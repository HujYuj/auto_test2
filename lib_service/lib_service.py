# -*- coding: utf-8 -*-
"""
    :author: Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
"""
import os, sys, logging, click
import json
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request

from utils.common import get_root_folder
root_folder = get_root_folder()
# root_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, root_folder)
print(sys.path)

from lib_service.blueprints.socket_io_service import socket_io_service_bp
from lib_service.blueprints.runner import runner_bp
from lib_service.extensions import socketio
from lib_service.config import PORT
# from nokia_5G_hwiv_configuration.utils.common_util import create_dir_if_not_exist


def start(port: str, public: bool):

    app = create_app()
    socket_io_server_url = {
        "url": f"http://localhost:{port}",
        "event": "runner_message_event"
    }

    app.config['socket_io_server_url'] = socket_io_server_url
    os.environ["socket_io_server_url"] = json.dumps(socket_io_server_url)
    host = '0.0.0.0' if public else '127.0.0.1'
    socketio.run(app, host=host, port=port)


def create_app():
    app = Flask('lib_service')

    app.config['SECRET_KEY'] = os.urandom(24)

    register_extensions(app)
    register_blueprints(app)
    # register_errors(app)

    return app


def register_extensions(app):
    socketio.init_app(app)

def register_blueprints(app):
    # csrf = CSRFProtect(app)
    app.register_blueprint(socket_io_service_bp)
    app.register_blueprint(runner_bp)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', description=e.description, code=e.code), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', description=e.description, code=e.code), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', description='Internal Server Error', code='500'), 500


def test():
    import configparser
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'ServerAliveInterval': '45',
                         'Compression': 'yes',
                         'CompressionLevel': '9'}
    config['bitbucket.org'] = {}
    config['bitbucket.org']['User'] = 'hg'
    config['topsecret.server.com'] = {}
    topsecret = config['topsecret.server.com']
    topsecret['Port'] = '50022'  # mutates the parser
    topsecret['ForwardX11'] = 'no'  # same here
    config['DEFAULT']['ForwardX11'] = 'yes'
    with open('example.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":

    start(port=PORT, public=False)

