import pandas as pd
from cerberus import Validator
from datetime import datetime

def validate_discounts_payload(payload):
    schema = {
        "email": {'type': 'string', 'required': True},
        "name": {'type': 'string', 'required': True},
        "role": {'type': 'string', 'required': True},
        "sapId": {'required': False},
        "classId" : {'required': False}
    } 
    v = Validator(schema, require_all=False)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors