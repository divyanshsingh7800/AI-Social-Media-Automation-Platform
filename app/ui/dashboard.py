import streamlit as st

from app.ui.post_ui import show_post_creator
from app.ui.schedule_ui import show_schedule
from app.ui.history_ui import show_history


def show_dashboard():

    show_post_creator()

    show_schedule()

    show_history()
