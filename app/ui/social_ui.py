import streamlit as st

from app.services.x_service import (
    get_x_authorization_url,
    get_oauth_data,
    exchange_code_for_token
)

from app.services.database import (
    save_social_account
)

from app.services.facebook_service import (
    get_facebook_authorization_url,
    get_meta_oauth_data,
    exchange_facebook_code,
    get_facebook_pages,
    get_instagram_account
)
from app.services.instagram_service import (
    get_instagram_authorization_url,
    exchange_instagram_code,
    get_instagram_account
)


def handle_x_oauth_callback():

    x_code = st.query_params.get(
        "code"
    )

    x_state = st.query_params.get(
        "state"
    )

    if not x_code:

        return False

    if not x_state:

        st.error(
            "X OAuth state missing."
        )

        st.query_params.clear()

        return True

    # Get OAuth data using the state
    oauth_data = get_oauth_data(
        x_state
    )

    if not oauth_data:

        st.error(
            "X OAuth session expired. "
            "Please connect X again."
        )

        st.query_params.clear()

        return True

    saved_state = oauth_data.get(
        "state"
    )

    code_verifier = oauth_data.get(
        "code_verifier"
    )

    if x_state != saved_state:

        st.error(
            "Invalid X OAuth state."
        )

        st.query_params.clear()

        return True

    try:

        with st.spinner(
            "Connecting X account..."
        ):

            token_data = (
                exchange_code_for_token(
                    x_code,
                    code_verifier
                )
            )

        access_token = (
            token_data.get(
                "access_token"
            )
        )

        refresh_token = (
            token_data.get(
                "refresh_token"
            )
        )

        if not access_token:

            raise Exception(
                "X did not return an access token."
            )

        save_social_account(
            user_id=st.session_state[
                "user_id"
            ],
            platform="X",
            access_token=access_token,
            refresh_token=refresh_token
        )

        st.session_state[
            "x_connected"
        ] = True

        st.session_state[
            "x_access_token"
        ] = access_token

        if refresh_token:

            st.session_state[
                "x_refresh_token"
            ] = refresh_token

        st.query_params.clear()

        st.success(
            "🐦 X account connected successfully! 🎉"
        )

        return True

    except Exception as e:

        st.error(
            "X account connection failed."
        )

        st.code(str(e))

        return True

def handle_facebook_oauth_callback():

    fb_code = st.query_params.get(
        "code"
    )

    fb_state = st.query_params.get(
        "state"
    )

    if not fb_code:

        return False


    if not fb_state:

        st.error(
            "Facebook OAuth state missing."
        )

        st.query_params.clear()

        return True


    oauth_data = (
        get_meta_oauth_data(
            fb_state
        )
    )


    if not oauth_data:

        st.error(
            "Facebook OAuth session expired. "
            "Please connect again."
        )

        st.query_params.clear()

        return True


    saved_state = oauth_data.get(
        "state"
    )

    user_id = oauth_data.get(
        "user_id"
    )


    if fb_state != saved_state:

        st.error(
            "Invalid Facebook OAuth state."
        )

        st.query_params.clear()

        return True


    if not user_id:

        st.error(
            "User information missing."
        )

        st.query_params.clear()

        return True


    try:

        with st.spinner(
            "Connecting Facebook..."
        ):

            token_data = (
                exchange_facebook_code(
                    fb_code
                )
            )


        user_access_token = (
            token_data.get(
                "access_token"
            )
        )


        if not user_access_token:

            raise Exception(
                "Meta did not return an access token."
            )


        pages = get_facebook_pages(
            user_access_token
        )


        if not pages:

            raise Exception(
                "No Facebook Pages were found. "
                "Make sure your Facebook account "
                "has access to a Page."
            )


        # Save token temporarily in session
        st.session_state[
            "meta_user_access_token"
        ] = user_access_token


        st.session_state[
            "meta_pages"
        ] = pages


        st.session_state[
            "meta_user_id"
        ] = user_id


        # Remove OAuth parameters

        st.query_params.clear()


        st.success(
            "🔵 Facebook connected successfully!"
        )


        return True


    except Exception as e:

        st.error(
            "Facebook connection failed."
        )

        st.code(
            str(e)
        )

        return True

def handle_instagram_oauth_callback():

    code = st.query_params.get("code")
    state = st.query_params.get("state")

    if not code:
        return False

    saved_state = st.session_state.get(
        "instagram_oauth_state"
    )

    if not saved_state:

        st.error(
            "Instagram OAuth session expired. "
            "Please connect again."
        )

        st.query_params.clear()

        return True

    if state != saved_state:

        st.error(
            "Invalid Instagram OAuth state."
        )

        st.query_params.clear()

        return True

    try:

        with st.spinner(
            "Connecting Instagram..."
        ):

            token_data = (
                exchange_instagram_code(code)
            )

            access_token = token_data.get(
                "access_token"
            )

            if not access_token:

                raise Exception(
                    "Instagram did not return "
                    "an access token."
                )

            account = get_instagram_account(
                access_token
            )

        instagram_user_id = account.get(
            "user_id"
        )

        username = account.get(
            "username"
        )

        if not instagram_user_id:

            raise Exception(
                "Instagram user ID not returned."
            )

        # Save account for current logged-in user
        from app.services.database import (
            save_social_account
        )

        save_social_account(
            user_id=st.session_state["user_id"],
            platform="Instagram",
            access_token=access_token,
            refresh_token=None
        )

        st.session_state[
            "instagram_connected"
        ] = True

        st.session_state[
            "instagram_user_id"
        ] = instagram_user_id

        st.session_state[
            "instagram_username"
        ] = username

        st.session_state.pop(
            "instagram_oauth_state",
            None
        )

        st.session_state.pop(
            "instagram_auth_url",
            None
        )

        st.query_params.clear()

        st.success(
            f"📸 Instagram @{username} "
            "connected successfully! 🎉"
        )

        return True

    except Exception as e:

        st.error(
            "Instagram connection failed."
        )

        st.code(str(e))

        return True

def show_social_accounts():

    st.divider()

    st.subheader(
        "🔗 Social Media Accounts"
    )

    col1, col2, col3 = st.columns(3)

    # X
    with col1:

        st.markdown("### 🐦 X")

        if st.session_state.get(
            "x_connected",
            False
        ):

            st.success(
                "Connected ✅"
            )

        else:

            if st.button(
                "Connect X",
                key="connect_x",
                width="stretch"
            ):

                try:

                    auth_url = (
                        get_x_authorization_url()
                    )

                    st.session_state[
                        "x_auth_url"
                    ] = auth_url

                except Exception as e:

                    st.error(
                        "Could not start X authentication."
                    )

                    st.code(str(e))

            if st.session_state.get(
                "x_auth_url"
            ):

                st.link_button(
                    "Continue with X",
                    st.session_state[
                        "x_auth_url"
                    ],
                    width="stretch"
                )

    # Facebook
    with col2:

        st.markdown(
            "### 🔵 Facebook"
        )

        if st.button(
                "Connect Facebook",
                key="connect_facebook",
                width="stretch"
        ):

            try:

                auth_url = (
                    get_facebook_authorization_url(
                        st.session_state["user_id"]
                    )
                )

                st.session_state[
                    "facebook_auth_url"
                ] = auth_url

            except Exception as e:

                st.error(
                    "Could not start Facebook authentication."
                )

                st.code(
                    str(e)
                )


        if st.session_state.get(
            "facebook_auth_url"
        ):

            st.link_button(
                "Continue with Facebook",
                st.session_state[
                    "facebook_auth_url"
                ],
                width="stretch"
            )

    # Instagram
    with col3:

        st.markdown(
            "### 📸 Instagram"
        )

        if st.session_state.get(
            "instagram_connected",
            False
        ):

            st.success(
                "Instagram Connected ✅"
            )

            st.write(
                f"@{st.session_state.get('instagram_username', '')}"
            )

        else:

            if st.button(
                "🔗 Connect Instagram",
                key="connect_instagram",
                width="stretch"
            ):

                auth_url, state = get_instagram_authorization_url()

                st.session_state[
                    "instagram_oauth_state"
                ] = state

                st.session_state[
                    "instagram_auth_url"
                ] = auth_url


            if st.session_state.get(
                "instagram_auth_url"
            ):

                st.link_button(
                "👉 Continue with Instagram",
                st.session_state["instagram_auth_url"],
                width="stretch"
            )
