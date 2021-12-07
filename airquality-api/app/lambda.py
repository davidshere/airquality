import json

from app.response import get_last_day_bucketed_aqi
from app.reading import write_reading

def handler(event=None, context=None):
    print('event', event)
    print('context', context)

    response = {
        'isBase64Encoded': False,
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(get_last_day_bucketed_aqi())
    }
    return response