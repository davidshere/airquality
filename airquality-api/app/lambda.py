import json

from app.response import get_last_day_bucketed_aqi
from app.reading import write_reading

def handler(event=None, context=None):
    if event.get('httpMethod') == "POST":
        data = json.loads(event['body'])
        write_reading(
           device=data['device_id'],
           pmi25=data['pmi2.5'],
           pmi10=data['pmi10']
        )
        body = f'written {event}'
    else:
        body = json.dumps(get_last_day_bucketed_aqi())

    response = {
        'isBase64Encoded': False,
        "statusCode": 200,
        "headers": {},
        "body": body
    }
    return response