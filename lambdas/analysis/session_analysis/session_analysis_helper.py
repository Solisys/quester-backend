"""
This is the helper to get visualization data
"""
from datetime import datetime, timedelta
from cerberus import Validator


def validate_payload(payload):
    """
    This is the function to validate the payload
    :param payload: body of the post API call
    :return: "valid" in case of valid data otherwise respective error message
    """
    schema = {
        "sessionSecret": {"type": "string", "required": True},
        "tag": {"type": "boolean", "required": True},
    }
    v = Validator(schema)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors
