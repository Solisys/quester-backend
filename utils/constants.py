"""
This file contains constants like configuration values, error message and success messages
for api responses and to be used across the project across all the APIs
"""


class ConfigConst:
    """
    This class will contain the list of all the config params
    """
    DEF_SKIP = 0
    DEF_TOP = 50
    DEF_ORDER = "DESC"
    DOWNLOAD_LINK_EXPIRY = 120  # in seconds
    UPLOAD_LINK_EXPIRY = 120  # in seconds
    ACCESS_TOKEN_EXPIRY = 14  # in days
    REFRESH_TOKEN_EXPIRY = 365  # in days
    DEF_FB_LIMIT = 10


class AuthConst:
    """
    This class defines the messages as constants for Auth.
    """

    INVALID_TOKEN = "Invalid token"
    MISSING_AUTH_TOKEN = "Unable to find token in headers"
    UNABLE_TO_DECODE = "Unable to decode provided authentication token"
    EXPIRED_TOKEN = "Token has expired"
    USER_DOES_NOT_EXIST = "No matching user for the given authentication token"
    NO_AUTH_TYPE = "No auth type was provided"
    AUTH_CONFIG_NOT_SET = "Auth configuration not set"


class Const:
    """
    This class will contain all the API responses both success and error messages
    """
    MISSING_COLUMN_ERROR = "Columns missing in input data"
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    MISSING_RECORD = "No record found in db"
    INVALID_FORMAT = "Input not in the expected formed"
    MISSING_TRANSACTION_ID = "Transaction id not provided in inputs"
    MISSING_QUERY_PARAMS = "Query parameters not provided in inputs"
    SUCCESS = "Success"
    FAILED_TO_GET_ENV_CONFIG = "Unable to fetch environment configuration"
    DB_FAILURE = "Failure while querying database"
    S3_FAILURE = "Failure while accessing S3"
    AUTH_TOKEN_NOT_GENERATED = "Access Token not generated for the given credential"
    ISSUE_GENR_AUTH = "Some issue with generating the auth URL(s)"
    EXT_API_FAILURE = "Failure while calling the external API"
    MISSING_PARA = "Parameters not provided in inputs"
    RECORD_PRESENT = "Record is already present"
    EXISTING_USER = "Cannot modify existing user"
    INVALID_USER = "User does not exist in domain"
    USER_EXISTS = "User already exists"
    INVALID_CREDENTIALS = "Invalid credentials"
    INVALID_INPUT = "Invalid input"
    INVALID_REQUEST = "Invalid request"
    INVALID_EMAIL = "Invalid email"
    UNAUTHORIZED = "Unauthorized to access this resource"