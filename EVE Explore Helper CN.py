import json
import math
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

ly = 9.46073047258E+15
au = 1.496E+11


def check_visited(name, names):
    return name in names


def is_valid_name(name, names):
    return name in names


def distance(a, b):
    a = [x / ly for x in a]
    b = [x / ly for x in b]
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def get_planet_by_name(name, systems):
    for i in range(0, len(systems)):
        if name == systems[i]["name"]:
            return systems[i]["planetCount"]
    return 0


def get_radius_by_name(name, systems):
    for i in range(0, len(systems)):
        if name == systems[i]["name"]:
            return systems[i]["outermostOrbitRadius"] / au
    return 0


def get_luminosity_by_name(name, systems):
    for i in range(0, len(systems)):
        if name == systems[i]["name"]:
            return systems[i]["luminosity"] / 3.828e26
    return 0


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


def check_constellations(name, data):
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            if name == data[i][j]:
                return True
    return False


root = tk.Tk()
root.title("EVE探索助手1.1")
root.geometry("980x560")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

with open("name_list.json", "r", encoding="utf-8") as f:
    name_list = json.load(f)

with open("starmap_processed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("constellations.json", "r", encoding="utf-8") as f:
    constellations = json.load(f)

system_map = {item["name"]: item for item in data}
result_records = []

main_frame = ttk.Frame(root, padding=12)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.columnconfigure(0, weight=0)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=0)
main_frame.rowconfigure(1, weight=1)

control_frame = ttk.LabelFrame(main_frame, text="搜索与筛选", padding=12)
control_frame.grid(row=0, column=0, sticky="new", padx=(0, 12))

result_frame = ttk.LabelFrame(main_frame, text="候选星系", padding=12)
result_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
result_frame.columnconfigure(0, weight=1)
result_frame.rowconfigure(0, weight=1)

info_frame = ttk.LabelFrame(main_frame, text="星系详情", padding=12)
info_frame.grid(row=0, column=2, sticky="new", padx=(12, 0))

# 控件
current_label = ttk.Label(control_frame, text="当前星系")
current_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
entry = AutocompleteEntry(name_list, control_frame, width=28)
entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))

range_label = ttk.Label(control_frame, text="搜索半径（光年）")
range_label.grid(row=2, column=0, sticky="w", pady=(0, 4))
entry_distance = ttk.Entry(control_frame, width=28)
entry_distance.grid(row=3, column=0, sticky="ew", pady=(0, 8))
entry_distance.insert(0, "50")

target_label = ttk.Label(control_frame, text="目标星系（可选）")
target_label.grid(row=4, column=0, sticky="w", pady=(0, 4))
entry_target = AutocompleteEntry(name_list, control_frame, width=28)
entry_target.grid(row=5, column=0, sticky="ew", pady=(0, 8))

sort_label = ttk.Label(control_frame, text="排序方式")
sort_label.grid(row=6, column=0, sticky="w", pady=(0, 4))

sort_var = tk.StringVar(value="与当前星系距离")
sort_options = ["与当前星系距离", "与目标星系距离", "行星个数"]
sort_menu = ttk.Combobox(control_frame, textvariable=sort_var, values=sort_options, state="readonly", width=25)
sort_menu.grid(row=7, column=0, sticky="ew", pady=(0, 8))

show_stargate = tk.BooleanVar()
show_visited = tk.BooleanVar()
ttk.Checkbutton(control_frame, text="显示有星门星系", variable=show_stargate).grid(row=8, column=0, sticky="w")
ttk.Checkbutton(control_frame, text="显示已访问星系", variable=show_visited).grid(row=9, column=0, sticky="w", pady=(0, 8))

columns = ("name", "dist_current", "dist_target", "planets")
listbox = ttk.Treeview(result_frame, columns=columns, show="headings", height=18)
listbox.heading("name", text="星系")
listbox.heading("dist_current", text="距当前(ly)")
listbox.heading("dist_target", text="距目标(ly)")
listbox.heading("planets", text="行星数")
listbox.column("name", width=180, anchor="w")
listbox.column("dist_current", width=100, anchor="center")
listbox.column("dist_target", width=100, anchor="center")
listbox.column("planets", width=80, anchor="center")
listbox.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=listbox.yview)
listbox.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

detail_var = tk.StringVar(value="请选择一个星系查看详情。")
detail_label = ttk.Label(info_frame, textvariable=detail_var, wraplength=230, justify="left")
detail_label.grid(row=0, column=0, sticky="w")


def sort_records(records):
    selected_sort = sort_var.get()
    if selected_sort == "与当前星系距离":
        records.sort(key=lambda item: item["distance_current"])
    elif selected_sort == "与目标星系距离":
        records.sort(key=lambda item: item["distance_target"])
    else:
        records.sort(key=lambda item: item["planet_count"], reverse=True)


def render_result(records):
    for row in listbox.get_children():
        listbox.delete(row)

    for item in records:
        target_distance_text = "-" if item["distance_target"] == float("inf") else f"{item['distance_target']:.2f}"
        listbox.insert(
            "",
            tk.END,
            iid=item["name"],
            values=(item["name"], f"{item['distance_current']:.2f}", target_distance_text, item["planet_count"])
        )


def get_entry_data():
    current_name = entry.get().strip()
    target_name = entry_target.get().strip()
    entry.hide_listbox()
    entry_target.hide_listbox()

    if not is_valid_name(current_name, name_list):
        messagebox.showwarning("警告", "不存在当前星系!")
        return

    if target_name and not is_valid_name(target_name, name_list):
        messagebox.showwarning("警告", "目标星系不存在!")
        return

    try:
        distance_max = int(entry_distance.get())
    except ValueError:
        messagebox.showwarning("警告", "搜索半径必须是整数。")
        return

    try:
        with open("visited.json", "r", encoding="utf-8") as f:
            visited_list = json.load(f)
    except FileNotFoundError:
        visited_list = []

    if not check_visited(current_name, visited_list):
        visited_list = visited_list + [current_name]

    with open("visited.json", "w", encoding="utf-8") as f:
        json.dump(visited_list, f, ensure_ascii=False, indent=4)

    current_cord = [
        system_map[current_name]["location"]["x"],
        system_map[current_name]["location"]["y"],
        system_map[current_name]["location"]["z"],
    ]

    target_cord = None
    if target_name:
        target_cord = [
            system_map[target_name]["location"]["x"],
            system_map[target_name]["location"]["y"],
            system_map[target_name]["location"]["z"],
        ]

    global result_records
    result_records = []

    for i in range(0, len(data)):
        name = data[i]["name"]
        cord_temp = [data[i]["location"]["x"], data[i]["location"]["y"], data[i]["location"]["z"]]
        dist_current = distance(current_cord, cord_temp)

        if dist_current < distance_max and dist_current != 0:
            visited_bool = check_visited(name, visited_list)
            stargate_bool = check_constellations(name, constellations)

            if show_stargate.get() and show_visited.get():
                show_it = True
            elif show_visited.get() and not show_stargate.get():
                show_it = not stargate_bool
            elif not show_visited.get() and show_stargate.get():
                show_it = not visited_bool
            else:
                show_it = not visited_bool and not stargate_bool

            if show_it:
                dist_target = float("inf")
                if target_cord:
                    dist_target = distance(target_cord, cord_temp)

                result_records.append({
                    "name": name,
                    "distance_current": dist_current,
                    "distance_target": dist_target,
                    "planet_count": get_planet_by_name(name, data),
                })

    if sort_var.get() == "与目标星系距离" and not target_name:
        messagebox.showinfo("提示", "已选择“与目标星系距离”排序，但未填写目标星系，结果将按无目标距离显示。")

    sort_records(result_records)
    render_result(result_records)


def on_select(event):
    selection = listbox.selection()
    if not selection:
        return

    key = selection[0]
    try:
        with open("visited.json", "r", encoding="utf-8") as f:
            visited_list = json.load(f)
    except FileNotFoundError:
        visited_list = []

    record = next((item for item in result_records if item["name"] == key), None)
    if not record:
        return

    detail_var.set(
        "距离当前: " + f"{record['distance_current']:.2f}" + "\n"
        + "距离目标: " + ("-" if record["distance_target"] == float("inf") else f"{record['distance_target']:.2f}") + "\n"
        + "行星数: " + str(get_planet_by_name(key, data)) + "\n"
        + "最大轨道: " + "{:.2f}".format(get_radius_by_name(key, data)) + "\n"
        + "光度: " + "{:.4f}".format(get_luminosity_by_name(key, data)) + "\n"
        + "温度指数: " + "{:.2f}".format(
            100 * get_luminosity_by_name(key, data) / get_radius_by_name(key, data) ** 2
        ) + "\n"
        + "是否有星门: " + str(check_constellations(key, constellations)) + "\n"
        + "是否访问过: " + str(check_visited(key, visited_list))
    )


def confirm_explore():
    selected_item = listbox.selection()
    if not selected_item:
        messagebox.showwarning("警告", "请先选择一个候选星系。")
        return

    selected_item_name = selected_item[0]
    try:
        with open("visited.json", "r", encoding="utf-8") as f:
            visited_list = json.load(f)
    except FileNotFoundError:
        visited_list = []

    if not check_visited(selected_item_name, visited_list):
        visited_list = visited_list + [selected_item_name]

    with open("visited.json", "w", encoding="utf-8") as f:
        json.dump(visited_list, f, ensure_ascii=False, indent=4)

    detail_var.set("")
    entry.delete(0, tk.END)
    entry.insert(0, selected_item_name)
    get_entry_data()


action_frame = ttk.Frame(control_frame)
action_frame.grid(row=10, column=0, sticky="ew", pady=(8, 0))

btn_search = ttk.Button(action_frame, text="搜索星系", command=get_entry_data)
btn_search.grid(row=0, column=0, sticky="ew")

btn_confirm = ttk.Button(action_frame, text="确认探索", command=confirm_explore)
btn_confirm.grid(row=1, column=0, sticky="ew", pady=(6, 0))

control_frame.columnconfigure(0, weight=1)
action_frame.columnconfigure(0, weight=1)

listbox.bind("<<TreeviewSelect>>", on_select)
sort_menu.bind("<<ComboboxSelected>>", lambda event: (sort_records(result_records), render_result(result_records)))

root.mainloop()
