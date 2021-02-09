#Non production code

import argparse
import boto3
from collections import Counter
import json
from boto3.dynamodb.conditions import Key
import numpy as np
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--table', '-t', help="Name of DynamoDB Table", type=str)
parser.add_argument('--testrun', '-r', help="Name of TestRun", type=str)

ddb = boto3.resource('dynamodb')
table = ddb.Table('TestResults')
diffArr = []
keyArr = []

def GetRecords(testrun, nextKey):
    if nextKey=='':
        results = table.query(ProjectionExpression='difference, partitionKey', KeyConditionExpression=Key('TestRun').eq(testrun))
    else:
        results = table.query(ProjectionExpression='difference, partitionKey', KeyConditionExpression=Key('TestRun').eq(testrun), ExclusiveStartKey=nextKey)
    return results

def evalRun(table, testrun):
    getRecords = True
    nextKey = ''
    while getRecords:
        results = GetRecords(testrun, nextKey)
        for record in results['Items']:
            diffArr.append(float(record['difference']))
            keyArr.append(record['partitionKey'])
        if results.get('LastEvaluatedKey'):
            nextKey=results['LastEvaluatedKey']
        else:
            getRecords = False
    if len(diffArr) == 0:
        print('No records found')
        return
    sorted = np.sort(diffArr);
    print(testrun)
    print(f'{np.size(sorted)} messages')
    print(f'average - {np.average(sorted)}')
    print(f'minimum - {np.amin(sorted)}')
    print(f'maximum - {np.amax(sorted)}')
    print(f'mean - {np.mean(sorted)}')
    percentiles = np.percentile(sorted, [25, 50, 75, 90, 95, 99])
    print(f'25th - {percentiles[0]}')
    print(f'50th - {percentiles[1]}')
    print(f'75th - {percentiles[2]}')
    print(f'90th - {percentiles[3]}')
    print(f'95th - {percentiles[4]}')
    print(f'99th - {percentiles[5]}')
    print('key distribution')
    print(f'{Counter(keyArr)}')

if __name__ == "__main__":
    args=parser.parse_args()
    evalRun(args.table, args.testrun)
