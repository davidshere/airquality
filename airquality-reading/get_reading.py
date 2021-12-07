import datetime
import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from base import get_results

API_URL = "https://3kwkbo4z21.execute-api.us-west-2.amazonaws.com/serverless_lambda_stage/data"

def write_result(device, pmi25, pmi10, recorded_at=None):
    return requests.post(
        API_URL,
        json={
            'device_id': device,
            'pmi2.5': pmi25,
            'pmi10': pmi10
        }
    )

def fetch_and_write_reading():
    results = get_results()
    if results:
        print(results, time.time())
        pm25, pm10, device_id = results
        resp = write_result(
            b''.join(device_id).decode(),
            pm25,
            pm10
        )
        print(resp)

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