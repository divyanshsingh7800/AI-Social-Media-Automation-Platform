import streamlit as st

from app.services.database import get_posts_by_user


def show_history():

    st.divider()

    st.subheader("📚 Post History")

    user_id = st.session_state.get("user_id")

    if not user_id:
        return

    posts = get_posts_by_user(user_id)

    if not posts:

        st.info(
            "No posts generated yet."
        )

        return

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

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Status:** {post_status}"
                )

            with col2:

                if post_platform:

                    st.write(
                        f"**Platform:** "
                        f"{post_platform}"
                    )

            st.write(
                f"**Created:** "
                f"{post_created_at}"
            )

            if post_scheduled_at:

                st.write(
                    f"**Scheduled At:** "
                    f"{post_scheduled_at}"
                )

            if post_image_path:

                st.markdown(
                    "### 🖼️ Image"
                )

                try:

                    st.image(
                        post_image_path,
                        use_container_width=True
                    )

                except Exception:

                    st.warning(
                        "Image could not be displayed."
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