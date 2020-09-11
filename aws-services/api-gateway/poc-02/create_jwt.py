import jwt
from datetime import datetime
import uuid
import json
import os


API_ID = os.getenv('AWS_APIGW_ID', 'unknown')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')


def get_utc_timestamp(with_decimal: bool=False): 
    epoch = datetime(1970,1,1,0,0,0) 
    now = datetime.utcnow() 
    timestamp = (now - epoch).total_seconds() 
    if with_decimal: 
        return timestamp 
    return int(timestamp) 


SECRET = 'cvb973246g(*&^89gbn(^&$%VC*67i876bnf9nm(*)&^%B*)(bfmj99087wq6onIOIKG(*765'
TTL = 60

now = get_utc_timestamp()

payload = {
    'iss': 'test-issuer',
    'sub': '3f94876234f876hb8',
    'exp': now + TTL,
    'nbf': now,
    'iat': now,
    'jti': str(uuid.uuid1()),
}

print('Payload in JSON:\n---------------\n{}\n---------------\n'.format(json.dumps(payload, indent='  ')))

encoded_jwt = jwt.encode(payload, SECRET, algorithm='HS256').decode('utf-8')

print('encoded_jwt={}\n'.format(encoded_jwt))

print('curl test command:\n----------------------------------------\n\ncurl -vvv -X GET -H "Authorization: {}"  https://{}.execute-api.{}.amazonaws.com/dev/echo-test\n\n----------------------------------------\n'.format(encoded_jwt, API_ID, AWS_REGION))
