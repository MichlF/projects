import time
import requests
import os
import yaml
import logging
import typing
import logging.config as logging_conf
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

# run pipreqs /path/to/project to get requirements.txt


def init_logger(
    default_path: str = "logging.yaml",
    default_level: typing.Any = logging.INFO,
    env_key: str = "LOG_CFG",
):
    """
    Initializes a logger with settings from separate YAML file.

    Parameters
    ----------
    default_path : str, optional
        Path to YAML file containing the logger settings, by default "logging.yaml"
    default_level : typing.Any, optional
        Python logging object determining the logging level, by default logging.INFO
    env_key : str, optional
        _description_, by default "LOG_CFG"
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging_conf.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    logging.info("Logging started...")


def write_payload(
    slack_msg: str,
    author: str,
    subreddit: str,
    query: str,
    time_ago: str,
    urllink: str = None,
) -> dict:
    """
    Writes the JSON payload interpreted by the Slack App (Bot).
    Is called by generate_bot_msg(). Template from Block Kit Builder:
    https://app.slack.com/block-kit-builder

    Parameters
    ----------
    slack_msg : str
        Predefined main text for the slack bot message.
    author : str
        Author of the reddit post
    subreddit : str
        Subreddit the post was posted in
    query : str
        Matched query
    time_ago : str
        Time since posting. Note: currently relatively inaccurate
        and static.
    urllink : str, optional
        If provided, posts the url contained in the reddit post,
        by default None

    Returns
    -------
    dict
        JSON-like dictionary containing Slack app markup with
        specified text.
    """

    json = {
        "text": f"Found a new post matching {query} !",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":mega:   LATEST REDDIT POST   :mega:",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"{slack_msg}"}},
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": "https://assets.stickpng.com/thumbs/580b57fcd9996e24bc43c531.png",
                        "alt_text": "Reddit user",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*{author}* posted this {time_ago}s ago in {subreddit}, matched query {query}.",
                    },
                ],
            },
        ],
    }

    return json


def generate_bot_msg(
    slack_webhook: str,
    query_results: typing.Any,
    old_post_id: int,
    time_passed: int = 120,
) -> int:
    """
    Generates the message for the Slack bot and posts it through
    provied webhook. Returns an iterator int to only post new
    posts from the database.

    Parameters
    ----------
    slack_webhook : str
        Slack webhook
    query_results : typing.Any
        The results set from querying the postgres database
    old_post_id : typing.Any
        Current post_id, will be overwritten if a new post was 
        processed.
    time_passed : int, optional
        Iterator int for post_id in the postgres database.
        Prevents repeated posting of messages, by default 
        120 seconds or 2 minutes.

    Returns
    -------
    int
        An iterator int to only post new posts from
        the database.
    """
    for row in query_results.fetchall():
        # We only want to post messages that we haven't posted
        # before in this session (i.e., since the bot was started)
        # and/or that are not older than a certain amount of time.
        # The session constraint is already happening through the
        # SQL SELECT outside the function. The time constraint
        # doesn't work with SQLAlchemy/psycopg, so we do it here.
        # Calculate time passed since post
        time_ago = round(
            (
                datetime.now() - datetime.fromtimestamp(float(row["date"]))
            ).total_seconds()
        )  # date is stored in string-ed unix format
        if time_ago >= time_passed:  # time constraint
            continue
        else:
            logger.info(f"Found a new post (id {row['post_id']}).")
            base_url = "https://www.reddit.com"
            # Emoji
            if row["sentiment"] > 0.25:
                emoji = ":smile:"
            elif row["sentiment"] <= -0.25:
                emoji = ":cry:"
            else:
                emoji = ":neutral_face:"
            # If post has content, provide sentiment score. Otherwise just post contained link.
            if row["content"]:
                str_sentiment = (
                    f"\nThe post's Sentiment score: {row['sentiment']} - {emoji}"
                )
                if (row["url_contained"]) and (
                    row["url_contained"] != base_url + row["url"]
                ):  # If no url contained, PRAW fills in the post link. Then, we shouldn't assume a link was provided.
                    str_sentiment += f"\nPost also contained a link: <{row['url_contained']}|check it out !>"
            else:
                str_sentiment = f"\nPost contained no text, but a link: <{row['url_contained']}|check it out !>"
            # Build slack bot body text and post it
            slack_msg = (
                f"_'{row['title']}'_\nTake a look at it <{base_url+row['url']}|on reddit>."
                + str_sentiment
            )
            bot_msg = write_payload(
                slack_msg=slack_msg,
                author=row["author"],
                subreddit=row["subreddit"],
                query=row["query_match"],
                time_ago=time_ago,
            )
            requests.post(url=slack_webhook, json=bot_msg)
            # Update the oldest id to prevent repeated messaging
            old_post_id = row["post_id"]
            logger.info("Message about new post successfully sent to Slack !")

    return old_post_id


if __name__ == "__main__":
    # Load environment vars
    load_dotenv()
    # Some variable paramater definitions
    update_time = int(os.getenv("LOG_UPDATE_TIME"))
    wait_time_job = 15
    wait_time_dbs = 60
    # Wait some time, till dbs are up and running
    time.sleep(wait_time_dbs)
    # Let's go!
    init_logger()
    logger = logging.getLogger("slack_bot")
    pg = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}",
        echo=False,
        pool_pre_ping=True,
    )
    old_post_id = 0
    start_time = time.time()
    while True:
        # Prevent picking the same post multiple times
        # f"SELECT * FROM posts WHERE posts.post_id > {old_post_id} AND posts.date >= NOW() - INTERVAL '2 MINUTES';"
        try:
            results_set = pg.execute(
                f"SELECT * FROM posts WHERE posts.post_id > {old_post_id};"
            )  # empty list if empty query
        except:
            logger.warning(
                "Error in query. Maybe there is no post in the database, yet?",
                exc_info=True,
            )
        if results_set:
            try:
                old_post_id = generate_bot_msg(
                    os.getenv("SLACK_WEBHOOK_URL"), results_set, old_post_id
                )
            except:
                logger.warning(
                    "Couldn't generate a bot message. Maybe there is no post in the database, yet?",
                    exc_info=True,
                )
        if time.time() - start_time > (update_time):
            logger.info(f"Slack bot is still waiting to post something to Slack...")
            start_time = time.time()
        time.sleep(wait_time_job)
