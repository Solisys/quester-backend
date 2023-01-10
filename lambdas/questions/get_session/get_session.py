import json
from os import access
import secrets
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
import get_session_helper as helper
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

    if isinstance(event.get("body"), type(None)) or not event.get("body"):
        message = {
            "message": f"Payload missing in the input"
        }
        logger.warning(message.get("message"))
        return api_response.generate_response(status_code=400, response_body=message)

    else:
        body = json.loads(event.get("body", dict()))
        result = helper.validate_payload(body)
        if result != "valid":
            logger.info("Input payload is invalid")
            logger.debug(result)
            return api_response.generate_response(status_code=400, response_body=result)

    secret = body['secret']

    result = user.to_dict('records')
    if result[0]['role'] == 'teacher':
        message = {"message": Const.INVALID_USER}
        return api_response.generate_response(status_code=404, response_body=message)

    query = f'select * from sys.students where user_id = {user_id}'
    try:
        user = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    user = user.to_dict('records')
    class_id = user[0]['class_id']

    query = f'select * from sys.sessions where secret = "{secret}" and access_by = {class_id}'

    try:
        session = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if session.empty:
        message = {"message": Const.NO_RESPONSES}
        return api_response.generate_response(status_code=401, response_body=message)

    session = session.to_dict('records')
    session_id = session[0]['session_id']

    query = f'select * from sys.responses where user_id = {user_id} and question_id in (select question_id from ' \
            f'sys.questions where session_id = {session_id})'

    try:
        responses = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if not responses.empty:
        message = {"message": Const.RECORD_PRESENT}
        return api_response.generate_response(status_code=409, response_body=message)

    query = f'select * from sys.questions where session_id = {session_id}'

    try:
        questions = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    questions = questions.to_dict('records')

    questions = {"questions": questions}

    return api_response.generate_response(status_code=200, response_body=questions)
