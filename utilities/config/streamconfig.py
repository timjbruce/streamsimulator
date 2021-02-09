#Not production code

import argparse
import boto3
import time

kinesis = boto3.client('kinesis')
#lambdaevent = boto3.resource('lambda')

parser = argparse.ArgumentParser()
parser.add_argument('--stream', '-s', help="Name of Stream", type=str)
parser.add_argument('--shards', '-x', help="Number of shards", type=int)


def checkStreamStatus(streamname):
    results = kinesis.describe_stream(StreamName=streamname)
    return results['StreamDescription']['StreamStatus']

def waitForStreamActive(streamname):
    status = checkStreamStatus(streamname)
    if status == 'ACTIVE':
        return True
    time.sleep(30)

def configStream(streamname, shards):
    results = kinesis.list_shards(StreamName=streamname)
    getShards = True
    totalShards = 0
    shardlist = []
    while getShards:
        for shard in results['Shards']:
            if shard['SequenceNumberRange'].get('EndingSequenceNumber') is None:
                shardlist.append(shard)
        if results.get('NextToken','') != "":
            nextToken = results['NextToken']
            results = kinesis.list_shards(StreamName=streamname, NextToken=nextToken)
        else:
            getShards = False
    #need to subtract the main shard
    totalShards = len(shardlist)
    print(f"wanted shards {shards}")
    print(f"currennt shards {totalShards}")
    print(f"{shardlist}")
    if shards > (2 * totalShards):
        #multiple increases
        print(f"Cannot increase shards by more than 2x in a single call")
        return
    if shards < (.5 * totalShards):
        print(f"Cannot decrease shards by more than 50% in a single call")
        return
    if shards == totalShards:
        print(f"nothing to do for Kinesis")
        return
    if shards > totalShards:
        #calling split
        i = 0
        while shards > totalShards:
            hashkey = str(int(((float(shardlist[i]['HashKeyRange']['EndingHashKey']) - float(shardlist[i]['HashKeyRange']['StartingHashKey']))/2) + float(shardlist[i]['HashKeyRange']['StartingHashKey'])))
            print(f"{hashkey}")
            print(f"Calling split_shard")
            response = kinesis.split_shard(StreamName=streamname,ShardToSplit=shardlist[i]['ShardId'],NewStartingHashKey=str(hashkey))
            print(f"{response}")
            print(f"Waiting for stream to be active")
            streamActive = False
            while not streamActive:
                streamActive = waitForStreamActive(streamname)
            i += 1
            totalShards += 1
    else:
        i = len(shardlist) - 1
        while shards < totalShards:
            print(f"calling merge with {shardlist[i]['ShardId']} and {shardlist[i-1]['ShardId']}")
            response = kinesis.merge_shards(StreamName=streamname,ShardToMerge=shardlist[i-1]['ShardId'],AdjacentShardToMerge=shardlist[i]['ShardId'])
            print(f"{response}")
            print(f"Waiting for stream to be active")
            streamActive = False
            while not streamActive:
                streamActive = waitForStreamActive(streamname)
            totalShards -= 1
            i -= 2
        #calling merge
    return

if __name__ == "__main__":
    args=parser.parse_args()
    configStream(args.stream, args.shards)
    print(f"Task complete")