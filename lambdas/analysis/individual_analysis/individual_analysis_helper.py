"""
This is the helper to get visualization data
"""
from datetime import datetime, timedelta
from cerberus import Validator
import pandas as pd


def validate_payload(payload):
    """
    This is the function to validate the payload
    :param payload: body of the post API call
    :return: "valid" in case of valid data otherwise respective error message
    """
    schema = {
        "studentId": {"type": "integer", "required": True},
        "tag": {"type": "boolean", "required": False},
    }
    v = Validator(schema)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors


def analysis(check, responses, type):
    temp = pd.DataFrame([check], columns=[type])
    correct = responses[(responses[type] == check) & (responses['correct_answer'] == 1)]
    incorrect = responses[(responses[type] == check) & (responses['correct_answer'] == 0)]
    if not correct.empty:
        temp['correct'] = int(correct['count'])
        temp['correct_time'] = correct['time']
    else:
        temp['correct'] = 0
        temp['correct_time'] = 0

    if not incorrect.empty:
        temp['incorrect'] = int(incorrect['count'])
        temp['incorrect_time'] = incorrect['time']
    else:
        temp['incorrect'] = 0
        temp['incorrect_time'] = 0

    temp['count'] = temp['correct'] + temp['incorrect']
    temp['avg_time'] = (temp['correct'] * temp['correct_time'] + temp['incorrect'] * temp['incorrect_time']) / temp[
        'count']

    return temp
