import os
import secrets
import hashlib
import base64
import json
import requests

from pathlib import Path
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

X_CLIENT_ID = os.getenv("X_CLIENT_ID")
X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
X_REDIRECT_URI = os.getenv("X_REDIRECT_URI")

OAUTH_DIR = (
    Path(__file__).resolve().parents[2]
    / "oauth_temp"
)

OAUTH_DIR.mkdir(
    exist_ok=True
)


def generate_code_verifier():

    return secrets.token_urlsafe(64)


def generate_code_challenge(
    code_verifier
):

    digest = hashlib.sha256(
        code_verifier.encode("utf-8")
    ).digest()

    return base64.urlsafe_b64encode(
        digest
    ).decode("utf-8").rstrip("=")


def get_x_authorization_url():

    code_verifier = (
        generate_code_verifier()
    )

    state = secrets.token_urlsafe(32)

    code_challenge = (
        generate_code_challenge(
            code_verifier
        )
    )

    params = {
        "response_type": "code",
        "client_id": X_CLIENT_ID,
        "redirect_uri": X_REDIRECT_URI,
        "scope": (
            "tweet.read "
            "tweet.write "
            "users.read "
            "offline.access"
        ),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    url = (
        "https://twitter.com/i/oauth2/authorize?"
        + urlencode(params)
    )

    # One temporary file per OAuth flow
    oauth_file = (
        OAUTH_DIR /
        f"{state}.json"
    )

    oauth_file.write_text(
        json.dumps({
            "state": state,
            "code_verifier": code_verifier
        }),
        encoding="utf-8"
    )

    return url


def get_oauth_data(state):

    if not state:

        return None

    oauth_file = (
        OAUTH_DIR /
        f"{state}.json"
    )

    if not oauth_file.exists():

        return None

    try:

        data = json.loads(
            oauth_file.read_text(
                encoding="utf-8"
            )
        )

        # Delete after reading
        oauth_file.unlink()

        return data

    except Exception:

        return None


def exchange_code_for_token(
    code,
    code_verifier
):

    token_url = (
        "https://api.x.com/2/oauth2/token"
    )

    data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": X_REDIRECT_URI,
        "code_verifier": code_verifier
    }

    response = requests.post(
        token_url,
        data=data,
        auth=(
            X_CLIENT_ID,
            X_CLIENT_SECRET
        ),
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
        timeout=30
    )

    if response.status_code != 200:

        raise Exception(
            f"X token exchange failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()