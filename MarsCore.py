from data_wrapping import wrangle
from json import load

JSON_PATH = "album_info/album_info.json"

# tuples indexation
INDEX = 0
GRADE = 1

RATING = 1


class MarsCore:
    def __init__(self, json_path):
        with open(json_path, "r") as file:
            albums_info = load(file)

        self.no_albums = len(albums_info)  # number of albums
        self.album_titles = [albums_info[i]["title"] for i in range(self.no_albums)]
        self.album_artists = [albums_info[i]["artist"] for i in range(self.no_albums)]

        self.similarity_matrix = wrangle(json_path)
        self.result_list = [(i, 0) for i in range(self.no_albums)]  # (index, curr_rating)
        self.already_chosen = {}  # soon: {index: grade}

    def choose(self, index, grade):
        if not -2 <= grade <= 2:
            return

        def get_elem_with_index(elem_list, ind):
            result = list(filter(lambda x: x[0] == ind, elem_list))
            return result[0] if result else None

        # print(f"Chosen album: {self.album_titles[index]} by {self.album_artists[index]}")
        album_tuple = get_elem_with_index(elem_list=self.result_list, ind=index)
        self.result_list.remove(album_tuple)
        self.already_chosen[index] = grade

        new_result_list = []
        for i, curr_rating in self.result_list:
            if i != index:
                similarity = self.similarity_matrix[i][index]  # [index][i] czy [i][index]?
                new_rating = curr_rating + grade * similarity
                new_result_list.append((i, new_rating))

        self.result_list = sorted(new_result_list, key=lambda x: x[1], reverse=True)

    def __str__(self):
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


# wangjangle = MarsCore(json_path=JSON_PATH)
# wangjangle.choose(39, 2)
# wangjangle.choose(379, 2)
# print(wangjangle)
