from data_wrapping import wrangle
from json import load
import logging

logging.basicConfig(level=logging.DEBUG)

JSON_PATH = "album_info/album_info.json"

# tuples indexation
INDEX = 0
RATING = 1


class MarsCore:
    """
    Stores and computes information for every album. That includes:
        - basic info (titles, artist)
        - similarity marix between every album
        - result list with all albums ranked by similarity to graded albums
        - already chosen albums with indexes and grades of graded albums"""
    def __init__(self, json_path):
        """
        Constructs MarsCore object based on data wrangling module

        :param json_path: path with information about albums
        """
        with open(json_path, "r") as file:
            albums_info = load(file)

        self.no_albums = len(albums_info)  # number of albums
        self.album_titles = [albums_info[i]["title"] for i in range(self.no_albums)]
        self.album_artists = [albums_info[i]["artist"] for i in range(self.no_albums)]

        self.similarity_matrix = wrangle(json_path)
        self.result_list = [(i, 0) for i in range(self.no_albums)]  # (index, curr_rating)
        self.already_chosen = {}  # {index: grade}

    def choose(self, index, grade):
        """Grading an album with index with a given grade"""
        logging.debug(f"Chosen album: {self.album_titles[index]} by {self.album_artists[index]}")
        self.already_chosen[index] = grade
        self.__update_result_list(index, grade)

    def unchoose(self, index):
        """Deleting album from the graded albums list and reverting it to result list"""
        logging.debug(f"Chosen album: {self.album_titles[index]} by {self.album_artists[index]}")
        old_grade = self.already_chosen.pop(index)
        new_rating = sum([grade*self.similarity_matrix[index][i] for i, grade in self.already_chosen.items()])
        self.__update_result_list(index, -old_grade, [(index, new_rating)])

    def __update_result_list(self, index, grade, base_list=None):
        new_result_list = base_list if base_list is not None else []
        for i, curr_rating in self.result_list:
            if i != index:
                similarity = self.similarity_matrix[i][index]  # [index][i] czy [i][index]?
                new_rating = curr_rating + grade * similarity
                new_result_list.append((i, new_rating))
        self.result_list = sorted(new_result_list, key=lambda x: x[RATING], reverse=True)

    def __str__(self):
        """For debug purposes"""
        already_chosen_info = [f"{self.album_titles[index]} by {self.album_artists[index]}" \
                               f" with grade {grade}"
                               for index, grade in self.already_chosen.items()]
        best_10_albums = [f"{self.album_titles[elem[INDEX]]} by {self.album_artists[elem[INDEX]]}"
                         for elem in self.result_list[:10]]
        result_string = f"Already chosen albums:\n"
        result_string += "\n".join(already_chosen_info)
        result_string += f"\n\nBest 10 albums so far:\n"
        result_string += "\n".join(best_10_albums)

        return result_string
