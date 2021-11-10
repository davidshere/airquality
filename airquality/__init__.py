import os

from flask import Flask
from flask_apscheduler import APScheduler

from airquality.base import get_results
from airquality.db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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

    from . import db
    db.init_app(app)

    from . import readings
    app.register_blueprint(readings.bp)

    # initialize scheduler
    scheduler = APScheduler()

    @scheduler.task('interval', id='fetch_reading', seconds=5, misfire_grace_time=900)
    def fetch_reading():
        results = get_results()
        print(results)
        if results:
            pm25, pm10, _ = results
            with scheduler.app.app_context():
                db = get_db()
                db.execute(
                    'INSERT INTO readings(pmi25, pmi10) '
                    'VALUES (?, ?);',
                    (pm25, pm10)
                )
                db.commit()

    scheduler.init_app(app)
    scheduler.start()

    return app

