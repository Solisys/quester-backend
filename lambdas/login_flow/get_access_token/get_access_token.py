import json
from os import access
from urllib import response
import requests 
import jwt
import logging
import sys
import pandas as pd

from sqlalchemy import create_engine
from utils.constants import Const
from utils import generate_response as api_response
from utils import generate_traceback as api_traceback
from utils.global_config import AuthConfig

rds_host = AuthConfig.database['rds_host']
user_name = AuthConfig.database['user_name']
password = AuthConfig.database['password']
db_name = AuthConfig.database['db_name']

logger = logging.getLogger()
logger.setLevel(10)

try:
    conn = create_engine(f'mysql+pymysql://{user_name}:{password}@{rds_host}/{db_name}')
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    sys.exit()


def lambda_handler(event, context):

    code=event["queryStringParameters"]["code"]
    endpoint = "https://auth.quester.live/oauth2/token/"
    data={'grant_type':'authorization_code', 'redirect_uri':'https://api.quester.live/get-token/','client_id':'3qisa8j0tgq6ng8447kglcltsh','code':code}
    try:
        request = requests.post(url = endpoint, data = data)
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.EXT_API_FAILURE}
        logger.warning(Const.EXT_API_FAILURE)
        
    data=request.json()
    id_token = data['id_token']
    access_token = data['access_token']
    decode = jwt.decode(id_token, options={"verify_signature": False})
    
    email = decode['email']

    query = f"select * from sys.users where email = '{email}'"
    
    print(query)
    try:
        data = pd.read_sql(query, conn)
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.DB_FAILURE}
        logger.warning(Const.DB_FAILURE)
        return api_response.generate_response(status_code=500, response_body=message)


    response = {'access_token': access_token, 'id_token': id_token, 'email': email, 'new_user': False}

    if len(data.index) == 0:
        response['new_user'] = True
    

    return api_response.generate_response(status_code=200, response_body=response)


