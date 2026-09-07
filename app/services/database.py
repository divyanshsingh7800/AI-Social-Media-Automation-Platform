import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "social_media.db"


def get_connection():

    return sqlite3.connect(DATABASE_PATH)

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
        """
        
    ) 

    # Existing posts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic TEXT NOT NULL,

            image_prompt TEXT NOT NULL,

            caption TEXT NOT NULL,

            hashtags TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Draft',

            platform TEXT,

            created_at TEXT NOT NULL,

            scheduled_at TEXT

        ) 
        """
        
    )

# --------------------------------------------------
# SOCIAL ACCOUNTS
# --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS social_accounts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            platform TEXT NOT NULL,

            access_token TEXT,

            refresh_token TEXT,

            created_at TEXT NOT NULL,

            UNIQUE(user_id, platform)

        )
        """
    )

    connection.commit()
    connection.close()

def migrate_database():

    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute(
        "PRAGMA table_info(posts)"
    )

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE posts
            ADD COLUMN user_id INTEGER
            """
        )

        connection.commit()

    connection.close()

def save_post(
    user_id,
    topic,
    image_prompt,
    caption,
    hashtags
):

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    hashtags_text = " ".join(
        hashtags
    )

    cursor.execute(
    """
    INSERT INTO posts
    (
        user_id,
        topic,
        image_prompt,
        caption,
        hashtags,
        status,
        created_at
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        user_id,
        topic,
        image_prompt,
        caption,
        hashtags_text,
        "Draft",
        created_at
    )
)

    connection.commit()

    post_id = cursor.lastrowid

    connection.close()

    return post_id


def update_image_path(
    post_id,
    image_path
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE posts

        SET image_path = ?

        WHERE id = ?
        """,
        (
            image_path,
            post_id
        )
    )

    connection.commit()

    connection.close()

def get_all_posts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            image_prompt,
            caption,
            hashtags,
            image_path,
            status,
            platform,
            created_at,
            scheduled_at

        FROM posts

        ORDER BY id DESC
        """
    )

    posts = cursor.fetchall()

    connection.close()

    return posts



def get_post(post_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            image_prompt,
            caption,
            hashtags,
            image_path,
            status,
            platform,
            created_at,
            scheduled_at

        FROM posts

        WHERE id = ?
        """,
        (post_id,)
    )

    post = cursor.fetchone()

    connection.close()

    return post



def update_post_status(
    post_id,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE posts

        SET status = ?

        WHERE id = ?
        """,
        (
            status,
            post_id
        )
    )

    connection.commit()

    connection.close()



def schedule_post(
    post_id,
    platform,
    scheduled_at
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE posts

        SET
            status = 'Scheduled',
            platform = ?,
            scheduled_at = ?

        WHERE id = ?
        """,
        (
            platform,
            scheduled_at,
            post_id
        )
    )

    connection.commit()

    connection.close()


def get_due_posts():

    connection = get_connection()

    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        SELECT
            id,
            topic,
            image_prompt,
            caption,
            hashtags,
            image_path,
            status,
            platform,
            created_at,
            scheduled_at

        FROM posts

        WHERE status = 'Scheduled'

        AND scheduled_at <= ?

        ORDER BY scheduled_at ASC
        """,
        (current_time,)
    )

    posts = cursor.fetchall()

    connection.close()

    return posts

# --------------------------------------------------
# SAVE SOCIAL ACCOUNT
# --------------------------------------------------

def save_social_account(
    user_id,
    platform,
    access_token,
    refresh_token=None
):

    connection = get_connection()

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO social_accounts
        (
            user_id,
            platform,
            access_token,
            refresh_token,
            created_at
        )

        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            platform,
            access_token,
            refresh_token,
            created_at
        )
    )

    connection.commit()
    connection.close()

def update_post_content(
    post_id,
    caption,
    hashtags
):

    connection = get_connection()

    cursor = connection.cursor()

    hashtags_text = " ".join(
        hashtags
    )

    cursor.execute(
        """
        UPDATE posts

        SET
            caption = ?,
            hashtags = ?

        WHERE id = ?
        """,
        (
            caption,
            hashtags_text,
            post_id
        )
    )

    connection.commit()

    connection.close()

# --------------------------------------------------
# UPDATE IMAGE PROMPT
# --------------------------------------------------

def update_image_prompt(
    post_id,
    image_prompt
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE posts

        SET image_prompt = ?

        WHERE id = ?
        """,
        (
            image_prompt,
            post_id
        )
    )

    connection.commit()

    connection.close()

# --------------------------------------------------
# CREATE USER
# --------------------------------------------------

def create_user(name, email, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
                created_at
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return user_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# --------------------------------------------------
# GET USER BY EMAIL
# --------------------------------------------------

def get_user_by_email(email):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            created_at

        FROM users

        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user

def get_posts_by_user(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            topic,
            image_prompt,
            caption,
            hashtags,
            image_path,
            status,
            platform,
            created_at,
            scheduled_at

        FROM posts

        WHERE user_id = ?

        ORDER BY id DESC
        """,
        (user_id,)
    )

    posts = cursor.fetchall()

    connection.close()

    return posts


# --------------------------------------------------
# GET SOCIAL ACCOUNT
# --------------------------------------------------

def get_social_account(
    user_id,
    platform
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            platform,
            access_token,
            refresh_token,
            created_at

        FROM social_accounts

        WHERE user_id = ?
        AND platform = ?
        """,
        (
            user_id,
            platform
        )
    )

    account = cursor.fetchone()

    connection.close()

    return account


# --------------------------------------------------
# GET USER SOCIAL ACCOUNTS
# --------------------------------------------------

def get_social_accounts(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            platform,
            created_at

        FROM social_accounts

        WHERE user_id = ?

        ORDER BY platform
        """,
        (user_id,)
    )

    accounts = cursor.fetchall()

    connection.close()

    return accounts


# --------------------------------------------------
# DELETE SOCIAL ACCOUNT
# --------------------------------------------------

def delete_social_account(
    user_id,
    platform
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM social_accounts

        WHERE user_id = ?
        AND platform = ?
        """,
        (
            user_id,
            platform
        )
    )

    connection.commit()
    connection.close()
