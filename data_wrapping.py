import matplotlib.pyplot as plt
import numpy as np
import json

from time import time

JSON_PATH = "album_info/album_info.json"


def get_features_matrix(features, size):
    # data standarization. Every feature has expected value 0 and standard deviation 1.
    standardized = np.array([(features[:, feature] - features[:, feature].mean())
                             / features[:, feature].std() for feature in range(9)]).T

    # returns matrix of similarity between albums. Every value is a sum of distances between feature values of two albums. The smaller number is, the more similar albums are.
    differences = np.array([[np.sum(np.abs(standardized[alb_1, :] - standardized[alb_2, :]))
                             for alb_2 in range(size)] for alb_1 in range(size)])

    similarity = np.square(np.ones((size, size)) - differences / np.max(differences))
    # similarity = np.array([similarity[]])

    # distribution = [0 for i in range(101)]
    # x = [i for i in range(101)]
    # for album_a in range(len(similarity)):
    #     for album_b in range(len(similarity)):
    #         distribution[int(similarity[album_a][album_b] * 100)] += 1
    # plt.scatter(x, distribution)
    # plt.title("SPOTIFY ALBUM PAIRS")
    # plt.show()
    #
    # distribution = [0 for i in range(30)]
    # x = [i for i in range(30)]
    # for album_a in range(len(similarity)):
    #     album_similarity = 0
    #     for album_b in range(len(similarity)):
    #         album_similarity += similarity[album_a][album_b]
    #     distribution[int(album_similarity / 10)] += 1
    # plt.scatter(x, distribution)
    # plt.title("SPOTIFY EVERY ALBUM")
    # plt.show()

    return similarity


def get_tags_matrix(tags):
    tags_values = np.sqrt(np.array([[tag[1] for tag in album_tags] for album_tags in tags]))
    weights_sum = np.sum(tags_values, axis=1)
    tags_values = np.array(
        [np.divide(tags_weights, weights_sum[index]) for index, tags_weights in enumerate(tags_values)])
    tags = [[(tag[0], tags_values[alb_ind][tag_ind]) for tag_ind, tag in enumerate(album_tags)] for alb_ind, album_tags
            in enumerate(tags)]
    similarity = np.array([[np.sum(
        [[tag_1[1] + tag_2[1] if tag_1[0] == tag_2[0] else 0 for tag_2 in tags_2] for tag_1 in tags_1]) for tags_2 in
                            tags] for tags_1 in tags])

    # similarity = np.zeros([len(tags), len(tags)])
    # for album_a_index, album_a_tags in enumerate(tags):
    #     for album_b_index, album_b_tags in enumerate(tags):
    #         for album_a_tag in album_a_tags:
    #             for album_b_tag in album_b_tags:
    #                 if album_a_tag[0] == album_b_tag[0]:
    #                     similarity[album_a_index][album_b_index] += album_a_tag[1] + album_b_tag[1]

    # distribution = [0 for i in range(21)]
    # x = [i for i in range(21)]
    # for album_a_index, album_a_tags in enumerate(tags):
    #     for album_b_index, album_b_tags in enumerate(tags):
    #         distribution[(int)(similarity[album_a_index][album_b_index] * 10)] += 1
    # plt.scatter(x, distribution)
    # plt.title("LASTFM ALBUM PAIRS")
    # plt.show()
    #
    # distribution = [0 for i in range(50)]
    # x = [i for i in range(50)]
    # for album_a_index, album_a_tags in enumerate(tags):
    #     counter = 0
    #     for album_b_index, album_b_tags in enumerate(tags):
    #         if similarity[album_a_index][album_b_index] > 0:
    #             counter += 1
    #     distribution[counter // 10] += 1
    # plt.scatter(x, distribution)
    # plt.title("LASTFM FOUND ALBUMS WITH SAME >= 1 TAGS")
    # plt.show()
    #
    # distribution = [0 for i in range(50)]
    # x = [i for i in range(50)]
    # for album_a_index, album_a_tags in enumerate(tags):
    #     album_similarity = 0
    #     for album_b_index, album_b_tags in enumerate(tags):
    #         album_similarity += similarity[album_a_index][album_b_index]
    #     distribution[int(album_similarity / 10)] += 1
    # plt.scatter(x, distribution)
    # plt.title("LASTFM ALBUMS WEIGHTS SUM")
    # plt.show()

    return similarity / 2


def prepare_data(json_path):
    with open(json_path, "r") as file:
        albums_info = json.load(file)

    no_albums = len(albums_info)
    max_tags = max(map(lambda album: len(album["tags"]), albums_info))
    max_genres = max(map(lambda album: len(album["genre"]), albums_info))

    spotify_features = np.array([[v for v in album["features"].values()] for album in albums_info], dtype="f8")

    # lastfm_tags = np.array([[list(album['tags'].items())[tag_ind] if tag_ind < len(album['tags'].items()) else (None, 0) for tag_ind in range(max_tags)] for album in albums_info])
    lastfm_tags = np.zeros((no_albums, max_tags), dtype=[('tag_name', "U128"), ("value", "f4")])
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


def get_genres_matrix(data):
    def cos_sim_np(vec_a, vec_b, len_a, len_b):
        return np.sum(vec_a * vec_b)/(len_a*len_b)

    def all_k_grams(album_genres, k):
        result = {}
        for genre_name in album_genres:
            for i in range(len(genre_name) - k + 1):
                k_gram = genre_name[i:i+k]
                result.setdefault(k_gram, 0)
                result[k_gram] += 1
        return result

    def cos_sim_dict(dict_a, dict_b, len_a, len_b):
        value = 0
        if len_a == 0 or len_b == 0:
            return 0
        for key_a, val_a in dict_a.items():
            if key_a in dict_b:
                val_b = dict_b[key_a]
                value += val_a * val_b
        return value/(len_a*len_b)

    n = data.shape[0]

    general_generes = np.array(["rock", "blues", "jazz", "rap", "pop", "r&b", "hop", "folk", "punk",
                                "reggae", "country", "soul", "funk", "baroque", "metal", "chamber", "art", "electro",
                                "disco", "soft", "hard", "alternative", "grunge", "new wave"])

    squeezed_matrix = np.array([";".join(row) for row in data])
    no_occurrences = np.array([np.char.count(squeezed_matrix, genre_name) for genre_name in general_generes])
    unmatched_indicator = np.float_(np.all(no_occurrences == 0, axis=0))
    no_occurrences = np.vstack([no_occurrences, unmatched_indicator])      #adding "other" row

    genre_tf = np.log(1 + no_occurrences)
    no_documents_with_given_genre = np.sum(np.sign(no_occurrences), axis=1)
    terms_idf = np.log(1 + n/no_documents_with_given_genre)
    tf_idf = terms_idf[:, np.newaxis] * genre_tf



    a = time()
    lengths = np.linalg.norm(tf_idf, axis=0)
    genre_array = np.array([[cos_sim_np(tf_idf[:, i], tf_idf[:, j], lengths[i], lengths[j])
                            for i in range(n)] for j in range(n)])
    b = time()
    print(f': General genres similarity computation: {round(b - a, 4)} [s]')

    a = time()
    trigrams = [all_k_grams(album_genres, 3) for album_genres in data]
    trigrams_lengths = np.array([np.linalg.norm(list(dictionary.values())) for dictionary in trigrams])
    trigram_array = np.array([[cos_sim_dict(trigrams[i], trigrams[j],
                                            trigrams_lengths[i], trigrams_lengths[j])
                               for i in range(n)] for j in range(n)])
    b = time()
    print(f"Cosine similarity of trigrams {round(b-a, 4)} [s]")

    return (genre_array + trigram_array)/2


def wrangle(features_weight, tags_weight, genre_weight):
    spotify_data, lastfm_data, wiki_data, albums_info = prepare_data(JSON_PATH)

    a = time()
    alice_in_wonderland = get_features_matrix(spotify_data, len(spotify_data))
    b = time()
    print(f"Spotify total time: {round(b-a, 4)} [s]")

    a = time()
    cat_in_a_hat = get_tags_matrix(lastfm_data)
    b = time()
    print(f"Last fm total time: {round(b-a, 4)} [s]")

    a = time()
    betty_boop = get_genres_matrix(data=wiki_data)
    b = time()
    print(f"Wikipedia total time: {round(b-a, 4)} [s]")

    ###         FOR TESTING         ###
    final_matrix = features_weight * alice_in_wonderland +\
                   tags_weight * cat_in_a_hat + genre_weight * betty_boop

    #TO THINK OF
    final_matrix = np.array([(final_matrix[i, :] - final_matrix[i, :].mean()) / final_matrix[i, :].std() for i in range(len(final_matrix))])

    # album_index = 364
    album_index = 32
    print(albums_info[album_index]['title'])
    similarity_list = [(i, final_matrix[album_index][i]) for i in range(len(final_matrix))]
    similarity_list.sort(key=lambda x: x[1], reverse=True)
    del similarity_list[0]
    acc = 0
    for album in similarity_list:
        if album[1] == 0:
            acc += 1
        print(f"{albums_info[album[0]]['title']:40}, {albums_info[album[0]]['artist']:30}, {album[1]:10}")

    x = [album_similarity[1] for album_similarity in similarity_list]
    plt.hist(x, bins=40)
    plt.show()

    print(f'Percent of 0 similarities {100*acc/len(albums_info)}')


# _, _, genres_data, _ = prepare_data(JSON_PATH)
# hahaha = get_genres_matrix(genres_data)
# n = hahaha.shape[0]
# print(np.count_nonzero(hahaha)/(n*n))
wrangle(3, 3, 1)
