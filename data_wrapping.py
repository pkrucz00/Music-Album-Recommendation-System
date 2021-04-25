import numpy as np
import json

JSON_PATH = "album_info/album_info.json"

def get_features_matrix(features, size):
    #data standarization. Every feature has expected value 0 and standard deviation 1.
    standardized = np.array([(features[:, feature] - features[:, feature].mean()) / features[:, feature].std() for feature in range(9)]).T

    #returns matrix of similarity between albums. Every value is a sum of distances between feature values of two albums. The smaller number is, the more similar albums are.
    return np.array([[np.sum(np.abs(standardized[alb_1, :] - standardized[alb_2, :])) for alb_2 in range(size)] for alb_1 in range(size)])



def prepare_data(json_path):
    with open(json_path, "r") as file:
        albums_info = json.load(file)

    no_albums = len(albums_info)
    max_tags = max(map(lambda album: len(album["tags"]), albums_info))
    max_genres = max(map(lambda album: len(album["genre"]), albums_info))
    # print(list(map(lambda x: (x["artist"], x["title"]), filter(lambda album: len(album["genre"]) > 7, albums_info))))

    spotify_features = np.array([[v for v in album["features"].values()] for album in albums_info], dtype="f4")
    lastfm_tags = np.zeros((no_albums, max_tags), dtype=[('tag_name', "U128"), ("value", "f4")])
    for i in range(no_albums):
        album_tags = list(albums_info[i]["tags"].items())
        no_tags = len(album_tags)
        for j in range(max_tags):
            lastfm_tags[i][j] = album_tags[j] if j < no_tags else None

    wiki_generes = np.zeros((no_albums, max_genres), dtype="U32")
    for i in range(no_albums):
        album_genres = albums_info[i]["genre"]
        no_genres = len(album_genres)
        for j in range(max_genres):
            wiki_generes[i][j] = album_genres[j] if j < no_genres else None

    return spotify_features, lastfm_tags, wiki_generes


def get_genres_matrix(data):
    def cos_sim(tab, i, j):
        return np.sum(tab[:, i]*tab[:, j])/(np.linalg.norm(tab[:, i])*np.linalg.norm(tab[:, j]))

    general_generes = np.array(["rock", "blues", "jazz", "hip-hop", "rap", "pop", "r&b", "soul", "funk"])

    squeezed_matrix = np.array([";".join(row) for row in data])

    genre_vectors = np.sign(np.array([np.char.count(squeezed_matrix, genre_name) for genre_name in general_generes]))
    n = genre_vectors.shape[1]

    return np.array([[cos_sim(genre_vectors, i, j) for i in range(n)] for j in range(n)])



spotify_data, lastfm_data, wiki_data = prepare_data(JSON_PATH)
marek_marucha = get_genres_matrix(data=wiki_data)
print(marek_marucha)
