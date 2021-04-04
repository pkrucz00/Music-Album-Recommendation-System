import pylast
import csv

passwd_path = "passwdData.csv"

'''
Names in password csv file:

NAME            FIRST_KEY   SECOND_KEY
last_fm_api     API Key 	Shared Secret
spotify_api     Client ID 	Client Secret
last_fm_login   Login       Hashed Password 
'''


def read_from_csv(path):
    result = {}

    with open(path, "r", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for line in csv_reader:
            result[line[0]] = (line[1], line[2])  # result["name"] = ("first_key", "second_key")

    return result


def print_albums_tag(api_info, user_info):
    network = pylast.LastFMNetwork(
        api_key=api_info[0],
        api_secret=api_info[1],
        username=user_info[0],
        password_hash=user_info[1]
    )
    album = network.get_album(title="Pain is Beauty", artist="Chelsea Wolfe")
    artist = network.get_artist(artist_name="Chelsea Wolfe")
    tags = album.get_top_tags()

    # please, God, remove the misogynistic, troll and offencive tags, thank you
    for tag in tags:
        print(f'Tag name: {tag.item.name:18s} ,tag weight: {int(tag.weight)}')
    print()
    tags = artist.get_top_tags()
    for tag in tags:
        print(f'Tag name: {tag.item.name:18s} ,tag weight: {int(tag.weight)}')


def main():
    passwords = read_from_csv(passwd_path)
    print_albums_tag(api_info=passwords["last_fm_api"],
                     user_info=passwords["last_fm_login"])


if __name__ == '__main__':
    main()
