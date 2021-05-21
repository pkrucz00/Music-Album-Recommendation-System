from MarsCore import MarsCore
import tkinter as tk
from tkinter import ttk
from functools import partial
from time import time
from math import ceil

JSON_PATH = "album_info/album_info.json"



class DisplayInfo:
    def __init__(self, chunk_length, mars_object):
        self.chunk_length = chunk_length
        self.curr_chunk_index = 0
        self.mars_object = mars_object

    def increment_chunk_index(self):
        print(self.curr_chunk_index)
        update(self.mars_object, self)
        self.curr_chunk_index += 1

    def decrement_chunk_index(self):
        print(self.curr_chunk_index)
        self.curr_chunk_index -= 1
        update(self.mars_object, self)

    def can_go_left(self):
        return self.curr_chunk_index > 0

    def can_go_right(self):
        return self.curr_chunk_index*(self.chunk_length+1) < self.get_no_albums()

    def return_chunk(self):
        return self.mars_object.result_list[self.chunk_length * self.curr_chunk_index:
                                            self.chunk_length * (self.curr_chunk_index + 1)]

    def get_no_albums(self):
        return len(self.mars_object.result_list)

    def get_no_chunks(self):
        return ceil(self.get_no_albums()/self.chunk_length)


core = MarsCore(json_path=JSON_PATH)
display_info = DisplayInfo(50, core)

# rating album, cleaning root and creating new elements (upadated)
def rate_update(index, rate):
    t1 = time()
    core.choose(index, rate)
    t2 = time()
    print('time of giving grade (adding similarities, sorting, etc.): {}s'.format(t2 - t1))

    t1 = time()
    for ele in root.winfo_children():
        ele.destroy()
    t2 = time()
    print('time of deleting elements from root: {}s'.format(t2 - t1))

    t1 = time()
    update(core, display_info)
    t2 = time()
    print('time of adding new elements to the root: {}s\n'.format(t2 - t1))


def del_elem(index):
    core.unchoose(index)
    for ele in root.winfo_children():
        ele.destroy()
    update(core, display_info)


def boolean_to_button_constants(expression):
    return tk.NORMAL if expression else tk.DISABLED


# setting root
root = tk.Tk()
root.geometry("1080x720")
# root.resizable(False, False)
root.title("MARS")


def update(core, display_info):
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
                            command=display_info.decrement_chunk_index,
                            state=boolean_to_button_constants(display_info.can_go_left()))
    chunk_num_label = tk.Label(display_window_left,
                               text=f"{display_info.curr_chunk_index+1} out of {display_info.get_no_chunks()}")
    right_button = tk.Button(display_window_left, text="right",
                             command=display_info.increment_chunk_index,
                             state=boolean_to_button_constants(display_info.can_go_right()))
    left_button.grid(row=0, column=0)
    chunk_num_label.grid(row=0, column=1)
    right_button.grid(row=0, column=2)
    # filling slidebar with albums
    truncated_list = display_info.return_chunk()
    for index, position in enumerate(truncated_list):
        label = tk.Label(display_window_left,
                         text="{}\n{}".format(core.album_titles[position[0]],
                                              core.album_artists[position[0]]))
        label.grid(row=index + 1, column=0)

        # adding buttons to rank
        for rate in range(-2, 3):
            display_rate = rate + 3
            new_button = tk.Button(display_window_left, text=display_rate,
                                   padx=20, pady=20,
                                   command=partial(rate_update, position[0], rate))
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
    for position in core.already_chosen.items():
        frame = tk.Frame(display_window_right, bd=10)
        frame.pack()
        label = tk.Label(frame,
                         text="{}\n{}\nRating: {}".format(core.album_titles[position[0]],
                                                          core.album_artists[position[0]],
                                                          position[1] + 3))
        remove_button = tk.Button(frame, text="remove", command=lambda: del_elem(position[0]))
        label.grid(column=0)
        remove_button.grid(column=1)


if __name__ == "__main__":
    update(core, display_info)
    root.mainloop()
