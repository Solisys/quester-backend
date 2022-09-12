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
import create_user_helper as helper

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

    if isinstance(event.get("body"), type(None)) or not event.get("body"):
        message = {
            "message": f"Payload missing in the input"
        }
        logger.warning(message.get("message"))
        return api_response.generate_response(status_code=400, response_body=message)

    else:
        body = json.loads(event.get("body", dict()))
        result = helper.validate_discounts_payload(body)
        if result != "valid":
            logger.info("Input payload is invalid")
            logger.debug(result)
            return api_response.generate_response(status_code=400, response_body=result)
    
    email = body['email']
    name = body['name']
    role = body['role']
    sap_id = body['sapId']
    class_id = body['classId']

    user = pd.DataFrame([{
            'email': email,
            'name': name,
            'role': role,
            'status': 'active'
        }])

    try:
        user.to_sql(con=conn, name='users', if_exists='append', index=False)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    query = f"select user_id from sys.users where email = '{email}'"

    try:    
        result = pd.read_sql(query, conn)
        result = result.to_dict('records')
        user_id = result[0]['user_id']
    except:
        api_traceback.generate_system_traceback()
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if role == 'teacher':
        for classes in class_id:
            teacher = pd.DataFrame([{
                'user_id': user_id,
                'class_id': classes,
            }])
            try:
                teacher.to_sql(con=conn, name='teacher_class', if_exists='append', index=False)
            except:
                api_traceback.generate_system_traceback()
                message = {"message": Const.DB_FAILURE}
                return api_response.generate_response(status_code=500, response_body=message)


    if role == 'student':
        student = pd.DataFrame([{
                'user_id': user_id,
                'class_id': class_id,
                'sap_id': sap_id
            }])
        try:
            student.to_sql(con=conn, name='students', if_exists='append', index=False)
        except:
            api_traceback.generate_system_traceback()
            message = {"message": Const.DB_FAILURE}
            return api_response.generate_response(status_code=500, response_body=message)

    message = {
        'user_id': user_id,
        'message': Const.SUCCESS
        }
    return api_response.generate_response(status_code=201, response_body=message)
