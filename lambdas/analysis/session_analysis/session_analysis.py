import json
from os import access
import secrets
from urllib import response
import requests 
import jwt
import logging
import sys
import pandas as pd
import numpy as np

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

    if result[0]['role'] == 'student':
        message = {"message": Const.INVALID_USER}
        return api_response.generate_response(status_code=404, response_body=message)

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
    tag = body['tag']

    query = f"select * from sys.sessions where secret = '{secret}'"

    try:
        session = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)
    
    if session.empty:
        message = {"message": Const.INVALID_SESSION}
        return api_response.generate_response(status_code=404, response_body=message)

    session_id = session['session_id'].values[0]

    if tag:
        query = f"select questions.tag, responses.correct_answer, count(responses.correct_answer) as count, avg(responses.time) as time from sys.responses left join sys.questions on responses.question_id = questions.question_id where questions.session_id = {session_id} group by questions.tag, responses.correct_answer"
    else:
        query = f"select questions.description, responses.correct_answer, count(responses.correct_answer) as count, avg(responses.time) as time from sys.responses left join sys.questions on responses.question_id = questions.question_id where questions.session_id = {session_id} group by responses.question_id, responses.correct_answer"

    try:
        responses = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)
    
    if responses.empty:
        message = {"message": Const.NO_RESPONSES}
        return api_response.generate_response(status_code=404, response_body=message)

    if tag:
        tags = list(responses['tag'].unique())
        data = pd.DataFrame()
        for tag in tags:
            temp = pd.DataFrame([question], columns=['tag'])
            temp['correct'] = int(responses[(responses['tag'] == tag) & (responses['correct_answer'] == 1)]['count'])
            temp['incorrect'] = int(responses[(responses['tag'] == tag) & (responses['correct_answer'] == 0)]['count'])
            temp['correct_time'] = int(responses[(responses['tag'] == tag) & (responses['correct_answer'] == 1)]['time'])
            temp['incorrect_time'] = int(responses[(responses['tag'] == tag) & (responses['correct_answer'] == 0)]['time'])
            temp['count'] = temp['correct'] + temp['incorrect']
            temp['avg_time'] = (temp['correct'] * temp['correct_time'] + temp['incorrect'] * temp['incorrect_time'])/temp['count']
            data = pd.concat([data, temp])
    else:
        questions = list(responses['description'].unique())
        data = pd.DataFrame()
        for question in questions:
            temp = pd.DataFrame([question], columns=['question'])
            temp['correct'] = int(responses[(responses['description'] == question) & (responses['correct_answer'] == 1)]['count'])
            temp['incorrect'] = int(responses[(responses['description'] == question) & (responses['correct_answer'] == 0)]['count'])
            temp['correct_time'] = int(responses[(responses['description'] == question) & (responses['correct_answer'] == 1)]['time'])
            temp['incorrect_time'] = int(responses[(responses['description'] == question) & (responses['correct_answer'] == 0)]['time'])
            temp['count'] = temp['correct'] + temp['incorrect']
            temp['avg_time'] = (temp['correct'] * temp['correct_time'] + temp['incorrect'] * temp['incorrect_time'])/temp['count']
            data = pd.concat([data, temp])
    
    data = data.to_json(orient='records')
    count = np.nansum(data['count'])
    avg_time = np.nansum(data['avg_time'])

    body = {"data" : data, "count": count, "avg_time": avg_time}
    
    return api_response.generate_response(status_code=200, response_body=questions)