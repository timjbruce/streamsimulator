#Non production code

import argparse
import boto3
import json
import random
from string import ascii_letters
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--stream', '-s', help="Name of Kinesis Stream", type=str)
parser.add_argument('--records', '-r', help="Number of records to send", type=int)
parser.add_argument('--sleep', '-z', help="Number of milliseconds to wait between sends", type=int)
parser.add_argument('--keys', '-k', help="Number of partition keys to use", type=int)
parser.add_argument('--testrun', '-t', help="Name of test run", type=str)
parser.add_argument('--bytes', '-b', help="Size of record to send", type=int)
parser.add_argument('--mode', '-m', help="Mode of run (normal or chaos)", type=str, default='normal')

random.seed()

kinesis = boto3.client('kinesis')

def getRandomInt(max):
    return random.randint(1, max)
    
def getMsgString(remaining, mode):
    if mode=='normal':
        return "".join(random.choice(ascii_letters) for i in range(remaining))
    else:
        return "".join(random.choice(ascii_letters) for i in range(getRandomInt(remaining)))

def timewait(msToSleep, mode):
    if mode=='normal':
        time.sleep(msToSleep/1000)
    else:
        time.sleep(getRandomInt(msToSleep)/1000)

def writeRecords(stream, testrun, records, recordsize, keys, sleep, mode):
    x = range(0, records)
    basemsgsize = len(json.dumps({'TestRun':testrun, 'message':''}))
    remaining = recordsize - basemsgsize
    for i in x:
        data = {}
        data['TestRun']=testrun
        data['message']=getMsgString(remaining, mode)
        partition = f"partition-{getRandomInt(keys)}" 
        result = kinesis.put_record(StreamName = stream, Data = json.dumps(data), PartitionKey=partition)
        #print(result)
        print(f"Record {i} sent", end="\r", flush=True)
        timewait(sleep, mode)

if __name__ == "__main__":
    args=parser.parse_args()
    print(f"Running test: {args.testrun} with {args.records} records of up to {args.bytes} bytes, {args.keys} keys, wait time {args.sleep}.  Stream is {args.stream}. Mode is {args.mode}")
    writeRecords(args.stream, args.testrun, args.records, args.bytes, args.keys, args.sleep, args.mode)
    print("Test complete")