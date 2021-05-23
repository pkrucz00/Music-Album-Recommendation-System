from MarsCore import MarsCore
import tkinter as tk
from tkinter import ttk

from functools import partial
from time import time
from math import ceil
import logging

INDEX = 0
RATING = 1
JSON_PATH = "album_info/album_info.json"

logging.basicConfig(level=logging.DEBUG)


class LoopState:
    def __init__(self, chunk_length, mars_object):
        self.chunk_length = chunk_length
        self.curr_chunk_index = 0
        self.mars_object = mars_object

    def increment_chunk_index(self):
        self.curr_chunk_index += 1
        update(self)

    def decrement_chunk_index(self):
        self.curr_chunk_index -= 1
        update(self)

    def can_go_left(self):
        return self.curr_chunk_index > 0

    def can_go_right(self):
        return (self.curr_chunk_index+1)*self.chunk_length < self.get_no_albums()

    def return_chunk(self):
        return self.mars_object.result_list[self.chunk_length * self.curr_chunk_index:
                                            self.chunk_length * (self.curr_chunk_index + 1)]

    def get_no_albums(self):
        return len(self.mars_object.result_list)

    def get_no_chunks(self):
        return ceil(self.get_no_albums()/self.chunk_length)


# rating album, cleaning root and creating new elements (upadated)
def rate_update(state, index, rate):
    print(state.mars_object)
    t1 = time()
    state.mars_object.choose(index, rate)
    t2 = time()
    print(state.mars_object)
    logging.debug('Time of giving grade (adding similarities, sorting, etc.): {}s'.format(t2 - t1))

    t1 = time()
    update(state)
    t2 = time()
    logging.debug('Time of updating the root: {}s\n'.format(t2 - t1))


def del_elem(state, index):
    state.mars_object.unchoose(index)
    update(state)


def boolean_to_button_constants(expression):
    return tk.NORMAL if expression else tk.DISABLED


# setting root



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

    left_button = tk.Button(display_window_left, text="left",
                            command=state.decrement_chunk_index,
                            state=boolean_to_button_constants(state.can_go_left()))
    chunk_num_label = tk.Label(display_window_left,
                               text=f"{state.curr_chunk_index + 1} out of {state.get_no_chunks()}")
    right_button = tk.Button(display_window_left, text="right",
                             command=state.increment_chunk_index,
                             state=boolean_to_button_constants(state.can_go_right()))
    left_button.grid(row=0, column=0)
    chunk_num_label.grid(row=0, column=1)
    right_button.grid(row=0, column=2)
    # filling slidebar with albums
    truncated_list = state.return_chunk()
    for index, entry in enumerate(truncated_list):
        label = tk.Label(display_window_left,
                         text="{}\n{}".format(mars_core.album_titles[entry[INDEX]],
                                              mars_core.album_artists[entry[INDEX]]))
        label.grid(row=index + 1, column=0)

        # adding buttons to rank
        for rate in range(-2, 3):
            display_rate = rate + 3
            print(entry[INDEX])
            new_button = tk.Button(display_window_left, text=display_rate,
                                   padx=20, pady=20,
                                   command=partial(rate_update, state, entry[INDEX], rate)
                                   )
            new_button.grid(row=index + 1, column=display_rate)

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
        remove_button = tk.Button(display_window_right, text="remove", command=partial(del_elem, state, index))
        label.grid(row=i, column=0)
        remove_button.grid(row=i, column=1)
        i += 1


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1080x720")
    # root.resizable(False, False)
    root.title("MARS")

    state = LoopState(chunk_length=30, mars_object=MarsCore(json_path=JSON_PATH))
    update(state)
    root.mainloop()
