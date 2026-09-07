import streamlit as st

from app.services.database import (
    initialize_database
)

from app.services.scheduler import (
    start_scheduler
)

from app.ui.auth_ui import (
    show_authentication,
    show_sidebar
)

from app.ui.social_ui import (
    handle_x_oauth_callback,
    handle_instagram_oauth_callback,
    handle_facebook_oauth_callback,
    show_social_accounts
)

from app.ui.dashboard import (
    show_dashboard
)


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Social Media Automation",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# START SCHEDULER
# --------------------------------------------------

if "scheduler_started" not in st.session_state:

    start_scheduler()

    st.session_state[
        "scheduler_started"
    ] = True


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

if not st.session_state.get(
    "logged_in",
    False
):

    show_authentication()

    st.stop()


# --------------------------------------------------
# SOCIAL OAUTH CALLBACKS
# --------------------------------------------------

query_params = st.query_params

code = query_params.get("code")
state = query_params.get("state")

if code:

    # Instagram callback
    if st.session_state.get(
        "instagram_oauth_state"
    ):

        handle_instagram_oauth_callback()

        st.stop()


    # Facebook callback
    if st.session_state.get(
        "facebook_oauth_state"
    ):

        handle_facebook_oauth_callback()

        st.stop()


    # X callback
    if st.session_state.get(
        "x_oauth_state"
    ):

        handle_x_oauth_callback()

        st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

show_sidebar()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title(
    "🤖 AI Social Media Automation"
)

st.write(
    "Turn a simple 2–5 word idea into ready-to-publish "
    "social media content."
)


# --------------------------------------------------
# SOCIAL MEDIA ACCOUNTS
# --------------------------------------------------

show_social_accounts()


# --------------------------------------------------
# MAIN DASHBOARD
# --------------------------------------------------

show_dashboard()