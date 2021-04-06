import pylast
import csv
import json
import logging
logging.basicConfig(level=logging.WARNING)

passwd_path = "hidden/passwdData.csv"
albums_info_path = "album_info/albums.csv"
dest_path = "album_info/last_fm_tags.json"

'''
Names in password csv file:

NAME            FIRST_KEY   SECOND_KEY
last_fm_api     API Key 	Shared Secret
spotify_api     Client ID 	Client Secret
last_fm_login   Login       Hashed Password 
'''


def read_passwords_from_csv(path):
    result = {}

    with open(path, "r", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for line in csv_reader:
            result[line[0]] = (line[1], line[2])  # result["name"] = ("first_key", "second_key")

    return result


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
            logging.warning(f'Album {artist} - {title} has 0 tags')

        return {tag.item.name: int(tag.weight) for tag in tags}

    except pylast.WSError:
        logging.warning(f"Album {artist} - {title} hasn't been found")
        return {}


def get_albums_tag(api_info, user_info, albums_info):
    network = pylast.LastFMNetwork(
        api_key=api_info[0],
        # api_secret=api_info[1],
        # username=user_info[0],
        # password_hash=user_info[1]
    )

    return [{"title": title, "artist": artist, "tags": get_tags(artist, title, network)} for artist, title in albums_info]


def write_to_json(data, path):
    with open(path, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4, sort_keys=True))


def main():
    passwords = read_passwords_from_csv(passwd_path)
    albums_info = read_album_info_from_csv(albums_info_path)

    tags = get_albums_tag(api_info=passwords["last_fm_api"],
                     user_info=passwords["last_fm_login"],
                     albums_info=albums_info)

    write_to_json(tags, dest_path)


if __name__ == '__main__':
    main()
