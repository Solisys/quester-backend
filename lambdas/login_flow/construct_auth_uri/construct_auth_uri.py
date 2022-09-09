"""
The api is used for constructing login URL(s) for Google and Microsoft
"""
import os
import logging
import sys

from utils import generate_response as api_response
from utils import generate_traceback as api_traceback
from utils import environment_config
from utils import constants
from utils.global_config import AuthConfig


logger = logging.getLogger()
logger.setLevel(int(os.environ.get("LOG_LEVEL")))


def lambda_handler(event, context):
    """
    Handler to construct auth URI
    @:param: {
        authType: string (auth type google)
    }
    @:returns {
        "authUrl": Google,
        "message": message
    }
    """
    auth_type = event.get("queryStringParameters").get("authType")
    if not auth_type:
        logger.warning(f"{constants.AuthConst.NO_AUTH_TYPE}")
        message = {"message": constants.AuthConst.NO_AUTH_TYPE}
        return api_response.generate_response(status_code=400, response_body=message)

    auth_type = auth_type.lower()
    try:
        auth_config = eval(f"AuthConfig.{auth_type}_auth_config")
        if not auth_config:
            message = {"message": constants.AuthConst.AUTH_CONFIG_NOT_SET}
            return api_response.generate_response(
                status_code=500, response_body=message
            )

        # constructing google/microsoft oauth2 api url
        auth_url = (
            f"{auth_config.get('endpointURL')}"
            f"response_type={auth_config.get('responseType')}"
            f"&client_id={auth_config.get('auth_client_id')}"
            f"&scope={auth_config.get('scope')}"
            f"&redirect_uri={auth_config.get('redirectURI')}"
            f"&access_type={auth_config.get('accessType')}"
            f"&state={auth_type}"
        )

        return api_response.generate_response(
            status_code=302, response_body={"authUrl": auth_url}, location=auth_url
        )

    except Exception as e:
        api_traceback.generate_system_traceback()
        message = {"message": constants.AuthConst.ISSUE_GENR_AUTH}
        logger.warning(message.get("message"))
        return api_response.generate_response(status_code=500, response_body=message)
