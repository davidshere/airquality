import dataclasses
import os
from collections import defaultdict
from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key

TIME_INTERVAL_MINUTES = 20
DEV_ENVIRON_LAST_DAY = datetime.fromisoformat("2021-11-27T20:33:06")

if os.environ.get('FLASK_ENV') == 'development':
    dynamo = boto3.resource('dynamodb', endpoint_url='http://dynamodb-local:8000')
    last_day = DEV_ENVIRON_LAST_DAY
else:
    dynamo = boto3.resource('dynamo')
    last_day = datetime.now() - timedelta(days=1)

readings = dynamo.Table('Readings')

def get_last_day(resource=readings, last_day=last_day):
    if os.environ.get('FLASK_ENV') == "development":
        last_day = DEV_ENVIRON_LAST_DAY
    else:
        last_day = datetime.now() - timedelta(days=1)

    items = resource.query(
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

