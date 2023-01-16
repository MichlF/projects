import os
import yaml
import praw
import time
import pymongo
import logging
import typing
import json
import logging.config as logging_conf
from get_reddit_posts import RedditCrawler
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
    logging.info("")
    logging.info("Starting a new logging session...")
    logging.info("")


def auth_oauth(
    client_id: str,
    client_secret: str,
    user_agent: str,
    username: str,
    password: str,
    *args,
    **kwargs
) -> typing.Any:
    """
    Perform authentication on reddit via your reddit app. Currently only password-driven
    using provided app credentials and user login data.

    Parameters
    ----------
    client_id : str
        Reddit app client id
    client_secret : str
        Reddit app client secret
    user_agent : str
        Reddit app user agent
    username : str
        Reddit user name
    password : str
        Reddit user password

    Returns
    -------
    typing.Any
        Authenticated PRAW object instance

    Raises
    ------
    failed_auth
        Error when being unable to authenticate.
    """
    try:
        authed_praw_ins = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username,
            *args,
            **kwargs
        )
        # Check authorization
        authed_praw_ins.user.me()
        logging.info("Successfully authenticated.")
    except Exception as failed_auth:
        logging.error("Could not authenticate. Raise error for now to force restart.", exc_info=True)
        raise failed_auth

    return authed_praw_ins


if __name__ == "__main__":
    # Load environment vars
    load_dotenv()
    # Some variable paramater definitions
    reddit_query = json.loads(os.getenv("REDDIT_QUERY"))
    subreddits = os.getenv("REDDIT_SUBREDDITS")
    search_where = os.getenv("REDDIT_SEARCH_WHERE")
    wait_time_dbs = 10
    # Wait some time, till dbs are up and running
    time.sleep(wait_time_dbs)
    # Initialize logger
    init_logger()
    # Initialize MongoDB and create a db and collection
    try:
        conn_str = f'mongodb://{os.getenv("MONGODB_HOST")}:{os.getenv("MONGODB_PORT")}'
        client = pymongo.MongoClient(host=conn_str)
        client.server_info()["version"]  # verify if instance is genuine
        db = client["db_reddit"]
        collection = db["reddit_posts"]
    except Exception as connection_fail:
        logging.error("Issue with connecting to MongoDB. Raise error for now !", exc_info=True)
        raise connection_fail
    # Get oauth token / authenticated praw instance
    authed_reddit = auth_oauth(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
    )
    # Search reddit (or subreddits) for particular key words
    reddit_bot = RedditCrawler(
        authed_praw_instance=authed_reddit, collection=collection, store_db=True
    )
    reddit_bot.stream_query(
        reddit_query,
        subreddit=subreddits,
        search_where=search_where,
        update_time=int(os.getenv("LOG_UPDATE_TIME"))
    )
