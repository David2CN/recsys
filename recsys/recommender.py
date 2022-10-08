import pandas as pd
import requests
import json
import random
from PIL import Image


root_dir = "recsys/"
df = pd.read_csv(root_dir+"static/data/movielens2019_small.csv")

df.rename(columns={
    "movie_id": "movieId",
    "user_id": "userId",
    "tmdb_id": "tmdbId"
}, inplace=True)

item_similarity = pd.read_parquet(root_dir+"static/data/item_similarity.parquet")
item_similarity.columns = [int(i) for i in item_similarity.columns]
item_similarity.index = [int(i) for i in item_similarity.index]


def id2titles(item_id):
    """return a string containing the title, average rating and genres for
    recomended movies.
    """
    try:
        mask = df["movieId"] == item_id
        title, tmdbId = df[mask][["title", "tmdbId"]].values[0]
        ratings = df[mask].groupby("title")["rating"].agg(["min", "max", "mean"])
        rating = round((0.5*ratings["max"] + 0.4*ratings["mean"] + 0.1*ratings["min"]).values[0], 2)
    except Exception as e:
        print(e, "id2titles")
        return None
    return [title, rating, tmdbId]


def item_predict(item_id, k=6):
    """given a movie id, return the top k most similar movies using
    the cosine similarity.
    returns: indices [movie Ids]
    """
    try:
        item_similarities = item_similarity[item_id].sort_values(ascending=True)
        top_k = item_similarities.index[1:k+1]
        extra = random.sample([i for i in item_similarities.index if i not in top_k and i != item_id], 3)
        res = list(top_k) + extra
        random.shuffle(res)
    except Exception as e:
        print(e, "Check here!")
        return None
    return res


def get_poster(item_id):
    # get poster url
    headers = {'Accept': 'application/json'}
    payload = {'api_key': 'b928107b0a1e32311fed48c4fd6235e6'}
    response = requests.get("http://api.themoviedb.org/3/configuration", params=payload, headers=headers)
    response = json.loads(response.text)
    base_url = response['images']['base_url'] + 'w185'

    try:
        # get correct movie id
        t, r, movie_id = id2titles(item_id)

        # Query themoviedb.org API for movie poster path.
        movie_url = 'http://api.themoviedb.org/3/movie/{:}/images'.format(movie_id)
        response = requests.get(movie_url, params=payload, headers=headers)
        file_path = json.loads(response.text)['posters'][0]['file_path']
    except Exception as e:
        print(e)
        file_path=""

    return base_url + file_path


def show_rec(id, show=False):
    try:
        t, r, tmdb_id = id2titles(id)
        print(f"{t} - {r}/5\n{tmdb_id, id}")
        image_url = get_poster(id)
        im = Image.open(requests.get(image_url, stream=True).raw)
    except:
        error_url = "static/image/img_error.png"
        im = Image.open(error_url)

    if show:
        im.show()
