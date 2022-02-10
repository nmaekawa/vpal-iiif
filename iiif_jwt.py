import datetime
import logging
from multiprocessing.sharedctypes import Value
import os
import jwt
from cryptography.hazmat.primitives import serialization

from settings import ROOT_DIR


logger = logging.getLogger(__name__)

def make_iiif_jwt(
    issuer: str,
    resources: list,
    private_key_path: str,
    kid: str, 
    algorithm: str = "RS256",
    expiration: int = 3600
    ):
    """
        Makes a JWT token
        private_key_path: the secret key provided by LTS for the given issuer
        issuer: the service which issued the token
        kid: key ID
        resources: a list of resource types that the token is allowed to access
        exp: expiration NumericDate

        Example token data
        Header
            {
                "alg": "RS256",
                "typ": "JWT",
                "iss": "testissuer",
                "kid": "testkeyid",
                "resources": [
                    "description"
                ]
            }

        Payload
        {
            "iat": 1619628554,
            "exp": 3239257168
        }

        Valid algs: RS256, ???
        Exp range: <8 hours maximum

    """
    logger.info("Make IIIF LTS jwt")
    
    timestamp = datetime.datetime.now()
    header = {
        "alg": algorithm,
        "typ": "JWT",
        "iss": issuer,
        "kid": kid,
        "resources": resources
    }
    payload = {
        "iat": timestamp,
        "exp": expiration
    }

    private_key = open(private_key_path, "r").read()
    encoded_jwt = jwt.encode(payload, private_key, algorithm=algorithm, headers=header)
    return encoded_jwt

def load_auth(issuer: str, environment: str = "qa"):
    valid_environments = ["qa", "dev", "prod"]
    valid_apps = ["atmch", "atmediamanager", "atomeka", "atdarth"]
    try:
        issuer in valid_apps
    except ValueError:
        print("Invalid issuer")

    try:
        environment in valid_environments
    except ValueError:
        print("Invalid environment")

    os.environ['ENVIRONMENT'] = environment
    os.environ['ISSUER'] = issuer
    os.environ['KEY_ID'] = f"${issuer}default"
    os.environ['PUBLIC_KEY_PATH'] = os.path.join(ROOT_DIR, f"auth/{environment}/keys/{issuer}/{issuer}default/public.key")
    os.environ['PRIVATE_KEY_PATH'] = os.path.join(ROOT_DIR, f"auth/{environment}/keys/{issuer}/{issuer}default/private.key")


def test():
    load_auth("atmch", "qa")
    token = make_iiif_jwt(
        os.environ.get("ISSUER"),
        ["ingest", "content", "description"],
        os.environ.get("PRIVATE_KEY_PATH"),
        os.environ.get("KEY_ID")
    )
    print(token)

if __name__ == '__main__':
    test()