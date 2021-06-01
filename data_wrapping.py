import numpy as np
import json
import logging
from time import time

JSON_PATH = "album_info/album_info.json"


def log_time_debug_message(func, message):
    """Helper function for showing time of a function"""
    t1 = time()
    result = func()
    t2 = time()
    logging.debug(message + f": {round(t2 - t1, 5)} [s]")
    return result


def prepare_data(json_path):
    """Getting and preparing data from json"""
    with open(json_path, "r") as file:
        albums_info = json.load(file)

    no_albums = len(albums_info)
    max_tags = max(map(lambda album: len(album["tags"]), albums_info))
    max_genres = max(map(lambda album: len(album["genre"]), albums_info))

    spotify_features = np.array(
        [[v for v in album["features"].values()] for album in albums_info], dtype="f8")

    lastfm_tags = np.zeros((no_albums, max_tags),
                           dtype=[('tag_name', "U128"), ("value", "f4")])
    for i in range(no_albums):
        album_tags = list(albums_info[i]["tags"].items())
        for j in range(len(album_tags)):
            lastfm_tags[i][j] = album_tags[j]

    wiki_generes = np.zeros((no_albums, max_genres), dtype="U32")
    for i in range(no_albums):
        album_genres = albums_info[i]["genre"]
        no_genres = len(album_genres)
        for j in range(max_genres):
            wiki_generes[i][j] = album_genres[j] if j < no_genres else ""

    # get_tags_matrix(lastfm_tags)
    return spotify_features, lastfm_tags, wiki_generes, albums_info


def get_features_matrix(features, size):
    """Wrangling spotify data"""
    # data standardization. Every feature has expected value 0 and standard deviation 1.
    standardized = np.array([(features[:, feature] - features[:, feature].mean())
                             / features[:, feature].std() for feature in range(9)]).T

    # returns matrix of similarity between albums.
    # Every value is a sum of distances between feature values of two albums.
    # The smaller number is, the more similar albums are.
    differences = np.array([[np.sum(np.abs(standardized[alb_1, :] - standardized[alb_2, :]))
                             for alb_2 in range(size)] for alb_1 in range(size)])

    similarity = np.square(np.ones((size, size)) - differences / np.max(differences))

    return similarity


def get_tags_matrix(tags):
    """Wrangling lastfm data"""
    tags_values = np.sqrt(np.array([[tag[1] for tag in album_tags] for album_tags in tags]))
    weights_sum = np.sum(tags_values, axis=1)
    tags_values = np.array(
        [np.divide(tags_weights, weights_sum[index])
         for index, tags_weights in enumerate(tags_values)])

    tag_dictionaries = [{tag[0]: tags_values[alb_ind][tag_ind]
                         for tag_ind, tag in enumerate(album_tags)}
                        for alb_ind, album_tags in enumerate(tags)]

    similarity = np.array([[np.sum([[val_1 + tags_2[tag_name] if tag_name in tags_2 else 0]
                                    for tag_name, val_1 in tags_1.items()])
                            for tags_2 in tag_dictionaries] for tags_1 in tag_dictionaries])

    return similarity / 2  # divided by 2 because max val in matrix can be 2


def get_genres_matrix(data):
    """Wrangling wikipedia data"""
    def cos_sim_np(vec_a, vec_b, len_a, len_b):
        """:returns similarity between two vectors, a and b, with lengths len_a and len_b"""
        return np.sum(vec_a * vec_b) / (len_a * len_b)

    def all_k_grams(album_genres, k):
        """:returns all k grams of a list of generes"""
        result = {}
        for genre_name in album_genres:
            for i in range(len(genre_name) - k + 1):
                k_gram = genre_name[i:i + k]
                result.setdefault(k_gram, 0)
                result[k_gram] += 1
        return result

    def cos_sim_dict(dict_a, dict_b, len_a, len_b):
        """:returns cosine similarity between two k-gram dicts"""
        value = 0
        if len_a == 0 or len_b == 0:
            return 0
        for key_a, val_a in dict_a.items():
            if key_a in dict_b:
                val_b = dict_b[key_a]
                value += val_a * val_b
        return value / (len_a * len_b)

    n = data.shape[0]  # Number of albums

    general_generes = np.array(["rock", "blues", "jazz", "rap", "pop", "r&b", "hip hop", "folk", "punk",
                                "reggae", "country", "soul", "funk", "baroque", "metal", "chamber", "art", "electro",
                                "disco", "soft", "hard", "alternative", "grunge", "new wave", "trip hop"])

    squeezed_matrix = np.array([";".join(row) for row in data])
    no_occurrences = np.array([np.char.count(squeezed_matrix, genre_name) for genre_name in general_generes])
    unmatched_indicator = np.float_(np.all(no_occurrences == 0, axis=0))
    no_occurrences = np.vstack([no_occurrences, unmatched_indicator])  # adding "other" row

    genre_tf = np.log(1 + no_occurrences)
    no_documents_with_given_genre = np.sum(np.sign(no_occurrences) + 10e-7, axis=1)
    terms_idf = np.log(1 + n / no_documents_with_given_genre)
    tf_idf = terms_idf[:, np.newaxis] * genre_tf

    lengths = np.linalg.norm(tf_idf, axis=0)
    genre_array = np.array([[cos_sim_np(tf_idf[:, i], tf_idf[:, j],
                                        lengths[i], lengths[j])
                             for i in range(n)] for j in range(n)])

    trigrams = [all_k_grams(album_genres, 3) for album_genres in data]
    trigrams_lengths = np.array([np.linalg.norm(list(dictionary.values()))
                                 for dictionary in trigrams])
    trigram_array = np.array([[cos_sim_dict(trigrams[i], trigrams[j],
                                            trigrams_lengths[i], trigrams_lengths[j])
                               for i in range(n)] for j in range(n)])

    return (genre_array + trigram_array) / 2


def wrangle(json_path, features_weight=2, tags_weight=2, genre_weight=1):
    """Computing all the final similarity matrix based on individual similarity matrices"""
    spotify_data, lastfm_data, wiki_data, albums_info = prepare_data(json_path)

    alice_in_wonderland = \
        log_time_debug_message(
            lambda: get_features_matrix(spotify_data, len(spotify_data)),
            "Spotify total time")

    cat_in_a_hat = \
        log_time_debug_message(
            lambda: get_tags_matrix(lastfm_data),
            "Last fm total time")  # last_fm matrix

    betty_boop = \
        log_time_debug_message(
            lambda: get_genres_matrix(data=wiki_data),
            "Wikipedia total time")  # wikipedia matrix

    # computing the final matrix by adding all wages element-wise
    final_matrix = features_weight * alice_in_wonderland + \
                   tags_weight * cat_in_a_hat + genre_weight * betty_boop

    # standardization
    final_matrix = [(final_matrix[i, :] - final_matrix[i, :].mean()) / final_matrix[i, :].std() for i in
                    range(len(final_matrix))]

    return final_matrix
