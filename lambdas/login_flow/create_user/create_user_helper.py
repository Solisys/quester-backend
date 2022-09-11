import pandas as pd
from cerberus import Validator
from datetime import datetime

def validate_discounts_payload(payload):
    schema = {
        "email": {'type': 'string'},
        "name": {'type': 'string'},
        "role": {'type': 'string'},
        "sapId": {'required': False, 'type': 'int'},
        "classId" : {'required': False, 'type': 'int'}
    } 
    v = Validator(schema, require_all=True)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors