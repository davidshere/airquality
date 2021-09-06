import os

from flask import Flask

from airquality.sensor import get_pmi_result

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'airquality.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simplepage that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def get_pmi():
        two_point_five, ten = get_pmi_result()
        return f"PMI 2.5: {two_point_five}, PMI 10: {ten}\n"

    from . import db
    db.init_app(app)

    from . import readings
    app.register_blueprint(readings.bp)

    return app

