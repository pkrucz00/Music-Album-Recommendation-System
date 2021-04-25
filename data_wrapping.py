import numpy as np
import json

JSON_PATH = "album_info/album_info.json"


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


print(prepare_data(JSON_PATH))
