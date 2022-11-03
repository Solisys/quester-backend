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
from utils.authentication import authenticate

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
    jwt_token = event.get("headers").get("Authorization").split('Bearer ')[1]

    try:
        email = authenticate(jwt_token, conn)
        print('done')
    except Exception as e:
        message = {"message": str(e)}
        return api_response.generate_response(status_code=401, response_body=message)

    query = f'select * from sys.users where email = "{email}"'

    try:
        user = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if user.empty:
        message = {"message": Const.INVALID_USER}
        return api_response.generate_response(status_code=404, response_body=message)

    result = user.to_dict('records')
    user_id = result[0]['user_id']

    query = f'select sessions.secret, sessions.created_on, class.stream, class.year from sys.sessions join sys.class ' \
            f'on class.class_id = sessions.access_by where sessions.user_id = {user_id}'

    try:
        sessions = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if sessions.empty:
        message = {"message": Const.NO_RESPONSES}
        return api_response.generate_response(status_code=404, response_body=message)

    result = sessions.to_dict('records')

    return api_response.generate_response(status_code=200, response_body=result)
