import datetime
import logging
import os

import boto3
from flask import Flask
from flask_apscheduler import APScheduler

from airquality.base import get_results

dynamo = boto3.client('dynamodb')

logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


def dynamo_put(client, device, pmi25, pmi10, recorded_at=None):
    client.put_item(
        TableName='Readings',
        Item={
            'DeviceId': {"S": device},
            'RecordedAt': {
                "S": recorded_at or datetime.datetime.now().isoformat()
            },
            'pmi2.5': {"N": str(pmi25)},
            'pmi10': {"N": str(pmi10)}
        }
    )

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

    # initialize scheduler
    scheduler = APScheduler()

    @scheduler.task('interval', id='fetch_reading', seconds=1, misfire_grace_time=900)
    def fetch_reading():
        results = get_results()
        if results:
            pm25, pm10, device_id = results
            dynamo_put(
                dynamo,
                b''.join(device_id).decode(),
                pm25,
                pm10
            )
            with scheduler.app.app_context():
                db = get_db()
                db.execute(
                    'INSERT INTO readings(pmi25, pmi10, recorded_at) '
                    'VALUES (?, ?, ?);',
                    (pm25, pm10, datetime.datetime.now())
                )
                db.commit()

    scheduler.init_app(app)
    scheduler.start()

    return app

