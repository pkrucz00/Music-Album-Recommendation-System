import pylast
import csv
import json
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


logging.basicConfig(level=logging.WARNING)


last_fm_api_key = "194ebdf5b49fa996adb5ffb9bfcab1db"
passwd_path = "hidden/passwdData.csv"
albums_info_path = "album_info/albums.csv"
dest_path = "album_info/last_fm_tags.json"



os.environ['SPOTIPY_CLIENT_ID'] = 'a7dfe025796347eeb0e630dc21b2abb4'
os.environ['SPOTIPY_CLIENT_SECRET'] = '3a3144d353cf42ff95b3f04a129c10a5'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
features_list = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
                     'liveness', 'valence', 'tempo']


def get_features(album, artist):
    album_info = spotify.search(q = "album:{} artist:{}".format(album, artist), type="album")['albums']['items']
    if len(album_info) == 0:
        logging.warning(f"Album {artist} - {album} hasn't been found on spotify")
        return {}

    album_features = {feature:0 for feature in features_list}
    tracks = spotify.album_tracks(album_info[0]['uri'])
    album_duration = 0

    for track in tracks['items']:
        track_duration = spotify.audio_features([track['id']])[0]['duration_ms']
        track_features = spotify.audio_features([track['id']])[0]
        for feature in features_list:
            album_features[feature] += track_features[feature] * track_duration
        album_duration += track_duration

    for feature in features_list:
        album_features[feature] /= album_duration

    return album_features


# ----- unnecessary as of right now --------
# '''
# Names in password csv file:
#
# NAME            FIRST_KEY   SECOND_KEY
# last_fm_api     API Key 	Shared Secret
# spotify_api     Client ID 	Client Secret
# last_fm_login   Login       Hashed Password
# '''
#
#
# def read_passwords_from_csv(path):
#     result = {}
#
#     with open(path, "r", newline='') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=";")
#         for line in csv_reader:
#             result[line[0]] = (line[1], line[2])  # result["name"] = ("first_key", "second_key")
#
#     return result
# -------------------------------------------


def read_album_info_from_csv(path):
    result = []

    with open(path, "r", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for line in csv_reader:
            result.append((line[0], line[1]))

    return result[1:]


def get_tags(artist, title, network):
    logging.info(f'Artist: {artist:30},Title: {title:30}')
    if " and " in artist or " and " in title:
        title = title.replace(" and ", " & ")
        artist = artist.replace(" and ", " & ")
    try:
        album = network.get_album(title=title, artist=artist)
        # artist = network.get_artist(artist_name=artist)    # might be needed in the future
        # artist.get_top_tags()
        tags = album.get_top_tags(limit=10)
        if len(tags) == 0:
            logging.warning(f'Album {artist} - {title} has 0 tags on last.fm')

        return {tag.item.name: int(tag.weight) for tag in tags}

    except pylast.WSError:
        logging.warning(f"Album {artist} - {title} hasn't been found")
        return {}


def get_albums_info(api_key, albums_info):
    network = pylast.LastFMNetwork(
        api_key=api_key
        # api_secret=api_info[1],
        # username=user_info[0],
        # password_hash=user_info[1]
    )

    return [{"title": title, "artist": artist, "tags": get_tags(artist, title, network), "features": get_features(title, artist)} for artist, title in
            albums_info]


def write_to_json(data, path):
    with open(path, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4, sort_keys=True))


def main():
    # passwords = read_passwords_from_csv(passwd_path)
    albums_info = read_album_info_from_csv(albums_info_path)

    tags = get_albums_info(api_key=last_fm_api_key,
                          albums_info=albums_info)

    write_to_json(tags, dest_path)


if __name__ == '__main__':
    main()
