from MarsCore import MarsCore
import tkinter as tk
from tkinter import ttk
from functools import partial

JSON_PATH = "album_info/album_info.json"

wangjangle = MarsCore(json_path=JSON_PATH)

#rating album, cleaning root and creating new elements (upadated)
def rate_update(index, rate):
    for ele in root.winfo_children():
        ele.destroy()

    print(index, rate)
    wangjangle.choose(index, rate)
    update(wangjangle)


#setting root
root = tk.Tk()
root.geometry("1080x720")
# root.resizable(False, False)
root.title("MARS")


def update(wangjangle):
    #creating left slidebar for albums sorted (to rank)
    not_chosen = tk.LabelFrame(root, border=2)
    not_chosen.pack(side='left', fill='both', expand=1)

    canvas_left = tk.Canvas(not_chosen)
    canvas_left.pack(side='left', fill='both', expand=1)

    scrollbar_left = ttk.Scrollbar(not_chosen, orient='vertical', command=canvas_left.yview)
    scrollbar_left.pack(side='right', fill='y')

    canvas_left.configure(yscrollcommand=scrollbar_left.set)
    canvas_left.bind('<Configure>', lambda e: canvas_left.configure(scrollregion=canvas_left.bbox('all')))

    display_window_left = tk.Frame(canvas_left)
    canvas_left.create_window((0,0), window=display_window_left, anchor='nw')

    #filling slidebar with albums
    for index, position in enumerate(wangjangle.result_list):
        label = tk.Label(display_window_left, text="{}\n{}".format(wangjangle.album_titles[position[0]], wangjangle.album_artists[position[0]]))
        label.grid(row=index, column=0)

        #adding buttons to rank
        for rate in range(-2, 3):
            new_button = tk.Button(display_window_left, text=rate, padx=20, pady=20, command=partial(rate_update, position[0], rate))
            new_button.grid(row=index, column=rate+3)



    #creating right slidebar for albums with grades
    chosen = tk.LabelFrame(root)
    chosen.pack(side='right', fill='both')

    canvas_right = tk.Canvas(chosen)
    canvas_right.pack(side='left', fill='both', expand=1)

    scrollbar_right = ttk.Scrollbar(chosen, orient='vertical', command=canvas_right.yview)
    scrollbar_right.pack(side='right', fill='y')

    canvas_right.configure(yscrollcommand=scrollbar_right.set)
    canvas_right.bind('<Configure>', lambda e: canvas_right.configure(scrollregion=canvas_right.bbox('all')))

    display_window_right = tk.Frame(canvas_right)
    canvas_right.create_window((0,0), window=display_window_right, anchor='nw')

    #filling slidebar with info
    for position in wangjangle.already_chosen.items():
        frame = tk.Frame(display_window_right, bd=10)
        frame.pack()
        label = tk.Label(frame, text="{}\n{}\nRating: {}".format(wangjangle.album_titles[position[0]], wangjangle.album_artists[position[0]], position[1]))
        label.pack()


update(wangjangle)

root.mainloop()
