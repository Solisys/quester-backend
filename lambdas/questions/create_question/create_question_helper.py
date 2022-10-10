import pandas as pd
from cerberus import Validator
from datetime import datetime

def validate_payload(payload):
    schema = {
        'sessionId': {'type': 'int'},
        'accessBy': {'type': 'int'},
        'secret': {'type': 'string'},
        'questions': {'type': 'list'}
    } 
    v = Validator(schema, require_all=True)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors