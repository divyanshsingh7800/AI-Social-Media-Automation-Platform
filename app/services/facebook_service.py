import os
import json
import secrets
import requests

from pathlib import Path
from urllib.parse import urlencode

from dotenv import load_dotenv


load_dotenv()


META_APP_ID = os.getenv(
    "META_APP_ID"
)

META_APP_SECRET = os.getenv(
    "META_APP_SECRET"
)

META_CONFIG_ID = os.getenv(
    "META_CONFIG_ID"
)

META_REDIRECT_URI = os.getenv(
    "META_REDIRECT_URI"
)


# --------------------------------------------------
# TEMP OAUTH STORAGE
# --------------------------------------------------

OAUTH_DIR = (
    Path(__file__).resolve().parents[2]
    / "meta_oauth_temp"
)

OAUTH_DIR.mkdir(
    exist_ok=True
)


# --------------------------------------------------
# CREATE META AUTH URL
# --------------------------------------------------

def get_facebook_authorization_url(
    user_id
):

    state = secrets.token_urlsafe(
        32
    )

    params = {

        "client_id":
            META_APP_ID,

        "redirect_uri":
            META_REDIRECT_URI,

        "state":
            state,

        "config_id":
            META_CONFIG_ID,

        "response_type":
            "code"
    }


    auth_url = (
        "https://www.facebook.com/dialog/oauth?"
        + urlencode(params)
    )


    # Save flow against this user
    # Each OAuth flow gets a unique file.

    oauth_file = (
        OAUTH_DIR
        / f"{state}.json"
    )


    oauth_file.write_text(

        json.dumps({

            "state":
                state,

            "user_id":
                user_id

        }),

        encoding="utf-8"
    )


    return auth_url


# --------------------------------------------------
# GET OAUTH DATA
# --------------------------------------------------

def get_meta_oauth_data(
    state
):

    if not state:

        return None


    oauth_file = (
        OAUTH_DIR
        / f"{state}.json"
    )


    if not oauth_file.exists():

        return None


    try:

        data = json.loads(

            oauth_file.read_text(
                encoding="utf-8"
            )

        )

        # One-time OAuth data
        oauth_file.unlink()

        return data


    except Exception:

        return None


# --------------------------------------------------
# EXCHANGE CODE
# --------------------------------------------------

def exchange_facebook_code(
    code
):

    token_url = (
        "https://graph.facebook.com/oauth/access_token"
    )


    params = {

        "client_id":
            META_APP_ID,

        "client_secret":
            META_APP_SECRET,

        "redirect_uri":
            META_REDIRECT_URI,

        "code":
            code
    }


    response = requests.get(

        token_url,

        params=params,

        timeout=30
    )


    if response.status_code != 200:

        raise Exception(

            "Meta token exchange failed: "
            f"{response.status_code} "
            f"{response.text}"

        )


    return response.json()


# --------------------------------------------------
# GET FACEBOOK PAGES
# --------------------------------------------------

def get_facebook_pages(access_token):

    url = "https://graph.facebook.com/me/accounts"

    params = {
        "access_token": access_token,
        "fields": "id,name,access_token,instagram_business_account"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    print("META /me/accounts STATUS:", response.status_code)
    print("META /me/accounts RESPONSE:", response.text)

    if response.status_code != 200:
        raise Exception(
            "Could not fetch Facebook Pages: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    return data.get("data", [])
# --------------------------------------------------
# GET INSTAGRAM ACCOUNT
# --------------------------------------------------

def get_instagram_account(
    page_access_token,
    instagram_id
):

    url = (
        f"https://graph.facebook.com/{instagram_id}"
    )


    params = {

        "access_token":
            page_access_token,

        "fields":
            (
                "id,"
                "username,"
                "name,"
                "profile_picture_url"
            )
    }


    response = requests.get(

        url,

        params=params,

        timeout=30
    )


    if response.status_code != 200:

        raise Exception(

            "Could not fetch Instagram account: "
            f"{response.status_code} "
            f"{response.text}"

        )


    return response.json()
