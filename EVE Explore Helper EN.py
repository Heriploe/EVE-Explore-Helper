import tkinter as tk
import json
import math
from tkinter import ttk
from tkinter import messagebox

ly = 9.46073047258E+15


def check_visited(name, list):
    result = False
    for i in range(0, len(list)):
        if name == list[i]:
            result = True
    return result


def is_valid_name(name, list):
    result = False
    for i in range(0, len(list)):
        if name == list[i]:
            result = True
    return result


def distance(a, b):
    a = [x / ly for x in a]
    b = [x / ly for x in b]
    d = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
    return d


def get_planet_by_name(name, data):
    for i in range(0, len(data)):
        if name == data[i]["name"]:
            return data[i]["planetCount"]


def get_radius_by_name(name, data):
    for i in range(0, len(data)):
        if name == data[i]["name"]:
            return data[i]["outermostOrbitRadius"]


def get_luminosity_by_name(name, data):
    for i in range(0, len(data)):
        if name == data[i]["name"]:
            return data[i]["luminosity"] / 3.828e26


class AutocompleteEntry(tk.Entry):
    def __init__(self, options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace("w", self.on_change)
        self.listbox = None

    def on_change(self, *args):
        value = self.var.get()
        if value == "":
            self.hide_listbox()
        else:
            matches = [item for item in self.options if item.startswith(value)]
            if matches:
                self.show_listbox(matches)
            else:
                self.hide_listbox()

    def show_listbox(self, matches):
        if self.listbox:
            self.listbox.destroy()
        self.listbox = tk.Listbox(width=self["width"])
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for item in matches:
            self.listbox.insert(tk.END, item)
        self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())

    def hide_listbox(self):
        if self.listbox:
            self.listbox.destroy()
            self.listbox = None

    def on_select(self, event):
        if self.listbox:
            selection = self.listbox.get(self.listbox.curselection())
            self.var.set(selection)
            self.hide_listbox()


root = tk.Tk()
root.title("EVE Travel Helper 1.0")
root.geometry("530x370")

file = "name_list.json"
with open(file, "r", encoding="utf-8") as f:
    name_list = json.load(f)

entry = AutocompleteEntry(name_list, root, width=30)
entry.grid(row=0, column=0, padx=20, pady=20, sticky="e")

entry_distance = AutocompleteEntry(name_list, root, width=30)
entry_distance.grid(row=1, column=0, padx=20, pady=20, sticky="e")
entry_distance.insert(0, "50")

file = "starmap_processed.json"
with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)

file = "constellations.json"
with open(file, "r", encoding="utf-8") as f:
    constellations = json.load(f)


def check_constellations(name, data):
    in_cconstellations = False
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            if name == data[i][j]:
                in_cconstellations = True
                break

    return in_cconstellations


distance_list = []



show_stargate = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Show Stargate", variable=show_stargate)
checkbox.grid(row=2, column=2, padx=20, pady=20, sticky="w")
show_visited = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Show Visited", variable=show_visited)
checkbox.grid(row=3, column=2, padx=20, pady=20, sticky="w")


def get_entry_data():
    name = entry.get()
    entry.hide_listbox()
    with open("name_list.json", "r", encoding="utf-8") as f:
        name_list_all = json.load(f)
    if is_valid_name(name, name_list_all):
        distance_max = int(entry_distance.get())

        try:
            with open("visited.json", "r", encoding="utf-8") as f:
                visited_list = json.load(f)
        except FileNotFoundError:
            visited_list = []
        if check_visited(name, visited_list) == False:
            visited_list = visited_list + [name]
        with open("visited.json", "w", encoding="utf-8") as f:
            json.dump(visited_list, f, ensure_ascii=False, indent=4)
        cord = []
        name_list = []
        global distance_list
        distance_list = []
        for i in range(0, len(data)):
            if data[i]["name"] == name:
                cord = [data[i]["location"]["x"], data[i]["location"]["y"],
                        data[i]["location"]["z"]]
        for i in range(0, len(data)):
            cord_temp = [data[i]["location"]["x"], data[i]["location"]["y"],
                         data[i]["location"]["z"]]

            if distance(cord, cord_temp) < distance_max and distance(cord, cord_temp) != 0:
                visited_bool = check_visited(data[i]["name"], visited_list)
                stargate_bool = check_constellations(data[i]["name"], constellations)
                if show_stargate.get() and show_visited.get():
                    name_list = name_list + [data[i]["name"]]
                elif show_visited.get() and not show_stargate.get():
                    if not stargate_bool:
                        name_list = name_list + [data[i]["name"]]
                elif not show_visited.get() and show_stargate.get():
                    if not visited_bool:
                        name_list = name_list + [data[i]["name"]]
                else:
                    if not visited_bool and not stargate_bool:
                        name_list = name_list + [data[i]["name"]]

                distance_list = distance_list + ["{:.2f}".format(distance(cord, cord_temp), 2)]
        listbox.delete(0, tk.END)
        for item in name_list:
            listbox.insert(tk.END, item)
    else:
        messagebox.showwarning("Warning", "Solar System Not Exist!")


btn = tk.Button(root, text="Find Solar Systems", command=get_entry_data)
btn.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

options = []
listbox = tk.Listbox(root, height=20, selectmode=tk.SINGLE)
for item in options:
    listbox.insert(tk.END, item)
listbox.grid(row=0, column=1, padx=20, pady=20, rowspan=4, sticky="e")


def on_select(event):
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        key = listbox.get(index)
        try:
            with open("visited.json", "r", encoding="utf-8") as f:
                visited_list = json.load(f)
        except FileNotFoundError:
            visited_list = []
        detail_var.set("Distance: " + distance_list[index] + "\n" + "Planets: " + str(
            get_planet_by_name(key, data)) + "\n" + "Radius: " + "{:.2f}".format(
            get_radius_by_name(key, data)) + "\n" + "Lumin: " + "{:.4f}".format(get_luminosity_by_name(key, data))
                       + "\n" + "Ratio: " + "{:.2f}".format(100*get_luminosity_by_name(key, data)/get_radius_by_name(key, data)**2)
                       + "\n" + "StarGate: " + str(check_constellations(key, constellations))
                       + "\n" + "Visited: " + str(check_visited(key, visited_list)))


listbox.bind("<<ListboxSelect>>", on_select)

detail_var = tk.StringVar()
detail_label = ttk.Label(root, textvariable=detail_var, wraplength=200, justify="left")
detail_label.grid(row=0, column=2, padx=20, pady=20, sticky="w")


def confirm_explore():
    selected_indice = listbox.curselection()
    selected_item = listbox.get(selected_indice)
    try:
        with open("visited.json", "r", encoding="utf-8") as f:
            visited_list = json.load(f)
    except FileNotFoundError:
        visited_list = []
    selected_item_name = selected_item
    print(selected_item_name)
    if not check_visited(selected_item_name, visited_list):
        visited_list = visited_list + [selected_item_name]

    with open("visited.json", "w", encoding="utf-8") as f:
        json.dump(visited_list, f, ensure_ascii=False, indent=4)
    detail_var.set("")
    entry.delete(0, tk.END)
    entry.insert(0, selected_item_name)

    get_entry_data()


btn = tk.Button(root, text="Confirm Explore", command=confirm_explore)
btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

root.mainloop()
