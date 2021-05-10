from data_wrapping import wrangle
from json import load

JSON_PATH = "album_info/album_info.json"

#tuples indexation
INDEX = 0
ALB_NAME = 1
GRADE =  2

RATING = 2


class MarsCore:
    def __init__(self, json_path):
        with open(json_path, "r") as file:
            albums_info = load(file)

        self.no_albums = len(albums_info)  # number of albums
        self.album_titles = [albums_info[i]["title"] for i in range(self.no_albums)]
        self.album_artists = [albums_info[i]["artist"] for i in range(self.no_albums)]

        self.result_list = [(i, 0) for i in range(self.no_albums)]  # (index, curr_rating)
        self.already_chosen = []    # soon: (index, grade)

