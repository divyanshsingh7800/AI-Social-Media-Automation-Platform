import streamlit as st
from app.services.x_service import (
    get_x_authorization_url,
    exchange_code_for_token
)
from app.services.database import (
    initialize_database,
    create_user,
    get_user_by_email
)
from app.services.auth_service import (
    hash_password,
    verify_password
)
import json
from app.services.x_service import (
    get_x_authorization_url,
    exchange_code_for_token,
    OAUTH_FILE
)
from app.services.image_service import generate_image
from app.services.gemini_service import generate_social_content

from app.services.database import (
    initialize_database,
    save_post,
    get_all_posts,
    schedule_post,
    update_image_path,
    update_post_content,
    update_image_prompt
)
from app.services.scheduler import start_scheduler


# --------------------------------------------------
# INITIALIZE
# --------------------------------------------------

initialize_database()


if "scheduler_started" not in st.session_state:

    start_scheduler()

    st.session_state["scheduler_started"] = True

st.subheader("🔐 Authentication Test")

name = st.text_input("Name")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)


if st.button("Create Account"):

    if not name or not email or not password:

        st.warning(
            "Please fill all fields."
        )

    else:

        password_hash = hash_password(
            password
        )

        user_id = create_user(
            name,
            email,
            password_hash
        )

        if user_id:

            st.success(
                f"Account created! User ID: {user_id}"
            )

        else:

            st.error(
                "Email already exists."
            )


if st.button("Test Login"):

    user = get_user_by_email(email)

    if not user:

        st.error(
            "User not found."
        )

    elif verify_password(
        password,
        user[3]
    ):

        st.success(
            f"Login successful! Welcome {user[1]}"
        )

    else:

        st.error(
            "Incorrect password."
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
# X OAUTH CALLBACK
# --------------------------------------------------

x_code = st.query_params.get("code")
x_state = st.query_params.get("state")


if x_code:

    try:

        oauth_data = json.loads(
            OAUTH_FILE.read_text(
                encoding="utf-8"
            )
        )

        saved_state = oauth_data["state"]

        code_verifier = oauth_data["code_verifier"]

    except Exception as e:

        st.error(
            "Temporary OAuth data not found."
        )

        st.code(str(e))

        st.stop()


    if x_state != saved_state:

        st.error(
            "Invalid X OAuth state."
        )

        st.stop()


    try:

        with st.spinner(
            "Connecting X account..."
        ):

            token_data = exchange_code_for_token(
                x_code,
                code_verifier
            )


        access_token = token_data.get(
            "access_token"
        )

        refresh_token = token_data.get(
            "refresh_token"
        )


        if not access_token:

            raise Exception(
                "X did not return an access token."
            )


        st.session_state[
            "x_access_token"
        ] = access_token


        if refresh_token:

            st.session_state[
                "x_refresh_token"
            ] = refresh_token


        st.session_state[
            "x_connected"
        ] = True


        # Delete temporary OAuth data
        if OAUTH_FILE.exists():

            OAUTH_FILE.unlink()


        st.session_state.pop(
            "x_auth_url",
            None
        )


        st.query_params.clear()


        st.success(
            "🐦 X account connected successfully! 🎉"
        )


    except Exception as e:

        st.error(
            "X account connection failed."
        )

        st.code(str(e))
# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🤖 AI Social Media Automation")

st.write(
    "Turn a simple 2–5 word idea into ready-to-publish "
    "social media content."
)

st.divider()


# --------------------------------------------------
# CREATE POST
# --------------------------------------------------

st.subheader("💡 Create New Post")


topic = st.text_input(
    "Enter your topic",
    placeholder="Example: AI in Healthcare"
)


if st.button(
    "✨ Generate Content",
    use_container_width=True
):

    if not topic.strip():

        st.warning(
            "Please enter a topic."
        )

    else:

        with st.spinner(
            "Creating your social media content..."
        ):

            try:

                # ----------------------------------
                # 1. GEMINI CONTENT GENERATION
                # ----------------------------------

                content = generate_social_content(
                    topic
                )


                # ----------------------------------
                # 2. SAVE POST TO DATABASE
                # ----------------------------------

                post_id = save_post(

                    topic=topic,

                    image_prompt=content[
                        "image_prompt"
                    ],

                    caption=content[
                        "caption"
                    ],

                    hashtags=content[
                        "hashtags"
                    ]
                )


                # ----------------------------------
                # 3. GENERATE REAL IMAGE
                # ----------------------------------

                image_filename = (
                    f"post_{post_id}.png"
                )

                image_path = generate_image(

                    content["image_prompt"],

                    image_filename
                )
                if image_path:

                            update_image_path(
                                post_id,
                                image_path
                            )


                # ----------------------------------
                # 4. SAVE TO SESSION
                # ----------------------------------

                st.session_state[
                    "content"
                ] = content

                st.session_state[
                    "topic"
                ] = topic

                st.session_state[
                    "post_id"
                ] = post_id

                st.session_state[
                    "image_path"
                ] = image_path


                if image_path:

                    st.success(
                        "Content and image generated successfully! 🎉"
                    )

                else:

                    st.warning(
                        "Content generated, but image generation failed."
                    )


            except Exception as e:

                st.error(
                    "Content generation failed."
                )

                st.code(
                    str(e)
                )


# --------------------------------------------------
# GENERATED CONTENT
# --------------------------------------------------

if "content" in st.session_state:

    content = st.session_state[
        "content"
    ]

    st.divider()

    st.subheader(
        "📋 Generated Content"
    )


    # ----------------------------------------------
    # IMAGE
    # ----------------------------------------------

    if (
        "image_path" in st.session_state
        and st.session_state["image_path"]
    ):

        st.markdown(
            "### 🖼️ Generated Image"
        )

        st.image(
            st.session_state["image_path"],
            width=500
        )


    # ----------------------------------------------
    # IMAGE PROMPT
    # ----------------------------------------------

    st.markdown(
        "### 🎨 Image Prompt"
    )

    edited_image_prompt = st.text_area(
    "Edit Image Prompt",

    value=content[
        "image_prompt"
    ],

    height=300,

    key="edited_image_prompt"
)   

    if st.button(
    "🔄 Regenerate Image",
    use_container_width=True):

                            with st.spinner(
                                "Generating new AI image..."
                            ):

                                try:

                                    post_id = st.session_state[
                                        "post_id"
                                    ]

                                    image_filename = (
                                        f"post_{post_id}.png"
                                    )

                                    # Generate new image
                                    new_image_path = generate_image(

                                        edited_image_prompt,

                                        image_filename
                                    )


                                    if new_image_path:

                                        # Update database
                                        update_image_path(

                                            post_id,

                                            new_image_path
                                        )


                                        # Update image prompt
                                        update_image_prompt(

                                            post_id,

                                            edited_image_prompt
                                        )


                                        # Update session
                                        st.session_state[
                                            "content"
                                        ]["image_prompt"] = (
                                            edited_image_prompt
                                        )


                                        st.session_state[
                                            "image_path"
                                        ] = new_image_path


                                        st.success(
                                            "New AI image generated successfully! 🎉"
                                        )


                                        st.rerun()


                                    else:

                                        st.error(
                                            "Image generation failed."
                                        )


                                except Exception as e:

                                    st.error(
                                        "Image regeneration failed."
                                    )

                                    st.code(
                                        str(e)
                                    )


    # ----------------------------------------------
    # CAPTION
    # ----------------------------------------------

    st.markdown(
        "### 📝 Caption"
    )

    st.text_area(
        "Social media caption",

        value=content[
            "caption"
        ],

        height=220,

        key="caption"
    )


    # ----------------------------------------------
    # HASHTAGS
    # ----------------------------------------------

    st.markdown(
        "### #️⃣ Hashtags"
    )

    hashtags = " ".join(
        content["hashtags"]
    )

    st.text_area(
        "Hashtags",

        value=hashtags,

        height=100,

        key="hashtags"
    )

    # ----------------------------------------------
    # EDIT POST
    # ----------------------------------------------

    st.divider()

    st.subheader("✏️ Edit Post")


    edited_caption = st.text_area(
        "Edit Caption",

        value=content["caption"],

        height=220,

        key="edited_caption"
    )


    edited_hashtags = st.text_input(
        "Edit Hashtags",

        value=" ".join(
            content["hashtags"]
        ),

        key="edited_hashtags"
    )

    if st.button(
        "💾 Save Changes",
        use_container_width=True
    ):

        hashtag_list = [
            tag.strip()
            for tag in edited_hashtags.split()
            if tag.strip()
        ]


        update_post_content(

            post_id=st.session_state[
                "post_id"
            ],

            caption=edited_caption,

            hashtags=hashtag_list
        )


        st.session_state[
            "content"
        ]["caption"] = edited_caption


        st.session_state[
            "content"
        ]["hashtags"] = hashtag_list


        st.success(
            "Post changes saved successfully! ✅"
        )


        st.rerun()


    # ----------------------------------------------
    # POST INFO
    # ----------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Post ID",
            st.session_state["post_id"]
        )

    with col2:

        st.metric(
            "Hashtags",
            len(content["hashtags"])
        )


st.divider()
if st.button(
    "🔗 Connect X Account",
    use_container_width=True
):

    try:

        auth_url = get_x_authorization_url()

        st.session_state["x_auth_url"] = auth_url

    except Exception as e:

        st.error(
            "Could not start X authentication."
        )

        st.code(str(e))


if st.session_state.get("x_auth_url"):

    st.link_button(
        "👉 Continue with X",
        st.session_state["x_auth_url"],
        use_container_width=True
    )

# --------------------------------------------------
# SCHEDULE POST
# --------------------------------------------------

if "post_id" in st.session_state:

    st.divider()

    st.subheader(
        "📅 Schedule Post"
    )


    col1, col2 = st.columns(2)


    with col1:

        platform = st.selectbox(
            "Select Platform",

            [
                "Instagram",
                "Facebook"
            ]
        )


    with col2:

        post_date = st.date_input(
            "Select Date"
        )


    post_time = st.time_input(
        "Select Time"
    )


    if st.button(
        "📅 Schedule Post",
        use_container_width=True
    ):

        scheduled_at = (
            f"{post_date} "
            f"{post_time}:00"
        )


        schedule_post(

            post_id=st.session_state[
                "post_id"
            ],

            platform=platform,

            scheduled_at=scheduled_at
        )


        st.success(
            f"Post scheduled for {platform} "
            f"on {scheduled_at}"
        )


        st.rerun()


# --------------------------------------------------
# POST HISTORY
# --------------------------------------------------

st.divider()

st.subheader(
    "📚 Post History"
)


posts = get_all_posts()


if not posts:

    st.info(
        "No posts generated yet."
    )


else:

    for post in posts:

        (
    post_id,
    post_topic,
    post_image_prompt,
    post_caption,
    post_hashtags,
    post_image_path,
    post_status,
    post_platform,
    post_created_at,
    post_scheduled_at
) = post

        with st.expander(

            f"#{post_id} — "
            f"{post_topic} — "
            f"{post_status}"

        ):

            st.write(
                f"**Created:** "
                f"{post_created_at}"
            )


            st.write(
                f"**Status:** "
                f"{post_status}"
            )


            if post_platform:

                st.write(
                    f"**Platform:** "
                    f"{post_platform}"
                )


            if post_scheduled_at:

                st.write(
                    f"**Scheduled At:** "
                    f"{post_scheduled_at}"
                )


            st.markdown(
                "### 🎨 Image Prompt"
            )

            st.write(
                post_image_prompt
            )


            st.markdown(
                "### 📝 Caption"
            )

            st.write(
                post_caption
            )


            st.markdown(
                "### #️⃣ Hashtags"
            )

            st.write(
                post_hashtags
            )


            # Show generated image
            image_path = (
                f"generated/images/"
                f"post_{post_id}.png"
            )


            try:

                st.image(
                    image_path,
                    width=400
                )

            except Exception:

                pass