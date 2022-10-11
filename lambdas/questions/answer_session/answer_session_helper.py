import pandas as pd
from cerberus import Validator
from datetime import datetime

def validate_payload(payload):
    schema = {
        'count': {'type': 'int'},
        'questions': {'type': 'list'},
        'sessionId': {'type': 'int'}
    }
    v = Validator(schema, require_all=True)

    if v.validate(payload):
        return "valid"
    else:
        return v.errors