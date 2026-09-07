import streamlit as st

from app.services.database import (
    create_user,
    get_user_by_email
)

from app.services.auth_service import (
    hash_password,
    verify_password
)


def show_authentication():

    st.title("🤖 AI Social Media Automation")

    st.write(
        "Create, schedule and manage your social media posts with AI."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    with login_tab:

        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            width="stretch"
        ):

            if not login_email or not login_password:

                st.warning(
                    "Please enter email and password."
                )

            else:

                user = get_user_by_email(
                    login_email.strip().lower()
                )

                if not user:

                    st.error(
                        "Invalid email or password."
                    )

                elif not verify_password(
                    login_password,
                    user[3]
                ):

                    st.error(
                        "Invalid email or password."
                    )

                else:

                    st.session_state[
                        "logged_in"
                    ] = True

                    st.session_state[
                        "user_id"
                    ] = user[0]

                    st.session_state[
                        "user_name"
                    ] = user[1]

                    st.session_state[
                        "user_email"
                    ] = user[2]

                    st.success(
                        f"Welcome, {user[1]}! 🎉"
                    )

                    st.rerun()

    # --------------------------------------------------
    # SIGN UP
    # --------------------------------------------------

    with signup_tab:

        st.subheader("Create Account")

        signup_name = st.text_input(
            "Name",
            key="signup_name"
        )

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm_password"
        )

        if st.button(
            "Create Account",
            width="stretch"
        ):

            if not all([
                signup_name,
                signup_email,
                signup_password,
                signup_confirm_password
            ]):

                st.warning(
                    "Please fill all fields."
                )

            elif signup_password != signup_confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                existing_user = get_user_by_email(
                    signup_email.strip().lower()
                )

                if existing_user:

                    st.error(
                        "An account with this email already exists."
                    )

                else:

                    password_hash = hash_password(
                        signup_password
                    )

                    user_id = create_user(
                        signup_name.strip(),
                        signup_email.strip().lower(),
                        password_hash
                    )

                    if user_id:

                        st.success(
                            "Account created successfully! "
                            "You can now login. 🎉"
                        )

                    else:

                        st.error(
                            "Could not create account."
                        )


def show_sidebar():

    with st.sidebar:

        st.success(
            f"Logged in as\n"
            f"{st.session_state['user_email']}"
        )

        if st.button(
            "🚪 Logout",
            width="stretch"
        ):

            for key in [
                "logged_in",
                "user_id",
                "user_name",
                "user_email",
                "content",
                "topic",
                "post_id",
                "image_path",
                "x_connected",
                "x_access_token",
                "x_refresh_token",
                "x_auth_url"
            ]:

                st.session_state.pop(
                    key,
                    None
                )

            st.rerun()
