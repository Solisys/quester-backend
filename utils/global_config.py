"""
This file contains constants like configuration values to be used across the project across all the APIs
"""


class AuthConfig:
    """
    This class will contain the list of all the configuration related to google auth
    """
    google_auth_config = {
        "endpointURL": "https://accounts.google.com/o/oauth2/v2/auth?",
        "scope": "profile email",
        "accessType": "offline",
        "redirectURI": "https://api.quester.live/create-tokens",
        "responseType": "code",
        "grantType": "authorization_code",
        "tokenURL": "https://oauth2.googleapis.com/token",
        "emailURL": "https://www.googleapis.com/oauth2/v3/userinfo?",
        "auth_client_id": '219657477408-tmus1ta8jgbp7mda4n1heniu3i20ssrl.apps.googleusercontent.com'
    }


class FrontEndConfig:
    """
    This class will contains all the configurations related to front end
    """
    callback_url = "https://app.quester.com/"
