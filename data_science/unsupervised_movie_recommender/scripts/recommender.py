import requests
from dataclasses import dataclass
import numpy as np
import dill as pickle
from pandas import DataFrame, Series, concat, merge
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Recommender:
    """
    Recommender class that assumes that recommender models for each method are already trained
    """

    model_paths: dict = None
    movies_information: DataFrame = None
    model_nmf: DataFrame = None
    model_nbcfilter: DataFrame = None

    def __post_init__(self) -> None:
        """loads in existing models or initializes the creation of models"""
        # Define the paths and then load existing data and model objects
        self.model_paths = {
            "movies_information": "model_objects/movies_information.pkl",
            "model_nmf": "model_objects/model_nmf.pkl",
            "nbcfilter_data": "model_objects/nbcfilter_data.pkl",
        }
        for name, model_path in self.model_paths.items():
            file_path = Path(model_path)
            if file_path.is_file():
                with open(model_path, "rb") as file:
                    setattr(self, name, pickle.load(file))
            else:
                print(
                    f"{name} not found. Creating a new model when there is no pickle file for it"
                    " already is not implemented, yet"
                )

    def recommend_model_random(self, user_movies: dict) -> DataFrame:
        """generates random movie recommendations"""
        # Remove the movies the user has already watched and randomly shuffle the df
        user_matrix = self.movies_information.loc[
            ~self.movies_information["title"].isin(user_movies.keys()), :
        ]
        user_matrix = user_matrix.sample(frac=1)

        return user_matrix

    def recommend_model_nmf(self, user_movies: dict) -> DataFrame:
        """generates recommendations based on Non-Negative Matrix Factorization"""
        # Get Q and P matrix
        q_mat = self.model_nmf.components_
        # For P matrix: create new user, replace default ratings of movies seen by user with their ratings
        new_user = self.movies_information["avg_ratings_pitem"].values
        movies_seen_idx = self.movies_information[
            self.movies_information["title"].isin(user_movies.keys())
        ].index.values
        new_user[movies_seen_idx] = list(user_movies.values())
        new_user_p_mat = self.model_nmf.transform(new_user.reshape(1, -1))
        # Generate a user matrix with rating predictions and remove the movies the user has already watched
        new_user_predictions = np.dot(new_user_p_mat, q_mat).flatten()
        user_matrix = concat(
            [
                self.movies_information,
                Series(new_user_predictions.flatten(), name="user_predictions"),
            ],
            axis=1,
        )
        user_matrix = user_matrix.loc[~user_matrix["title"].isin(user_movies), :]

        return user_matrix

    def recommend_model_nbcfilter(self, user_movies: dict, num_neighbors: int = 5) -> DataFrame:
        """generates recommendations based on Neighborhood-based collaborative filtering"""
        # create new user, replace default ratings of movies seen by user with their ratings
        new_user = np.zeros(np.shape(self.movies_information["avg_ratings_pitem"]))
        movies_seen_idx = self.movies_information[
            self.movies_information["title"].isin(user_movies.keys())
        ].index.values
        new_user[movies_seen_idx] = list(user_movies.values())
        cosim_table = self._nbcfilter_get_cosim_table(new_user=new_user, data=self.nbcfilter_data)
        movies_unseen = self.nbcfilter_data.T.index[
            self.nbcfilter_data.T["new_user"] == 0
        ].tolist()
        neighbors = (
            cosim_table.loc["new_user", :]
            .sort_values(ascending=False)
            .index[1 : num_neighbors + 1]
            .tolist()
        )
        predicted_rating_df = self._nbcfilter_get_movie_predictions(
            cosim_table=cosim_table, movies_unseen=movies_unseen, neighbors=neighbors
        )
        user_matrix = merge(self.movies_information, predicted_rating_df, on="title")

        return user_matrix

    def _nbcfilter_get_cosim_table(self, new_user: np.ndarray, data: DataFrame) -> DataFrame:
        """internal method that calculates the cosimilarity table"""
        data.loc["new_user"] = new_user
        cosim_table = cosine_similarity(self.nbcfilter_data)
        cosim_table = DataFrame(
            cosim_table,
            index=self.nbcfilter_data.index,
            columns=self.nbcfilter_data.index,
        )

        return cosim_table

    def _nbcfilter_get_movie_predictions(
        self, cosim_table: DataFrame, movies_unseen: list, neighbors: list
    ) -> DataFrame:
        """internal method that returns the movie predictions based on neighborhood-based collaborative filtering"""
        predicted_ratings_movies = []
        for movie in movies_unseen:
            others_seen = list(
                self.nbcfilter_data.T.columns[self.nbcfilter_data.T.loc[movie] > 0]
            )  # find people who watched the unseen movies
            numerator = 0
            min_similarity = 1e-9
            # go through users who are similar but watched the film
            for user in neighbors:
                if user in others_seen:
                    # extract the ratings and similarities for similar users
                    rating = self.nbcfilter_data.T.loc[movie, user]
                    similarity = cosim_table.loc["new_user", user]
                    # predict rating based on the averaged rating of the neighbors
                    # sum(ratings)/number of users OR sum(ratings * similarity)/sum(similarities)
                    numerator += rating * similarity
                    min_similarity += similarity
            predicted_ratings = round(numerator / min_similarity, 1)
            predicted_ratings_movies.append([predicted_ratings, movie])
        predicted_rating_df = DataFrame(
            predicted_ratings_movies, columns=["user_predictions", "title"]
        )

        return predicted_rating_df

    def get_recommendations(
        self, user_matrix: DataFrame, request_object, recommendations
    ) -> tuple[list[str, ...], list[str, ...], list[str, ...]]:
        """
        returns the poster link titles and genres of the movies depending on the model chosen and
        the users input regarding the recommendation criteria (i.e., restrictions on number, year
        genre or avg rating of other users)
        """
        # Check for recommendations refinement POST
        if request_object.method == "POST":
            recommendations = self.process_recommender_post(
                request_form=request_object.form,
                user_matrix=user_matrix,
                recommendations=recommendations,
            )
        # If search was refined, return top X rated movies from refined search. Otherwise just top 5
        if len(recommendations) > 0:
            recommendations = self.recommend_top(
                user_matrix=recommendations,
                n_recommendations=int(request_object.form["n-recommendations"]),
            )
        else:
            recommendations = self.recommend_top(user_matrix=user_matrix, n_recommendations=5)
        # Based on our recommendations, retrieve all information we need to present the results
        poster_links = list(recommendations["poster_links"])
        titles = list(recommendations["title"])
        genres = list(recommendations["genres"])

        return poster_links, titles, genres

    def process_recommender_post(
        self, user_matrix: DataFrame, request_form: dict, recommendations: DataFrame
    ) -> DataFrame:
        """produces the output of the recommender including handling of post request to refine search"""

        if request_form["refine-type"] == "none":
            recommendations = user_matrix
        elif request_form["refine-type"] == "year":
            recommendations = self.recommend_restrict_year(
                user_matrix=user_matrix, year=int(request_form["refine-value-year"])
            )
        elif request_form["refine-type"] == "genre":
            recommendations = self.recommend_restrict_genre(
                user_matrix=user_matrix, genres=request_form["refine-value-genre"].split(",")
            )
        elif request_form["refine-type"] == "avgratings":
            recommendations = self.recommend_restrict_avgratings_pitem(
                user_matrix=user_matrix,
                rating_threshold=float(request_form["refine-value-avgratings"]),
            )
        else:
            raise ValueError("No or unknown 'refine-type' value")

        return recommendations

    def recommend_top(self, user_matrix: DataFrame, n_recommendations: int = 5) -> DataFrame:
        """picks the recommendations out of all movies, just based on the model predictions"""
        try:  # non-random model has user_predictions
            return user_matrix.sort_values("user_predictions", ascending=False).head(
                n_recommendations
            )
        except:  # random model has no user_predictions
            return user_matrix.head(n_recommendations)

    def recommend_restrict_year(self, user_matrix: DataFrame, year: int) -> DataFrame:
        """picks the recommendations out of movies made since year year (inclusive)"""
        # Remove entries with missing year
        user_matrix = user_matrix.loc[~user_matrix.loc[:, "year_only"].isna(), :]
        return user_matrix[user_matrix.loc[:, "year_only"].astype(int) >= year]

    def recommend_restrict_genre(self, user_matrix: DataFrame, genres: list) -> DataFrame:
        """picks the recommendations out of movies from specific genre/s"""
        print("in function", list(genres))
        return user_matrix.loc[
            user_matrix["genres"].apply(lambda x: any(genre in x for genre in genres)), :
        ]

    def recommend_restrict_avgratings_pitem(
        self, user_matrix: DataFrame, rating_threshold: float = 0.0
    ) -> DataFrame:
        """picks the recommendations out of movies that exceed a certain average rating"""

        return user_matrix[
            user_matrix.loc[:, "avg_ratings_pitem"].astype(float) >= float(rating_threshold)
        ]


def main():
    recommend = Recommender()


if __name__ == "__main__":
    main()
