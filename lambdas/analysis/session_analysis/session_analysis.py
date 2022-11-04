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
import session_analysis_helper as helper
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
    # jwt_token = event.get("headers").get("Authorization").split('Bearer ')[1]
    #
    # try:
    #     email = authenticate(jwt_token, conn)
    #     print('done')
    # except Exception as e:
    #     message = {"message": str(e)}
    #     return api_response.generate_response(status_code=401, response_body=message)
    #
    # query = f'select * from sys.users where email = "{email}"'
    #
    # try:
    #     user = pd.read_sql(query, conn)
    # except:
    #     message = {"message": Const.DB_FAILURE}
    #     return api_response.generate_response(status_code=500, response_body=message)
    #
    # if user.empty:
    #     message = {"message": Const.INVALID_USER}
    #     return api_response.generate_response(status_code=404, response_body=message)
    #
    # result = user.to_dict('records')
    #
    # if result[0]['role'] == 'student':
    #     message = {"message": Const.INVALID_USER}
    #     return api_response.generate_response(status_code=404, response_body=message)
    #
    # if isinstance(event.get("body"), type(None)) or not event.get("body"):
    #     message = {
    #         "message": f"Payload missing in the input"
    #     }
    #     logger.warning(message.get("message"))
    #     return api_response.generate_response(status_code=400, response_body=message)
    #
    # else:
    #     body = json.loads(event.get("body", dict()))
    #     result = helper.validate_payload(body)
    #     if result != "valid":
    #         logger.info("Input payload is invalid")
    #         logger.debug(result)
    #         return api_response.generate_response(status_code=400, response_body=result)
    #
    # secret = body['sessionSecret']
    # tag = body.get('tag', None)

    tag = None
    secret = "demo"

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
        query = f"select questions.tag, responses.correct_answer, count(responses.correct_answer) as count, " \
                f"avg(responses.time) as time from sys.responses left join sys.questions on responses.question_id = " \
                f"questions.question_id where questions.session_id = {session_id} group by questions.tag, " \
                f"responses.correct_answer"
    else:
        query = f"select questions.description, responses.correct_answer, count(responses.correct_answer) as count, " \
                f"avg(responses.time) as time from sys.responses left join sys.questions on responses.question_id = " \
                f"questions.question_id where questions.session_id = {session_id} group by responses.question_id, " \
                f"responses.correct_answer"

    try:
        responses = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if responses.empty:
        message = {"message": Const.NO_RESPONSES}
        return api_response.generate_response(status_code=404, response_body=message)

    data = pd.DataFrame()

    if tag:
        tags = list(responses['tag'].unique())
        for tag in tags:
            temp = helper.analysis(tag, responses, 'tag')
            data = pd.concat([data, temp])
    else:
        questions = list(responses['description'].unique())
        for question in questions:
            temp = helper.analysis(question, responses, 'description')
            data = pd.concat([data, temp])

    if "tag" in data.columns:
        data.rename(columns={'tag': 'description'}, inplace=True)

    avg_time = np.nansum(data['avg_time'])
    count = np.nansum(data['count'])
    most_time = data[data.avg_time == data.avg_time.max()].to_json(orient='records')
    least_time = data[data.avg_time == data.avg_time.min()].to_json(orient='records')
    most_correct = data[data.correct == data.correct.max()].to_json(orient='records')
    least_correct = data[data.correct == data.correct.min()].to_json(orient='records')
    data = data.to_json(orient='records')

    body = {
        "data": json.loads(data),
        "count": count,
        "avg_time": avg_time,
        "mostCorrect": json.loads(most_correct),
        "mostTime": json.loads(most_time),
        "leastCorrect": json.loads(least_correct),
        "leastTime": json.loads(least_time)
    }

    return api_response.generate_response(status_code=200, response_body=body)

lambda_handler("123", 123)