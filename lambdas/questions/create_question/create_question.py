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
import create_question_helper as helper
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
    
    query = f'select * from sys.users where email = {email}'
    
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
    

    questions = body['questions']
    access = body['accessBy']
    secret = body['secret']
    
    result = user.to_dict('records')
    if result[0]['role'] == 'student':
        message = {"message": Const.INVALID_USER}
        return api_response.generate_response(status_code=404, response_body=message)
    
    session = pd.DataFrame([{
        'user_id': user_id,
        'access_by': access,
        'secret': secret,
    }])

    try:
        session.to_sql('sys.sessions', conn, if_exists='append', index=False)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    for question in questions:
        question_sql = pd.DataFrame([{
        'choice_1': question.get('choice1'),
        'choice_2': question.get('choice2'),
        'choice_3': question.get('choice3', None),
        'choice_4': question.get('choice4', None),
        'correct_ans': question.get('correctAns'),
        'description': question.get('description'),
        'session_id': session['session_id'].iloc[0],
        'tag': question.get('tag', None),
        'time': question.get('time', None)
        }])
        try:
            question_sql.to_sql('sys.questions', conn, if_exists='append', index=False)
        except:
            message = {"message": Const.DB_FAILURE}
            return api_response.generate_response(status_code=500, response_body=message)
    
    message = {"message": "success"}

    return api_response.generate_response(status_code=200, response_body=message)