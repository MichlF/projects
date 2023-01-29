from flask import Flask, render_template, request, session, flash
from scripts.recommender import Recommender

app = Flask(__name__)
app.secret_key = "A-super-secret-key"  # need to set one if we use session
recommend = Recommender()
movies = recommend.movies_information["title"].values


@app.route("/", methods=["GET", "POST"])
def index(movies=movies):
    """Creates main landing page"""
    # Reset recommendations for this session, and create movies_added if it doesn't exist
    session["recommendations"] = {}
    if not session.get("movies_added"):
        session["movies_added"] = {}
    movies_added = session["movies_added"]
    # If user gives input (generates POST), we update movies_added with the movie+rating
    # If no post is generate, we assume the page has been reloaded or loaded for the first
    # time, triggering a reset of movies_added
    if request.method == "POST":
        movie_title = request.form["movie-title"]
        rating = request.form["rating"]
        if movie_title not in movies:
            flash("Sorry, I don't know this movie. Please choose a movie I know!")
        else:
            if movie_title not in movies_added:
                movies_added[movie_title] = rating
                session["movies_added"] = movies_added
                flash(
                    f"'{movie_title}' rated {movies_added[movie_title]} added to your list of"
                    f" {len(movies_added)} movies!"
                )
            else:
                flash(
                    f"You've already added '{movie_title}' with rating"
                    f" {movies_added[movie_title]} to your list !"
                )
    else:
        session["movies_added"] = {}

    return render_template("index.html", movie_titles=movies)


@app.route("/random_recommender", methods=["GET", "POST"])
def random_recommender():
    """a naive/random recommender"""
    recommendations = session.get("recommendations")
    movies_added = session.get("movies_added")
    user_matrix = recommend.recommend_model_random(user_movies=movies_added)
    poster_links, titles, genres = recommend.get_recommendations(
        user_matrix=user_matrix, request_object=request, recommendations=recommendations
    )

    return render_template(
        "recommendations.html", titles=titles, poster_links=poster_links, genres=genres
    )


@app.route("/nmf_recommender", methods=["GET", "POST"])
def nmf_recommender():
    """a recommender based on non-negative matrix factorization"""
    recommendations = session.get("recommendations")
    movies_added = session.get("movies_added")
    user_matrix = recommend.recommend_model_nmf(user_movies=movies_added)
    poster_links, titles, genres = recommend.get_recommendations(
        user_matrix=user_matrix, request_object=request, recommendations=recommendations
    )

    return render_template(
        "recommendations.html", titles=titles, poster_links=poster_links, genres=genres
    )


@app.route("/nbcfilter_recommender", methods=["GET", "POST"])
def nbcfilter_recommender():
    """a recommender based on neighborhood-based collaborative filtering"""
    recommendations = session.get("recommendations")
    movies_added = session.get("movies_added")
    user_matrix = recommend.recommend_model_nbcfilter(user_movies=movies_added)
    poster_links, titles, genres = recommend.get_recommendations(
        user_matrix=user_matrix, request_object=request, recommendations=recommendations
    )

    return render_template(
        "recommendations.html", titles=titles, poster_links=poster_links, genres=genres
    )


@app.route("/clear_movies", methods=["POST"])
def clear_movies():
    """Removes all movies on the list"""
    session["movies_added"] = {}

    return "Cleared the seen movie list !"


def main():
    app.run(debug=False, port=4242)


if __name__ == "__main__":
    main()
