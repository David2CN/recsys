import pandas as pd
from flask import Flask, render_template
from recsys.recommender import get_poster, id2titles, item_predict


root_dir = "recsys/"
df = pd.read_csv(root_dir+"static/data/movielens2019_small.csv")

df.rename(columns={
    "movie_id": "movieId",
    "user_id": "userId",
    "tmdb_id": "tmdbId"
}, inplace=True)


def get_movies(kind="top", item_id=None, k=6):
    if kind == "top":
        ids = df["movieId"].sample(k)
    elif kind == "recs":
        ids = [item_id] + item_predict(item_id, k=k)

    movies = []
    for item in ids:
        print(item, type(item))
        # get poster link
        id_dict = {"img_link": get_poster(item)}

        # get movie title and rating
        t, r, td = id2titles(item)
        id_dict["title"] = f"{t} - {int(r*20)}%"

        # add movie id
        id_dict["movieId"] = item

        movies.append(id_dict)
    return movies


def create_app():

    app = Flask(__name__)

    @app.route("/")
    def index():
        movies = get_movies()
        print(movies)
        return render_template("index.html", movies=movies)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/show/<item_id>")
    def show_info(item_id):
        item_id = int(item_id)
        movie_recs = get_movies("recs", item_id=item_id)
        return render_template("info.html", movie_recs=movie_recs)

    return app
