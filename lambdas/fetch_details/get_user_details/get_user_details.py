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
import get_user_details_helper as helper

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
    
    user_id = body['userId']
    query = f'select * from sys.users where id = {user_id}'
    
    try:
        user = pd.read_sql(query, conn)
    except:
        message = {"message": Const.DB_FAILURE}
        return api_response.generate_response(status_code=500, response_body=message)

    if user.empty:
        message = {"message": Const.INVALID_USER}
        return api_response.generate_response(status_code=404, response_body=message)
    
    result = user.to_dict('records')
    if result[0]['role'] == 'student':

        query = f'select * from sys.students where id = {user_id}'
    
        try:
            student = pd.read_sql(query, conn)
            student = student.to_dict('records')
        except:
            message = {"message": Const.DB_FAILURE}
            return api_response.generate_response(status_code=500, response_body=message)
        
        user = {
            "user_id": student[0]['user_id'],
            "class_id": student[0]['class_id'],
            "name": result[0]['name'],
            "email": result[0]['email']
        }
    else:
        
        query = f'select * from sys.teacher_class where id = {user_id}'
    
        try:
            teachers = pd.read_sql(query, conn)
            teachers = teachers.to_dict('records')
        except:
            message = {"message": Const.DB_FAILURE}
            return api_response.generate_response(status_code=500, response_body=message)

        class_id = []
        for teacher in teachers:
            class_id.append(teacher['class_id'])

        user = {
            "user_id": result[0]['id'],
            "name": result[0]['name'],
            "email": result[0]['email'],
            "class_id": class_id
        }
    
    return api_response.generate_response(status_code=200, response_body=user)