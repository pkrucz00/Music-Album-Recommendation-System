from MarsCore import MarsCore
import tkinter as tk
from tkinter import ttk

from functools import partial
from time import time
from math import ceil
from PIL import ImageTk, Image
import logging

INDEX = 0
RATING = 1
JSON_PATH = "album_info/album_info.json"
album_covers = "album_info/album_covers/"

logging.basicConfig(level=logging.DEBUG)


class LoopState:
    def __init__(self, chunk_length, mars_object):
        self.mars_object = mars_object

        self.chunk_length = chunk_length
        self.curr_chunk_index = 0

        self.searched_phrase = ""
        # No. ALL albums to display (including albums on other pages)
        self.display_list = mars_object.result_list

    def rate_album(self, index, rate):
        log_time_debug_message(
            lambda: self.mars_object.choose(index, rate),
            'Time of giving grade (adding similarities, sorting, etc.)')
        self.__show_modifications()

    def del_album(self, index):
        log_time_debug_message(
            lambda: self.mars_object.unchoose(index),
            'Time of deleting grade')
        self.__show_modifications()

    def __show_modifications(self):
        log_time_debug_message(
            self.set_display_list,
            "Time of resorting the list")
        log_time_debug_message(
            lambda: update(self),
            'Time of updating the root')

    def increment_chunk_index(self, event=None):
        self.curr_chunk_index += 1
        update(self)

    def decrement_chunk_index(self, event=None):
        self.curr_chunk_index -= 1
        update(self)

    def can_click_left(self):
        return self.curr_chunk_index > 0

    def can_click_right(self):
        return (self.curr_chunk_index + 1) * self.chunk_length < len(self.display_list)

    def set_display_list(self):
        if self.searched_phrase == '':
            self.display_list = self.mars_object.result_list
        else:
            titles = list(map(lambda title: title.lower(), self.mars_object.album_titles))
            artists = list(map(lambda artist: artist.lower(), self.mars_object.album_artists))
            result_list = self.mars_object.result_list
            self.display_list = list(filter(
                lambda elem: self.searched_phrase in titles[elem[INDEX]] or
                             self.searched_phrase in artists[elem[INDEX]],
                result_list))

    def set_searched_phrase(self, new_phrase):
        self.searched_phrase = new_phrase.lower()
        self.set_display_list()
        self.curr_chunk_index = 0
        update(self)

    def clear_search(self, search_bar):
        search_bar.delete(0, len(search_bar.get()))
        self.set_searched_phrase("")  # setting search phrase to BLANK resets the search

    def get_truncated_list(self):
        display_list = self.display_list
        return display_list[self.chunk_length * self.curr_chunk_index:
                            self.chunk_length * (self.curr_chunk_index + 1)]

    def get_no_displayed_albums(self):
        return len(self.display_list)

    def get_no_total_albums(self):
        return len(self.mars_object.result_list)

    def get_no_chunks(self):
        return ceil(self.get_no_displayed_albums() / self.chunk_length)


def log_time_debug_message(func, message):
    t1 = time()
    func()
    t2 = time()
    logging.debug(message + f": {round(t2 - t1, 5)} [s]")


def boolean_to_button_constants(expression):
    return tk.NORMAL if expression else tk.DISABLED





def update(state):
    mars_core = state.mars_object
    for ele in root.winfo_children():
        ele.destroy()
    # creating left slidebar for albums sorted (to rank)
    not_chosen = tk.LabelFrame(root, border=2)
    not_chosen.pack(side='left', fill='both', expand=1)

    canvas_left = tk.Canvas(not_chosen)
    canvas_left.pack(side='left', fill='both', expand=1)

    scrollbar_left = ttk.Scrollbar(not_chosen, orient='vertical', command=canvas_left.yview)
    scrollbar_left.pack(side='right', fill='y')

    canvas_left.configure(yscrollcommand=scrollbar_left.set)
    canvas_left.bind('<Configure>', lambda e: canvas_left.configure(scrollregion=canvas_left.bbox('all')))

    display_window_left = tk.Frame(canvas_left)
    canvas_left.create_window((0, 0), window=display_window_left, anchor='nw')

    # buttons for traversing the list
    left_button = tk.Button(display_window_left, text="left",
                            command=state.decrement_chunk_index,
                            state=boolean_to_button_constants(state.can_click_left()),
                            padx=7, pady=5)
    chunk_num_label = tk.Label(display_window_left,
                               text=f"{state.curr_chunk_index + 1} out of {state.get_no_chunks()}")
    right_button = tk.Button(display_window_left, text="right",
                             command=state.increment_chunk_index,
                             state=boolean_to_button_constants(state.can_click_right()),
                             padx=7, pady=5)
    left_button.grid(row=0, column=0)
    chunk_num_label.grid(row=0, column=1)
    right_button.grid(row=0, column=2, columnspan=5)

    if state.can_click_left(): root.bind("<Left>", state.decrement_chunk_index)
    else: root.unbind("<Left>")

    if state.can_click_right(): root.bind("<Right>", state.increment_chunk_index)
    else: root.unbind("<Right>")

    # searchbar
    search_label = tk.LabelFrame(display_window_left, border=0)
    search_bar = tk.Entry(search_label,
                          width=30)
    search_button = tk.Button(search_label,
                              command=lambda: state.set_searched_phrase(search_bar.get()),
                              text="Search", padx=10, pady=5)
    clear_button = tk.Button(search_label,
                             command=lambda: state.clear_search(search_bar),
                             text="Clear", padx=10, pady=5)

    search_bar.grid(row=0, column=0, padx=5, ipady=5)
    search_button.grid(row=0, column=1, padx=5)
    clear_button.grid(row=0, column=2, padx=5)

    search_label.grid(row=1, column=1, pady=10, columnspan=3)

    # filling slidebar with albums
    truncated_list = state.get_truncated_list()
    global cover
    cover = [None for _ in range(len(truncated_list))]

    for index, entry in enumerate(truncated_list):
        try:
            cover[index] = ImageTk.PhotoImage(Image.open(
                album_covers + "{} - {}.png".format(state.mars_object.album_artists[entry[INDEX]],
                                                    state.mars_object.album_titles[entry[INDEX]]).replace('/', ' ')
                .replace('?', ' ').replace(':', ' ')))
        except FileNotFoundError:
            cover[index] = ImageTk.PhotoImage(Image.open(album_covers + "no_image.png"))

        cover_label = tk.Label(display_window_left, image=cover[index])
        cover_label.grid(row=index + 2, column=0)

        label = tk.Label(display_window_left,
                         text="{}\n{}".format(mars_core.album_titles[entry[INDEX]],
                                              mars_core.album_artists[entry[INDEX]]),
                         width=50)
        label.grid(row=index + 2, column=1)

        # adding buttons to rank
        for rate in range(-2, 3):
            rate_to_display = rate + 3
            new_button = tk.Button(display_window_left, text=rate_to_display,
                                   padx=20, pady=20,
                                   command=partial(state.rate_album, entry[INDEX], rate))
            new_button.grid(row=index + 2, column=rate_to_display + 1)

    # creating right slidebar for albums with grades
    chosen = tk.LabelFrame(root)
    chosen.pack(side='right', fill='both')

    canvas_right = tk.Canvas(chosen)
    canvas_right.pack(side='left', fill='both', expand=1)

    scrollbar_right = ttk.Scrollbar(chosen, orient='vertical', command=canvas_right.yview)
    scrollbar_right.pack(side='right', fill='y')

    canvas_right.configure(yscrollcommand=scrollbar_right.set)
    canvas_right.bind('<Configure>', lambda e: canvas_right.configure(scrollregion=canvas_right.bbox('all')))

    display_window_right = tk.Frame(canvas_right)
    canvas_right.create_window((0, 0), window=display_window_right, anchor='nw')

    # filling slidebar with info
    for i, (index, grade) in enumerate(mars_core.already_chosen.items()):
        display_grade = grade + 3
        label = tk.Label(display_window_right, width=46, height=5,
                         text="{}\n{}\nRating: {}".format(mars_core.album_titles[index],
                                                          mars_core.album_artists[index],
                                                          display_grade))
        remove_button = tk.Button(display_window_right, text="remove", command=partial(state.del_album, index))
        label.grid(row=i, column=0)
        remove_button.grid(row=i, column=1)
        i += 1


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("MARS")
    root.iconbitmap('album_info/MARS_icon.ico')

    state = LoopState(mars_object=MarsCore(json_path=JSON_PATH), chunk_length=30)
    update(state)
    root.mainloop()
