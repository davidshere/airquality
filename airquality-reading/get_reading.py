import datetime
import time

import boto3
from apscheduler.schedulers.background import BackgroundScheduler

from base import get_results

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
def fetch_and_write_reading():
    dynamo = boto3.client('dynamodb')
    results = get_results()
    if results:
        print(results, time.time())
        pm25, pm10, device_id = results
        dynamo_put(
            dynamo,
            b''.join(device_id).decode(),
            pm25,
            pm10
        )

if __name__ == "__main__":

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_write_reading, 'interval', seconds=5)
    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()