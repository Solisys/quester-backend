"""
Probable set of re-usable validations on various types for use cases
"""
import re


def validate_email_regex(email):
    """
    Function to validate email regex
    :param email: str
    :return: true/False
    """
    regex_check = re.match(r"^[\w\.-]+@[\w\.-]+(\.[\w]+)+", email, flags=re.IGNORECASE)
    domain = email.split("@")[-1]
    if regex_check and domain not in ["gmail.com", "outlook.com", "live.com"]:
        return True
    return False
