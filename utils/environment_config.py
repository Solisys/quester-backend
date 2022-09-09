"""
Environment config would be used to fetch secret based key/value pairs using
AWS Secrets Manager. The Key/Value pairs need to be configured manually
"""
import os
import json
import logging

import boto3

from utils import constants
from utils import generate_traceback as api_traceback


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class EnvironmentConfigurations:
    """
    The class will use AWS Secrets manager to store and retrieve secrets from AWS
    which can in turn then be used by any of the lambdas whenever required
    """
    def __init__(self):
        self.secrets_client = boto3.client("secretsmanager", region_name=os.environ.get("REGION_NAME"))

    def get_value(self, name, version=None):
        """
        Gets the value of a secret.

        Version (if defined) is used to retrieve a particular version of
        the secret.
        """
        kwargs = {"SecretId": name}
        if version is not None:
            kwargs["VersionStage"] = version
        try:
            response = self.secrets_client.get_secret_value(**kwargs)

        except Exception:
            api_traceback.generate_system_traceback()
            raise ValueError(constants.Const.FAILED_TO_GET_ENV_CONFIG)
        else:
            response = json.loads(response.get("SecretString"))
        return response
