# streamsimulator

This project contains sample source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- save_records/ - Source code to save Kinesis records to a DynamoDB
- template.yaml - A template that defines the application's AWS resources.
- utilities/eval - Source code to evaluate results of test run
- utilities/producer - Source code to send simulated data stream to Kinesis
- utilities/config - Source code to modify the environment (# of shards, Consumer Event on Lambda)

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

This application is built on python3.7 and requirements.txt files are provided for any 3rd party software that is required.

## Warranty of code

No warrantee of code is provided.  Nothing included in this project should be considered production code.

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided --stack-name streamsimulator
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

There will be two important outputs from the `sam deploy` commaond
* TestStream - the name of the Kinesis Stream created
* TestingTable - the name of the DynamoDB Table that holds your test

These two outputs will be used for the command line utilities that generate Kinesis Streams records and evaluate the results.

## Configure the Stream

The initial environment is setup with a single shard on a Kinesis Stream. You can change the Stream via the console. There is also a utility that is provided that can split and merge streams.  This is located in utilities/config.

Run the script with the command from the utilities/config directory:

`python3 streamconfig.py --stream <streamname> --shards <# of shards>`

The streamname is provided from the `sam deploy` output above as the TestingStream.  Just like the console, you can only increase the number of shards by 2x and decrease the shards by .5x at a time.  If you need larger changes, you should run this utility to reach the number you want.

**Known Issue** This utility may report errors in merging shards.  If this occurs, it is recommended to use the the console to merge the thread back to 1 shard.

## Configure the Lambda Event

The initial Lambda function event is setup with batch size of 100, no batch window, and 1 concurrent batch. There is a utility that can be used to change the event.  This is located in utlities/config.

`python3 lambdaevent.py --function <functionname> --batchsize <size of records in a batch> --consumerarn <consumerarn> --batchwindow <-1 for null or # of seconds to wait> --concurrent <# of concurrent batches>`

The functionname and consumerarn are reported via the `sam deploy` command.

## Running batch of records

The tool to run sample records is located in the utlities/producer directory. To run the batch, use:

`python3 producer.py --stream <name of stream> --records <count of records to run> --sleep <sleep in ms> --keys <# of partition keys> --testrun <name of test run> --bytes <size of message to send> --mode (normal | chaos)`

Stream is from the `sam deploy` command.  Testrun will be stored in the DynamoDB table to separate out sets of records (and used during eval).  Normal mode will use the exact settings for bytes and sleep.  Chaos will use bytes and sleep up to and including the amount sepecified.

## Evaluation

The tool to eval is in the utilities/eval directory. To run eval after a batch, use:

`python3 eval.py --testrun <test run from producer step> --table <table name for results>`

The table name for results is from the `sam deploy` command.  This step will show the # of messages sent to DynamoDB, average, min, max, mean, and a number of percentiles for the time it took to process records. It will also display a count of how many of each key was created in the run.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
streamsimulator$ sam logs -n SaveRecords --stack-name streamsimulator --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name streamsimulator
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
