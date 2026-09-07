from apscheduler.schedulers.background import BackgroundScheduler

from app.services.database import (
    get_due_posts,
    initialize_database
)

from app.services.publisher import publish_post


def check_scheduled_posts():

    print(
        "Checking scheduled posts..."
    )

    posts = get_due_posts()

    if not posts:

        print(
            "No posts due."
        )

        return


    print(
        f"Found {len(posts)} post(s) ready to publish."
    )


    for post in posts:

        try:

            publish_post(post)

        except Exception as e:

            print(
                f"Failed to publish post #{post[0]}:"
            )

            print(e)


def start_scheduler():

    initialize_database()

    scheduler = BackgroundScheduler()

    scheduler.add_job(

        check_scheduled_posts,

        "interval",

        minutes=1,

        id="social_media_scheduler",

        replace_existing=True
    )

    scheduler.start()

    print(
        "Social Media Scheduler started."
    )

    return scheduler
