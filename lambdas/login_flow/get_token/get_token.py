import json
from datetime import datetime, timedelta
from os import access
from urllib import response
import requests
import jwt
import logging
import sys
import pandas as pd

from utils.authentication import check
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
    code = event["queryStringParameters"]["code"]
    endpoint = "https://auth.quester.live/oauth2/token/"
    data = {'grant_type': 'authorization_code', 'redirect_uri': 'https://api.quester.live/get-token/',
            'client_id': '3qisa8j0tgq6ng8447kglcltsh', 'code': code}
    try:
        request = requests.post(url=endpoint, data=data)
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.EXT_API_FAILURE}
        logger.warning(Const.EXT_API_FAILURE)

    data = request.json()
    id_token = data['id_token']
    access_token = data['access_token']

    try:
        email = check(id_token, conn)
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.DB_FAILURE}
        logger.warning(Const.DB_FAILURE)
        return api_response.generate_response(status_code=500, response_body=message)

    query = f"select * from sys.users where email = '{email}'"

    try:
        data = pd.read_sql(query, conn)
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.DB_FAILURE}
        logger.warning(Const.DB_FAILURE)
        return api_response.generate_response(status_code=500, response_body=message)

    expires = (datetime.utcnow() + timedelta(minutes=60)).strftime("%a, %d %b %Y %H:%M:%S GMT")  # expires in 1 minute
    common_cookie_str = f'expires={expires};'
    new_user = False

    role = 'teacher'
    if 'nmims.edu.in' in email:
        role = 'student'

    if len(data.index) == 0:
        new_user = True

    return api_response.generate_response(status_code=302, response_body={'success': True},
                                          location=f"http://localhost:3000/login?onboardingStatus=successful&accessToken={access_token}&email={email}&new={new_user}&role={role}",
                                          cookies={
                                              "Set-Cookie": [
                                                  f'accessToken={access_token};{common_cookie_str}',
                                                  f'id_token={id_token};{common_cookie_str}',
                                                  f'email={email};{common_cookie_str}',
                                                  f'new_user={new_user};{common_cookie_str}'
                                              ]
                                          }
                                          )
