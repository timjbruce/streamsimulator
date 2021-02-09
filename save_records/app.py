#Non production code

import base64
import boto3
from decimal import Decimal
import json
import os
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TableName'])

def lambda_handler(event, context):
    
    for record in event['Records']:
        print(record)

        payload=base64.b64decode(record['kinesis']['data'])
        TestRun = json.loads(payload)['TestRun'];
        key = time.time()
        Time = str(key);
        difference = Decimal(str(key - record['kinesis']['approximateArrivalTimestamp']))
        Item = { 'TestRun': TestRun, 'Time': Time, 'partitionKey': record['kinesis']['partitionKey'], 'data': payload, 'SequenceNumber': record['kinesis']['sequenceNumber'], 'arrivalTS': Decimal(str(record['kinesis']['approximateArrivalTimestamp'])), 'difference': difference };
        print(Item)
        table.put_item(Item=Item)
    response = { 'statusCode': 200, 'message': 'records processed' };
    return response;
