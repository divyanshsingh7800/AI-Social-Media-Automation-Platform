import os
import secrets
import requests
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()


META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
META_REDIRECT_URI = os.getenv("META_REDIRECT_URI")
INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
INSTAGRAM_REDIRECT_URI = os.getenv("META_REDIRECT_URI")


# --------------------------------------------------
# INSTAGRAM AUTHORIZATION
# --------------------------------------------------

def get_instagram_authorization_url():

    state = secrets.token_urlsafe(32)

    params = {
        "client_id": INSTAGRAM_APP_ID,
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "response_type": "code",
        "scope": (
            "instagram_business_basic,"
            "instagram_business_content_publish"
        ),
        "state": state,
    }

    auth_url = (
        "https://www.instagram.com/oauth/authorize?"
        + urlencode(params)
    )

    return auth_url, state

# --------------------------------------------------
# TOKEN EXCHANGE
# --------------------------------------------------

def exchange_instagram_code(code):

    response = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": META_REDIRECT_URI,
            "code": code,
        },
        timeout=30,
    )

    if response.status_code != 200:

        raise Exception(
            f"Instagram token exchange failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()


# --------------------------------------------------
# GET INSTAGRAM ACCOUNT
# --------------------------------------------------

def get_instagram_account(access_token):

    response = requests.get(
        "https://graph.instagram.com/me",
        params={
            "fields": "user_id,username",
            "access_token": access_token,
        },
        timeout=30,
    )

    if response.status_code != 200:

        raise Exception(
            f"Instagram account fetch failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    return response.json()
