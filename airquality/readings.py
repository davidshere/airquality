import dataclasses
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List
from xml.etree import ElementTree

import boto3
from boto3.dynamodb.conditions import Key
from flask import (
    Blueprint, jsonify,render_template
)
import requests

from airquality.utils import get_aqi, Particle

TIME_INTERVAL_MINUTES = 20

logger = logging.getLogger(__name__)
dynamo = boto3.resource('dynamodb')
readings = dynamo.Table('Readings')
bp = Blueprint('readings', __name__)

@bp.route('/outside', methods=('GET',))
def outside():
    url = 'http://feeds.airnowapi.org/rss/realtime/98.xml'
    print(url)
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)
    print(tree)
    breakpoint()
    return ''

def get_last_day():
    last_day = datetime.now() - timedelta(days=1)

    items = readings.query(
        TableName='Readings',
        KeyConditionExpression=Key('RecordedAt').gt(last_day.isoformat()) & Key('DeviceId').eq('2A84')
    )['Items']

    items = sorted(items, key=lambda x: x['RecordedAt'])
    for res in items:
        yield datetime.fromisoformat(res['RecordedAt']), float(res['pmi2.5']), float(res['pmi10'])

@dataclasses.dataclass
class TimingResponse:
    recorded_at: datetime
    aqi_two_point_five: int
    aqi_ten: int

def timing_results_to_buckets(results):
    bucket_marker = results[0].recorded_at 
    buckets = defaultdict(list)
    for result in results:
        if result.recorded_at > bucket_marker + timedelta(
            minutes=TIME_INTERVAL_MINUTES
        ):
            bucket_marker = result.recorded_at
        buckets[bucket_marker].append(result)
    return buckets

def average_aqi_from_buckets(buckets):
    response = []
    for marker, bucket in buckets.items():
        two_point_five = [a.aqi_two_point_five for a in bucket]
        ten = [a.aqi_ten for a in bucket]
        response.append([
            marker.isoformat(),
            round(sum(two_point_five)/len(two_point_five)),
            round(sum(ten)/len(ten))
        ])
    return response

@bp.route('/series', methods=('GET',))
def series():
    results = [
        TimingResponse(
            a[0],
            get_aqi(a[1],Particle.TWO_POINT_FIVE),
            get_aqi(a[2], Particle.TEN)
        )
        for a in get_last_day()
    ]
    buckets = timing_results_to_buckets(results)
    average_aqi = average_aqi_from_buckets(buckets)
    return jsonify(average_aqi)

@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')
