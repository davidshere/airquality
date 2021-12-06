import os

import boto3

parameters = {'service_name': 'dynamodb'}
if os.environ.get('FLASK_ENV') == "development":
    parameters['endpoint_url'] = 'http://dynamodb-local:8000'

client = boto3.client(**parameters)
resource = boto3.resource(**parameters)
readings = resource.Table('Readings')