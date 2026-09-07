import streamlit as st

from app.services.database import (
    save_post,
    update_image_path,
    update_image_prompt,
    update_post_content
)

from app.services.gemini_service import generate_social_content
from app.services.image_service import generate_image


def show_post_creator():

    st.divider()

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

                    content = generate_social_content(
                        topic
                    )

                    st.session_state[
                        "content"
                    ] = content

                    st.session_state[
                        "topic"
                    ] = topic

                    post_id = save_post(
                        user_id=st.session_state[
                            "user_id"
                        ],
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

                    st.session_state[
                        "post_id"
                    ] = post_id

                    image_filename = (
                        f"post_{post_id}.png"
                    )

                    with st.spinner(
                        "Generating AI image..."
                    ):

                        image_path = generate_image(
                            content["image_prompt"],
                            image_filename
                        )

                    if image_path:

                        st.session_state[
                            "image_path"
                        ] = image_path

                        update_image_path(
                            post_id,
                            image_path
                        )

                    st.success(
                        "Content and image generated successfully! 🎉"
                    )

                except Exception as e:

                    st.error(
                        "Content generation failed."
                    )

                    st.code(str(e))


    # --------------------------------------------------
    # GENERATED CONTENT
    # --------------------------------------------------

    if "content" not in st.session_state:

        return


    content = st.session_state[
        "content"
    ]

    st.divider()

    st.subheader(
        "📋 Generated Content"
    )


    # --------------------------------------------------
    # IMAGE
    # --------------------------------------------------

    if st.session_state.get(
        "image_path"
    ):

        st.markdown(
            "### 🖼️ Generated Image"
        )

        st.image(
            st.session_state[
                "image_path"
            ],
            use_container_width=True
        )


    # --------------------------------------------------
    # IMAGE PROMPT
    # --------------------------------------------------

    st.markdown(
        "### 🎨 Image Prompt"
    )

    image_prompt = st.text_area(
        "Image generation prompt",
        value=content["image_prompt"],
        height=200,
        key="post_image_prompt"
    )


    # --------------------------------------------------
    # CAPTION
    # --------------------------------------------------

    st.markdown(
        "### 📝 Caption"
    )

    caption = st.text_area(
        "Social media caption",
        value=content["caption"],
        height=200,
        key="post_caption"
    )


    # --------------------------------------------------
    # HASHTAGS
    # --------------------------------------------------

    st.markdown(
        "### #️⃣ Hashtags"
    )

    hashtags = st.text_area(
        "Hashtags",
        value=" ".join(
            content["hashtags"]
        ),
        height=100,
        key="post_hashtags"
    )


    # --------------------------------------------------
    # SAVE EDITS
    # --------------------------------------------------

    if st.button(
        "💾 Save Changes",
        use_container_width=True
    ):

        try:

            hashtag_list = [
                tag.strip()
                for tag in hashtags.split()
                if tag.strip()
            ]

            update_post_content(
                st.session_state["post_id"],
                caption,
                hashtag_list
            )

            update_image_prompt(
                st.session_state["post_id"],
                image_prompt
            )

            st.session_state[
                "content"
            ] = {
                "image_prompt": image_prompt,
                "caption": caption,
                "hashtags": hashtag_list
            }

            st.success(
                "Changes saved successfully! ✅"
            )

        except Exception as e:

            st.error(
                "Failed to save changes."
            )

            st.code(str(e))


    # --------------------------------------------------
    # REGENERATE IMAGE
    # --------------------------------------------------

    if st.button(
        "🔄 Regenerate Image",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Generating a new image..."
            ):

                image_filename = (
                    f"post_{st.session_state['post_id']}.png"
                )

                image_path = generate_image(
                    image_prompt,
                    image_filename
                )

            if image_path:

                st.session_state[
                    "image_path"
                ] = image_path

                update_image_path(
                    st.session_state[
                        "post_id"
                    ],
                    image_path
                )

                st.success(
                    "New image generated successfully! 🎉"
                )

                st.rerun()

        except Exception as e:

            st.error(
                "Image regeneration failed."
            )

            st.code(str(e))