#Not production code

import argparse
import boto3
import time

lambdaclient = boto3.client('lambda')

parser = argparse.ArgumentParser()
parser.add_argument('--function', '-f', help="Name of function", type=str)
parser.add_argument('--consumerarn', '-a', help="Stream consumer Arn", type=str)
parser.add_argument('--batchsize', '-b', help="Batch Size", type=int)
parser.add_argument('--batchwindow', '-w', help="Batch Window", type=int)
parser.add_argument('--concurrent', '-c', help="Concurrent Batches per Shard", type=int)

def getFunctionActive(function):
    active = False
    while not active:
        response = lambdaclient.get_function(FunctionName=function, Qualifier="TESTING")
        if response['Configuration']['State'] == 'Active':
            print("Function is active")
            active = True
        else:
            time.sleep(20)

def deleteEventSourceMappings(function, consumerarn):
    print('Getting event source mappings')
    functionfull = function + ":TESTING"
    response = lambdaclient.list_event_source_mappings(FunctionName=functionfull)
    for mapping in response['EventSourceMappings']:
        print(f"Deleting Mapping {mapping['UUID']}")
        response = lambdaclient.delete_event_source_mapping(UUID=mapping['UUID'])
        time.sleep(10)

def createNewEventSourceMapping(function, consumerarn, batchsize, batchwindow, concurrent):
    print('Creating new source mapping')
    functionfull = function + ":TESTING"
    if batchwindow==-1:
        response = lambdaclient.create_event_source_mapping(EventSourceArn=consumerarn,FunctionName=functionfull,Enabled=True,BatchSize=batchsize,ParallelizationFactor=concurrent,StartingPosition='LATEST')
    else:
        response = lambdaclient.create_event_source_mapping(EventSourceArn=consumerarn,FunctionName=functionfull,Enabled=True,BatchSize=batchsize,ParallelizationFactor=concurrent,StartingPosition='LATEST',MaximumBatchingWindowInSeconds=batchwindow)
    print(response)
    enabled = False
    while not enabled:
        time.sleep(10)
        response = lambdaclient.list_event_source_mappings(FunctionName=functionfull)
        if response['EventSourceMappings'][0]['State']=='Enabled':
            enabled = True
    print('New source mapping setup')
    return

def configFunctionTrigger(function, consumerarn, batchsize, batchwindow, concurrent):
    getFunctionActive(function)
    deleteEventSourceMappings(function, consumerarn)
    createNewEventSourceMapping(function, consumerarn, batchsize, batchwindow, concurrent)
    
if __name__ == "__main__":
    args=parser.parse_args()
    configFunctionTrigger(args.function, args.consumerarn, args.batchsize, args.batchwindow, args.concurrent)