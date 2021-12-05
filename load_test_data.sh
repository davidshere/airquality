#!/bin/bash

DATA_DIR='data/*'

for FILE in $DATA_DIR; do 
    aws dynamodb batch-write-item \
        --request-items=file:///home/david/src/airquality/$FILE \
        --endpoint-url=http://127.0.0.1:8000
done