import json
import os
import logging
from datetime import datetime
import traceback
import jwt


L = logging.getLogger()
L.setLevel(logging.INFO)
if int(os.getenv('DEBUG', '0')) > 0:
    L.setLevel(logging.DEBUG)


SECRET = os.getenv('SECRET', 'cvb973246g(*&^89gbn(^&$%VC*67i876bnf9nm(*)&^%B*)(bfmj99087wq6onIOIKG(*765')
JWT_REQUIRED_FIELDS = {
    'iss': os.getenv('AUTHZ_ISS', 'test-issuer'),
    'sub': None,
    'exp': None,
    'nbf': None,
    'iat': None,
    'jti': None,
}


def get_utc_timestamp(with_decimal: bool=False): 
    epoch = datetime(1970,1,1,0,0,0) 
    now = datetime.utcnow() 
    timestamp = (now - epoch).total_seconds() 
    if with_decimal: 
        return timestamp 
    return int(timestamp)


def get_jwt_payload(encoded_jwt: str)->dict:
    result = dict()
    try:
        L.info('get_jwt_payload(): encoded_jwt={}'.format(encoded_jwt))
        result = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
        L.info('get_jwt_payload(): result={}'.format(result))
    except:
        L.error('EXCEPTION: {}'.format(traceback.format_exc()))
    return result


def validate_decoded_jwt_payload(jwt_payload: dict, now: int)->bool:
    for required_field in list(JWT_REQUIRED_FIELDS.keys()):
        if required_field not in jwt_payload:
            L.error('validate_decoded_jwt_payload(): Required field "{}" not found in payload.'.format(required_field))
            return False
    L.info('validate_decoded_jwt_payload() Required field validation passes')
    if jwt_payload['iss'] != JWT_REQUIRED_FIELDS['iss']:
        L.error('validate_decoded_jwt_payload(): Expected iss value mismatched')
        return False
    L.info('validate_decoded_jwt_payload() iss validation passes')
    if now >= int(jwt_payload['exp']):
        L.error('validate_decoded_jwt_payload(): EXPIRED. exp={}   now={}'.format(jwt_payload['exp'], now))
        return False
    L.info('validate_decoded_jwt_payload() not expired')
    if int(jwt_payload['nbf']) >= now:
        L.error('validate_decoded_jwt_payload(): nbf validation failed')
        return False
    L.info('validate_decoded_jwt_payload(): nbf validation passed')
    if len(jwt_payload['sub']) < 3:
        L.error('validate_decoded_jwt_payload(): sub validation failed')
        return False
    L.info('validate_decoded_jwt_payload(): sub validation passed')
    if len(jwt_payload['jti']) < 3:
        L.error('validate_decoded_jwt_payload(): jti validation failed')
        return False
    L.info('validate_decoded_jwt_payload(): jti validation passed')
    return True


def lambda_handler(event, context):
    isAuthorized = False
    sub = None
    jti = None
    now = get_utc_timestamp()
    L.info('event={}'.format(event))
    encoded_jwt = None
    if 'headers' in event:
        if 'authorization' in event['headers']:
            encoded_jwt = event['headers']['authorization']
            if encoded_jwt.startswith('Authorization:'):
                encoded_jwt = encoded_jwt[14:]
                encoded_jwt = encoded_jwt.lstrip()
    jwt_payload = get_jwt_payload(encoded_jwt=encoded_jwt)
    if len(jwt_payload) > 0:
        if validate_decoded_jwt_payload(jwt_payload=jwt_payload, now=now):
            L.info('jwt_payload validation passed')
            isAuthorized = True
            sub = jwt_payload['sub']
            jti = jwt_payload['jti']
    return {
      "isAuthorized": isAuthorized,
      "context": {
        "sub": sub,
        "jti": jti
      }
    }
