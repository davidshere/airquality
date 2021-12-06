import datetime

from app.connection import client


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

def write_reading(device, pmi25, pmi10):
    dynamo_put(client, device, pmi25, pmi10)