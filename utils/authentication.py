import json
import logging
import jwt
import pandas as pd

from datetime import datetime, timedelta

from utils import exceptions
from utils.constants import AuthConst, Const
from utils import generate_traceback as api_traceback

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def authenticate(jwt_token, conn):
    try:
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
    except jwt.ExpiredSignatureError as e:
        logger.error(e)
        raise jwt.ExpiredSignatureError(AuthConst.EXPIRED_TOKEN)
    except (jwt.InvalidSignatureError, jwt.DecodeError) as e:
        logger.error(e)
        raise ValueError(AuthConst.INVALID_TOKEN)

    query = f"select * from sys.username where username = {decoded_token['userId']}"
    records = pd.read_sql(query, conn)

    if len(records) == 0:
        raise ValueError(AuthConst.USER_DOES_NOT_EXIST)

    records = records.to_dict(orient='records')
    email = records[0]['email']

    return decoded_token['emailId'].lower()

def check(jwt_token, conn):
    try:
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
    except jwt.ExpiredSignatureError as e:
        logger.error(e)
        raise jwt.ExpiredSignatureError(AuthConst.EXPIRED_TOKEN)
    except (jwt.InvalidSignatureError, jwt.DecodeError) as e:
        logger.error(e)
        raise ValueError(AuthConst.INVALID_TOKEN)
        
    print(decoded_token)
    username = decoded_token['cognito:username']
    print(username)
    
    query = f"select * from sys.username where username = '{username}'"
    records = pd.read_sql(query, conn)
    print(decoded_token['email'])

    if len(records) == 0:
        data = pd.DataFrame([{
            'username': username,
            'email': decoded_token['email']
        }])
        try:
            data.to_sql(con=conn, name='username', if_exists='append', index=False)
        except:
            message = {"message": Const.DB_FAILURE}
            logger.warning(Const.DB_FAILURE)
            raise
        
    return decoded_token['email'].lower()