from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def create_app(test_config=None):
    app = Flask(__name__)

    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        return jsonify(status=str(e)), code

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_pyfile('test_config.py')

    from app.database import config_redis
    redis_client = config_redis(test_config)
    redis_client.init_app(app)
    app.redis = redis_client

    from . import api
    app.register_blueprint(api.links)

    return app
