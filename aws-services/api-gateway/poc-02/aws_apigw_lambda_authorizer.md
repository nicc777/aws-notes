
- [Introduction](#introduction)
- [Proof of Concept Design](#proof-of-concept-design)
- [Preparing for Distribution](#preparing-for-distribution)
- [Source Code](#source-code)
  - [The `echo-test` Lambda Function](#the-echo-test-lambda-function)
  - [The `test-apigw-authorizer` Lambda Function](#the-test-apigw-authorizer-lambda-function)
- [API Gateway Setup](#api-gateway-setup)
- [Testing](#testing)
  - [Command Line Testing](#command-line-testing)
  - [Examining the Logs](#examining-the-logs)
    - [The API Gateway Log Entry](#the-api-gateway-log-entry)
    - [Authorization Lambda Log Entry](#authorization-lambda-log-entry)
    - [Test Lambda BAckend Log Entry](#test-lambda-backend-log-entry)
- [Key Takeaways](#key-takeaways)

# Introduction

The idea is to test the basic functionality of an AWS API Gateway Lambda Authorizer.

This proof of concepts builds on the [previous one](../poc-01/aws_apigw_lambda_authorizer.md), but adds the [`PyJWT`](https://pyjwt.readthedocs.io/en/latest/) module in order to create a JWT (from the command line) that we can use to test a scenario whereby the decoded and validated JWT values are passed in context variables which in turn will be visible to the backend Lambda function.

A typical use case will be to pass a user identifier (UID) - or the `sub` in the JWT - so that the backend can use it in subsequent queries related to the authenticated user. The identity is trusted based on the validation of the JWT.

It is important that the secret used to create the JWT is also the same secret used to validate the JWT.

The `PyJWT` module will validate the JWT signature expiry and `aud` values. In the Authorizer Lambda function, I still checked the expiry just to be sure, but you should not check the `aud` or else you may run into an exception - leave it up to the `PyJWT` module.

References:

* [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)

# Proof of Concept Design

![poc-design](aws_authorizer.png)

# Preparing for Distribution

In order to package the Lambda functions for your use, you will need to run a couple of commands to create the final ZIP files. You could also just use the supplied ZIP files, which is based on the AWS Python 3.8 runtime.

The packages are required since we deploy the `PyJWT` package with the Authorizer.

References:

* [AWS Lambda deployment package in Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

# Source Code

## The `echo-test` Lambda Function

I re-used the Lambda function from `poc-01` (see [the README](../poc-01/aws_apigw_lambda_authorizer.md)).

## The `test-apigw-authorizer` Lambda Function

This is the Lambda Authorizer that we will be linking to from the API Gateway

Refer to the code in the `aws-services/api-gateway/poc-02/lambda-functions/test_apigw_authorizer/test_apigw_authorizer2.py` file. Use the ZIP file `aws-services/api-gateway/poc-02/lambda-functions/test_apigw_authorizer/test_apigw_authorizer2.zip` to upload to AWS

Keep in mind that the set-up assumes a version 2.0 for the incoming and response messages. 

The response follows a `Simple Response` message format.

References:

* [Working with AWS Lambda authorizers for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html)
* [AWS Lambda deployment package in Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)

# API Gateway Setup

I re-used the API from `poc-01` (see [the README](../poc-01/aws_apigw_lambda_authorizer.md)) and the only change you need to make is to link the new Authorizer.

# Testing

## Command Line Testing

First, set the environment variable `AWS_APIGW_ID` to the AWS API Gateway ID for your environment:

```bash
$ export AWS_APIGW_ID=xxxxxxxx
```

If you are NOT using AWS region `us-east-1` you can also set the environment variable `AWS_REGION` to suite your needs.

**Note**: You may need to make a small change to `aws-services/api-gateway/poc-02/create_jwt.py` if you are using a custom domain.

Now you can run the script `aws-services/api-gateway/poc-02/create_jwt.py` that will create the correct `curl` command for you, which you can run in turn:

A simple `curl` test:

```bash
$ python3 aws-services/api-gateway/poc-02/create_jwt.py
Payload in JSON:
---------------
{
  "iss": "test-issuer",
  "sub": "3f94876234f876hb8",
  "exp": 1599837804,
  "nbf": 1599837744,
  "iat": 1599837744,
  "jti": "97eb04e6-f442-11ea-9219-acde48001122"
}
---------------

encoded_jwt=xxxxxxxxxx.xxxxxxxxxxx.xxxxxxxxxxx

curl test command:
----------------------------------------

curl -vvv -X GET -H "Authorization: xxxxxxxxxx.xxxxxxxxxxx.xxxxxxxxxxx"  https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/echo-test

----------------------------------------
```

## Examining the Logs

The various AWS CloudWatch log entries reflecting the test above can be seen in this section

### The API Gateway Log Entry

```json
{
    "requestId": "StQNhguioAMEM8w=",
    "ip": "165.73.110.75",
    "requestTime": "11/Sep/2020:15:12:48 +0000",
    "httpMethod": "GET",
    "routeKey": "GET /echo-test",
    "status": "200",
    "protocol": "HTTP/1.1",
    "responseLength": "20",
    "authzLatency": "-",
    "integrationLatency": "72",
    "integrationRequestId": "221fce37-8c97-4d77-a536-b67390c73f26"
}
```

### Authorization Lambda Log Entry

```text
START RequestId: 3e15f9e9-f83e-4fa1-8979-d60a9cc27be2 Version: $LATEST
[INFO]	2020-09-11T15:25:50.934Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	event={'version': '2.0', 'type': 'REQUEST', 'routeArn': 'arn:aws:execute-api:us-east-1:342872205792:66j88og9x3/dev/GET', 'identitySource': ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0ZXN0LWlzc3VlciIsInN1YiI6IjNmOTQ4NzYyMzRmODc2aGI4IiwiZXhwIjoxNTk5ODM4MDA1LCJuYmYiOjE1OTk4Mzc5NDUsImlhdCI6MTU5OTgzNzk0NSwianRpIjoiMTAwZTkwYzgtZjQ0My0xMWVhLWExZDItYWNkZTQ4MDAxMTIyIn0.X_gv9mb_65IHKCgjvZ3ArxzhGC2sHvalZ3zRCaH-0kk'], 'routeKey': 'GET /echo-test', 'rawPath': '/dev/echo-test', 'rawQueryString': '', 'headers': {'accept': '*/*', 'authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0ZXN0LWlzc3VlciIsInN1YiI6IjNmOTQ4NzYyMzRmODc2aGI4IiwiZXhwIjoxNTk5ODM4MDA1LCJuYmYiOjE1OTk4Mzc5NDUsImlhdCI6MTU5OTgzNzk0NSwianRpIjoiMTAwZTkwYzgtZjQ0My0xMWVhLWExZDItYWNkZTQ4MDAxMTIyIn0.X_gv9mb_65IHKCgjvZ3ArxzhGC2sHvalZ3zRCaH-0kk', 'content-length': '0', 'host': '66j88og9x3.execute-api.us-east-1.amazonaws.com', 'user-agent': 'curl/7.64.1', 'x-amzn-trace-id': 'Root=1-5f5b96fe-6040fee4c98d64bca45ac7b8', 'x-forwarded-for': '165.73.110.75', 'x-forwarded-port': '443', 'x-forwarded-proto': 'https'}, 'requestContext': {'accountId': '342872205792', 'apiId': '66j88og9x3', 'domainName': '66j88og9x3.execute-api.us-east-1.amazonaws.com', 'domainPrefix': '66j88og9x3', 'http': {'method': 'GET', 'path': '/dev/echo-test', 'protocol': 'HTTP/1.1', 'sourceIp': '165.73.110.75', 'userAgent': 'curl/7.64.1'}, 'requestId': 'StSH2g17IAMEMSg=', 'routeKey': 'GET /echo-test', 'stage': 'dev', 'time': '11/Sep/2020:15:25:50 +0000', 'timeEpoch': 1599837950905}}
[INFO]	2020-09-11T15:25:50.934Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	get_jwt_payload(): encoded_jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0ZXN0LWlzc3VlciIsInN1YiI6IjNmOTQ4NzYyMzRmODc2aGI4IiwiZXhwIjoxNTk5ODM4MDA1LCJuYmYiOjE1OTk4Mzc5NDUsImlhdCI6MTU5OTgzNzk0NSwianRpIjoiMTAwZTkwYzgtZjQ0My0xMWVhLWExZDItYWNkZTQ4MDAxMTIyIn0.X_gv9mb_65IHKCgjvZ3ArxzhGC2sHvalZ3zRCaH-0kk
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	get_jwt_payload(): result={'iss': 'test-issuer', 'sub': '3f94876234f876hb8', 'exp': 1599838005, 'nbf': 1599837945, 'iat': 1599837945, 'jti': '100e90c8-f443-11ea-a1d2-acde48001122'}
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload() Required field validation passes
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload() iss validation passes
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload() not expired
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload(): nbf validation passed
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload(): sub validation passed
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	validate_decoded_jwt_payload(): jti validation passed
[INFO]	2020-09-11T15:25:50.935Z	3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	jwt_payload validation passed
END RequestId: 3e15f9e9-f83e-4fa1-8979-d60a9cc27be2
REPORT RequestId: 3e15f9e9-f83e-4fa1-8979-d60a9cc27be2	Duration: 2.33 ms	Billed Duration: 100 ms	Memory Size: 128 MB	Max Memory Used: 54 MB	
```

### Test Lambda BAckend Log Entry

```text
START RequestId: a21d5f82-b49a-4183-aeef-acb7c919c4be Version: $LATEST
[INFO]	2020-09-11T15:25:51.178Z	a21d5f82-b49a-4183-aeef-acb7c919c4be	event={'version': '2.0', 'routeKey': 'GET /echo-test', 'rawPath': '/dev/echo-test', 'rawQueryString': '', 'headers': {'accept': '*/*', 'authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ0ZXN0LWlzc3VlciIsInN1YiI6IjNmOTQ4NzYyMzRmODc2aGI4IiwiZXhwIjoxNTk5ODM4MDA1LCJuYmYiOjE1OTk4Mzc5NDUsImlhdCI6MTU5OTgzNzk0NSwianRpIjoiMTAwZTkwYzgtZjQ0My0xMWVhLWExZDItYWNkZTQ4MDAxMTIyIn0.X_gv9mb_65IHKCgjvZ3ArxzhGC2sHvalZ3zRCaH-0kk', 'content-length': '0', 'host': '66j88og9x3.execute-api.us-east-1.amazonaws.com', 'user-agent': 'curl/7.64.1', 'x-amzn-trace-id': 'Root=1-5f5b96fe-6040fee4c98d64bca45ac7b8', 'x-forwarded-for': '165.73.110.75', 'x-forwarded-port': '443', 'x-forwarded-proto': 'https'}, 'requestContext': {'accountId': '342872205792', 'apiId': '66j88og9x3', 'authorizer': {'lambda': {'jti': '100e90c8-f443-11ea-a1d2-acde48001122', 'sub': '3f94876234f876hb8'}}, 'domainName': '66j88og9x3.execute-api.us-east-1.amazonaws.com', 'domainPrefix': '66j88og9x3', 'http': {'method': 'GET', 'path': '/dev/echo-test', 'protocol': 'HTTP/1.1', 'sourceIp': '165.73.110.75', 'userAgent': 'curl/7.64.1'}, 'requestId': 'StSH2g17IAMEMSg=', 'routeKey': 'GET /echo-test', 'stage': 'dev', 'time': '11/Sep/2020:15:25:50 +0000', 'timeEpoch': 1599837950905}, 'isBase64Encoded': False}
END RequestId: a21d5f82-b49a-4183-aeef-acb7c919c4be
REPORT RequestId: a21d5f82-b49a-4183-aeef-acb7c919c4be	Duration: 1.69 ms	Billed Duration: 100 ms	Memory Size: 128 MB	Max Memory Used: 52 MB	Init Duration: 133.70 ms	
```

# Key Takeaways

You will notice the `jti` and `sub` values have also been passed to the back-end as these have been set from the authorizer. The `sub` represent the identity or reference to an entity that was authorized. You should be able to use this to lookup a user if need be.



