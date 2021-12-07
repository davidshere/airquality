import dataclasses
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key

from app.aqi import get_aqi, Particle
from app.connection import readings

TIME_INTERVAL_MINUTES = 20
DEV_ENVIRON_LAST_DAY = datetime.fromisoformat("2021-11-27T20:33:06")

if os.environ.get('FLASK_ENV') == 'development':
    last_day = DEV_ENVIRON_LAST_DAY
else:
    last_day = datetime.now() - timedelta(days=1)
 
 
def get_last_day(resource=readings, last_day=last_day):
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

def get_last_day_bucketed_aqi():
    results = [
        TimingResponse(
            a[0],
            get_aqi(a[1],Particle.TWO_POINT_FIVE),
            get_aqi(a[2], Particle.TEN)
        )
        for a in get_last_day()
    ]

    buckets = timing_results_to_buckets(results)
    return average_aqi_from_buckets(buckets)

