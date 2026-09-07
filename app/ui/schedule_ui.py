import streamlit as st

from app.services.database import schedule_post


def show_schedule():

    if "post_id" not in st.session_state:

        return

    st.divider()

    st.subheader("📅 Schedule Post")

    col1, col2 = st.columns(2)

    with col1:

        platform = st.selectbox(
            "Select Platform",
            [
                "Instagram",
                "Facebook",
                "X"
            ],
            key="schedule_platform"
        )

    with col2:

        post_date = st.date_input(
            "Select Date",
            key="schedule_date"
        )

    post_time = st.time_input(
        "Select Time",
        key="schedule_time"
    )

    if st.button(
        "📅 Schedule Post",
        width="stretch"
    ):

        scheduled_at = (
            f"{post_date} {post_time}"
        )

        try:

            schedule_post(
                post_id=st.session_state[
                    "post_id"
                ],
                platform=platform,
                scheduled_at=scheduled_at
            )

            st.success(
                f"Post scheduled for {platform} "
                f"on {scheduled_at} ✅"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Failed to schedule post."
            )

            st.code(str(e))
