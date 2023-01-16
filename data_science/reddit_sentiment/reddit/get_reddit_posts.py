# For a tutorial to connect to the reddit api using request, see:
# https://alpscode.com/blog/how-to-use-reddit-api/
# And for PRAW specifically, see:
# https://praw.readthedocs.io/en/stable/index.html
# https://github.com/praw-dev/praw/blob/827a4f210c114fc0d70bbac15276654e76272946/docs/index.rst
# To monitor your reddit apps, see:
# https://old.reddit.com/prefs/apps/

import logging
import typing
import time
import re
from datetime import datetime
from dataclasses import dataclass


@dataclass
class RedditCrawler:
    """
    Class to crawl reddit for posts matching specific queries.
    """

    authed_praw_instance: typing.Any = object()
    store_db: bool = True
    collection: typing.Any = None

    def __post_init__(self):
        """
        Initializes logger object
        """
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _findWholeWord(word: str) -> typing.Any:
        """
        Staticmethod to match whole words (case-insensitive) to a given string.

        Parameters
        ----------
        word : str
            Word to match

        Returns
        -------
        typing.Any
            Regex compile object with match string or NoneType object if no match
        """
        # Returns found word if match or None if no match
        return re.compile(r"\b({0})\b".format(word), flags=re.IGNORECASE).search

    def stream_query(
        self,
        search_query: str | list[str],
        subreddit: str = "python",
        search_where: str = "all",
        update_time: int = 5 * 60,
    ):
        """
        Initializes streamer that searches for query-matching posts in either the
        title or title and text of a given subreddit.

        Parameters
        ----------
        search_query : str | list[str]
            Query word/s to match.
        subreddit : str, optional
            Subreddit that should be searched. Can handle multiple
            subreddits joined by +, by default "python".
        search_where : str, optional
            Match query either only in title ("title") or in both title and the
            posts body/text, by default "all".
        update_time : int, optional
            Time to pass until app signals it's still alive, by default
            5 * 60 or 5 minutes.
        """
        try:
            assert search_where in [
                "all",
                "title",
            ], f"Value '{search_where}' for parameter search_where is invalid."
        except AssertionError as e:
            self.logger.error("Assertion check failed: ", exc_info=True)
        try:
            subreddit = self.authed_praw_instance.subreddit(subreddit)
        except Exception as e:
            self.logger.error(
                f"Subreddit '{subreddit}' could not be initiated: ", exc_info=True
            )
        if not isinstance(
            search_query, list
        ):  # Transform to list, in case of single (string) query
            search_query = [search_query]
        self.logger.info("")
        self.logger.info(
            f"Streaming new reddit posts and looking for '{search_query}' in '{search_where}' of subreddit/s '{subreddit}'."
        )
        self.logger.info("")
        start_time = time.time()
        for submission in subreddit.stream.submissions(skip_existing=True):
            self._process_submission(submission, search_query, search_where)
            if time.time() - start_time > (
                update_time
            ):  # Note: this only runs when we enter the stream, which is after we've found the first post
                self.logger.info(
                    "Reddit app is still looking for new posts matching your query..."
                )
                start_time = time.time()

    def _process_submission(
        self, submission: typing.Any, search_query: list[str], search_where: str
    ):
        """
        Writes query-matching reddit posts into a dictionary ready to store to
        the mongoDB. Called by stream_query().

        Parameters
        ----------
        submission : typing.Any
            PRAWs streamed submission.
        search_query : list[str]
            Query word/s to match.
        search_where : str
            Match query either only in title ("title") or in both title and the
            posts body/text, by default "all".
        """
        for query in search_query:
            if (self._findWholeWord(query)(submission.title)) or (
                (search_where == "all")
                and (self._findWholeWord(query)(submission.selftext))
            ):  # does whole word matching
                posting = {
                    "db_store_date": datetime.utcnow(),
                    "query_match": query,
                    "url": submission.permalink,
                    "date": int(submission.created),
                    "subreddit": submission.subreddit.url,
                    "title": submission.title,
                    "author": submission.author.name,
                    "url_contained": submission.url,
                    "content": submission.selftext,
                }
                self.logger.info(
                    f"Found a new reddit post matching the query '{query}' in subreddit '{submission.subreddit.url}' titled '{submission.title}'."
                )
                if self.store_db:
                    self._store_to_mongodb(posting)
                # Prevent the same post from being stored multiple times
                break

    def _store_to_mongodb(self, posting: dict, t_deleted: int = 120):
        """
        Stores reddit post dictionary and sets the entry to be deleted
        from the mongoDB after a given amount of time. Called by
        _process_submission().

        Parameters
        ----------
        posting : dict
            Contains detailes on query-matching posts (submissions)
        t_deleted : int, optional
            Time, in seconds, until entry is deleted. Note: Internal
            deletion happens as a repeating subprocess every 60 seconds.
        """
        try:
            self.collection.create_index(
                "db_store_date", expireAfterSeconds=t_deleted
            )  # UTC datetime must be chosen for expireAfterSeconds
            self.collection.insert_one(posting)
            self.logger.info("Successfully saved post to MongoDB.")
        except Exception as e:
            self.logger.warning("Could not save post to MongoDB:", exc_info=True)
