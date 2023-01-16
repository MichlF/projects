import pymongo
import time
import os
import yaml
import logging
import logging.config as logging_conf
import typing
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.dialects.postgresql import insert
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


def connect_mongoDB(
    db_name: str = "",
    collection_name: str = "",
    wait_time: int = 10,
    *args,
    **kwargs,
) -> tuple:
    """
    Creates client connected to MongoDB. Returns client and, if collection_name
    is defined, a collection from database.

    Parameters
    ----------
    db_name : str, optional
        Name of data base, by default None
    collection_name : str, optional
        Name of collection to be returned, by default None
    wait_time : int, optional
        Wait time before connecting to database, therby giving databases time
        to initialize, by default 10

    Returns
    -------
    tuple
        Contains client, and if collection_name is defined, the specified collection
        in that database

    Raises
    ------
    Exception
        Arbitrary exception if connection or collection checks failed.
    """
    try:
        assert isinstance(
            db_name, str
        ), f"Value '{db_name}' for parameter db_name is invalid."
        assert isinstance(
            collection_name, str
        ), f"Value '{collection_name}' for parameter collection_name is invalid."
    except AssertionError as e:
        logger.error("Assertion check failed: ", exc_info=True)
    # Wait for startup
    time.sleep(wait_time)
    # Build client and connect
    returnables = []
    try:
        client = pymongo.MongoClient(*args, **kwargs)
        client.server_info()["version"]  # verify if instance is genuine
        returnables.append(client)
        if collection_name:
            collection_object = client[db_name].get_collection(collection_name)
            returnables.append(collection_object)
        logging.info("Succesfully connected to mongoDB.")
    except Exception as e:
        logging.error("Failed to connect to mongoDB: ", exc_info=True)
        raise Exception("Check the log!") from e  # raise error for now

    return tuple(returnables)


def init_postgres(
    host: str, port: int, user: str, password: str, dbname: str, table_name: str
) -> tuple[typing.Any, typing.Any]:
    """
    Connect to postgres server and given database using SQLAlchemy.
    Also creates a table in that database. Table parameters are currently
    hardcoded to the function.

    Parameters
    ----------
    host : str
        Postgres server hostname or IPv4
    port : int
        Postgres port
    user : str
        Username of postgres server
    password : str
        Password of postgres server
    dbname : str
        Username of postgres database
    table_name : str
        Name of table to be retrieved from database

    Returns
    -------
    tuple[typing.Any, typing.Any]
        Returns SQLAlchemy engine for postgres server and specific table object
    """
    # Connect to postgres server
    pg_engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{dbname}",
        echo=False,
        pool_pre_ping=True,
    )
    # Create database dbname if it doesn't already exist
    if not database_exists(pg_engine.url):
        logging.info(f"Postgres: '{dbname}' database did not exists. Created it.")
        create_database(pg_engine.url)
    # Create table table_name if it doesn't exist
    pg_engine.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (post_id SERIAL PRIMARY KEY, date BIGINT, query_match VARCHAR(150), url VARCHAR(500) UNIQUE, subreddit VARCHAR(150), title VARCHAR(500), author VARCHAR(100), url_contained VARCHAR(500), sentiment FLOAT, content TEXT);"
    )
    # Get table object for later
    db_reddit_meta = MetaData()
    db_reddit_meta.reflect(bind=pg_engine)
    table_object = db_reddit_meta.tables[table_name]
    logging.info(f"Postgres: 'Post' table in '{dbname}' database initialized.")

    return pg_engine, table_object


def data_transform(collection_object: typing.Any) -> list[dict] | dict:
    """
    Transforms data from mongoDB collection to regular dictionary and adds
    sentiment score. Note: sentiment function is globally defined.

    Parameters
    ----------
    collection_object : typing.Any
        To-be-transformed collection from MongoDB

    Returns
    -------
    list[dict] | dict
        List of dicts holding transformed mongoDB data including sentiment score.
    """
    # We could use the sentiment score in order to filter out posts based on it,
    # but we don't do this here. We just want to show it along with the post.
    data_extracted = list(
        collection_object.find()
    )  # returns dicts of mongoDB collection entries (= postgres table rows)
    transformed = []
    for entry in data_extracted:
        # Add sentiment score of the post to db dict
        sentiment = senti.polarity_scores(entry["content"])
        entry.pop("_id")  # remove MongoDB's id
        entry.update({"sentiment": sentiment["compound"]})
        transformed.append(entry)

    return transformed


def data_store(
    sql_engine_object: typing.Any,
    table_object: typing.Any,
    data_transformed: list[dict] | dict,
    conflict_column: list[str] | str,
    rollback: bool = True,
):
    """
    Saves transformed data to postgres database in bulk.

    Parameters
    ----------
    sql_engine_object : typing.Any
        SQLAlchemy engine object for postgres server
    table_object : typing.Any
        Table object wherein data is to be inserted.
    data_transformed : list[dict] | dict
        Data to be stored to table.
    conflict_column : list[str] | str
        Executes SQL 'CONFLICT ON' command on given column
        Prevents adding the same post multiple times to the
        database.
    """
    # SQLAlchemy engine needs a list of strings
    if not isinstance(conflict_column, list):
        conflict_column = [conflict_column]
    # Dump our dict list data_transformed in table_name
    # We CONFLICT ON conflict_columns and do nothing to make sure we are not creating duplicate entries
    sql_engine_object.execute(
        insert(table_object).on_conflict_do_nothing(index_elements=conflict_column),
        data_transformed,
    )
    # # Note: As part of the ON CONFLICT resolve, the SERIAL post_id has been incremented even if no new
    # # row occurred b/c of ON CONFLICT DO NOTHING. That is by design. However, we can rollback the id
    # # to prevent gaps in the id:
    # if rollback:
    #     last_id = sql_engine_object.execute(
    #         f"SELECT setval('{table_object.name}_post_id_seq', MAX({table_object.name}.post_id)) FROM {table_object.name};"
    #     )
    #     last_id1 = last_id.fetchall()[0][0]
    #     sql_engine_object.execute(
    #         f"ALTER SEQUENCE posts_post_id_seq RESTART WITH {last_id1+1};"
    #     )
    #     # Note this doesn't do much in this version of the script because the on_conflic id increments
    #     # happen as part of the execution earlier. One way, to solve this issue would be not relying on
    #     # SQLalchemys insert function but rather raw SQL iterate over each new row with subsequent roll-
    #     # back.


if __name__ == "__main__":
    # Load environment vars
    load_dotenv()
    # Some variable paramater definitions
    update_time = int(os.getenv("LOG_UPDATE_TIME"))
    conflict_columns = "url"  # Ensure no double entries based on post url
    wait_time_job = 15
    wait_time_dbs = 15
    # Wait some time, 'till dbs are up and running
    time.sleep(wait_time_dbs)
    # Init logger and connect to databases
    init_logger()
    logger = logging.getLogger("etl")
    conn_str = f'mongodb://{os.getenv("MONGODB_HOST")}:{os.getenv("MONGODB_PORT")}'
    _, collection = connect_mongoDB(
        host=conn_str,
        db_name="db_reddit",
        collection_name="reddit_posts",
    )
    pg_engine, table_object = init_postgres(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DBNAME"),
        table_name="posts",
    )
    # ETL: Extract data from MongoDB, calculate sentiment score and load it with data together into the postgres db
    senti = SentimentIntensityAnalyzer()
    start_time = time.time()
    logger.info("")
    logger.info("Starting to work on ETL jobs...")
    while True:
        transformed = data_transform(
            collection
        )  # returns empty list, when collection is empty
        if transformed:
            data_store(pg_engine, table_object, transformed, conflict_columns)
        if time.time() - start_time > (update_time):
            logger.info("ETL app is still waiting to perform ETL jobs...")
            start_time = time.time()
        time.sleep(wait_time_job)
