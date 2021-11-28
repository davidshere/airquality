import logging
import os

from flask import Flask


logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='/home/pi/src/airquality/airquality-ui/build/',
        static_folder='/home/pi/src/airquality/airquality-ui/build/static/'
    )
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'airquality.sqlite'),
        SCHEDULER_API_ENABLED=True,
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

    from . import readings
    app.register_blueprint(readings.bp)

    return app

