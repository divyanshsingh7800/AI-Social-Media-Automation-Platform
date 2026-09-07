from app.services.database import update_post_status


def publish_post(post):

    post_id = post[0]
    topic = post[1]
    image_prompt = post[2]
    caption = post[3]
    hashtags = post[4]
    image_path = post[5]
    status = post[6]
    platform = post[7]
    scheduled_at = post[9]


    print(
        f"Publishing post #{post_id}"
    )

    print(
        f"Topic: {topic}"
    )

    print(
        f"Platform: {platform}"
    )

    print(
        f"Image: {image_path}"
    )

    print(
        f"Scheduled At: {scheduled_at}"
    )

    print(
        "Publishing simulation successful."
    )


    update_post_status(
        post_id,
        "Published"
    )
