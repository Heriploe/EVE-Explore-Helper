import json
import math
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk

LY = 9.46073047258E+15
AU = 1.496E+11
SETTINGS_FILE = Path("settings.json")

I18N = {
    "zh": {
        "app_title": "EVE探索助手",
        "control_title": "搜索与筛选",
        "result_title": "候选星系",
        "info_title": "星系详情",
        "language": "语言",
        "lang_zh": "中文",
        "lang_en": "English",
        "current_system": "当前星系",
        "distance_limit": "搜索半径（光年）",
        "target_system": "目标星系（可选）",
        "sort_mode": "排序方式",
        "sort_current": "与当前星系距离",
        "sort_target": "与目标星系距离",
        "sort_planets": "行星个数",
        "show_stargate": "显示有星门星系",
        "show_visited": "显示已访问星系",
        "btn_search": "搜索星系",
        "btn_confirm": "确认探索",
        "col_name": "星系",
        "col_dist_current": "距当前(ly)",
        "col_dist_target": "距目标(ly)",
        "col_planets": "行星数",
        "detail_placeholder": "请选择一个星系查看详情。",
        "distance_current": "距离当前",
        "distance_target": "距离目标",
        "planet_count": "行星数",
        "radius": "最大轨道",
        "luminosity": "光度",
        "temp_ratio": "温度指数",
        "has_stargate": "是否有星门",
        "visited": "是否访问过",
        "warn_missing_current": "不存在当前星系!",
        "warn_missing_target": "目标星系不存在!",
        "warn_distance_int": "搜索半径必须是数字。",
        "warn_no_selection": "请先选择一个候选星系。",
        "tip": "提示",
        "tip_target_missing": "已选择按目标距离排序，但未填写目标星系。",
        "dash": "-",
    },
    "en": {
        "app_title": "EVE Explore Helper",
        "control_title": "Search & Filters",
        "result_title": "Candidate Systems",
        "info_title": "System Details",
        "language": "Language",
        "lang_zh": "中文",
        "lang_en": "English",
        "current_system": "Current System",
        "distance_limit": "Distance Limit (ly)",
        "target_system": "Target System (optional)",
        "sort_mode": "Sort By",
        "sort_current": "Distance to Current",
        "sort_target": "Distance to Target",
        "sort_planets": "Planet Count",
        "show_stargate": "Show Stargate Systems",
        "show_visited": "Show Visited Systems",
        "btn_search": "Search Systems",
        "btn_confirm": "Confirm Explore",
        "col_name": "System",
        "col_dist_current": "To Current(ly)",
        "col_dist_target": "To Target(ly)",
        "col_planets": "Planets",
        "detail_placeholder": "Select a system to see details.",
        "distance_current": "Distance to current",
        "distance_target": "Distance to target",
        "planet_count": "Planets",
        "radius": "Max orbit",
        "luminosity": "Luminosity",
        "temp_ratio": "Temperature index",
        "has_stargate": "Has stargate",
        "visited": "Visited",
        "warn_missing_current": "Current system does not exist!",
        "warn_missing_target": "Target system does not exist!",
        "warn_distance_int": "Distance limit must be numeric.",
        "warn_no_selection": "Please select a candidate system first.",
        "tip": "Tip",
        "tip_target_missing": "Sort-by-target selected, but target system is empty.",
        "dash": "-",
    },
}


def dist(a, b):
    aa = [x / LY for x in a]
    bb = [x / LY for x in b]
    return math.sqrt((aa[0] - bb[0]) ** 2 + (aa[1] - bb[1]) ** 2 + (aa[2] - bb[2]) ** 2)


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
            return
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

    def on_select(self, _event):
        if self.listbox:
            selection = self.listbox.get(self.listbox.curselection())
            self.var.set(selection)
            self.hide_listbox()


class App:
    def __init__(self, default_language="zh"):
        self.name_list = self.load_json("name_list.json")
        self.data = self.load_json("starmap_processed.json")
        self.constellations = self.load_json("constellations.json")
        self.system_map = {item["name"]: item for item in self.data}
        self.result_records = []

        self.settings = self.load_settings(default_language)
        self.root = tk.Tk()
        self.root.geometry("980x560")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.lang_var = tk.StringVar(value=self.settings.get("language", default_language))
        self.sort_key_var = tk.StringVar(value=self.settings.get("sort_key", "sort_current"))
        self.show_stargate_var = tk.BooleanVar(value=self.settings.get("show_stargate", False))
        self.show_visited_var = tk.BooleanVar(value=self.settings.get("show_visited", False))

        self.detail_var = tk.StringVar()
        self.build_ui()
        self.apply_texts()

        self.entry_current.insert(0, self.settings.get("last_current", ""))
        self.entry_distance.insert(0, str(self.settings.get("distance_max", 50)))
        self.entry_target.insert(0, self.settings.get("last_target", ""))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    @staticmethod
    def load_json(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def tr(self, key):
        return I18N[self.lang_var.get()][key]

    def load_settings(self, default_language):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("language") in I18N:
                        return data
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "language": default_language,
            "sort_key": "sort_current",
            "distance_max": 50,
            "show_stargate": False,
            "show_visited": False,
            "last_current": "",
            "last_target": "",
        }

    def save_settings(self):
        self.settings.update({
            "language": self.lang_var.get(),
            "sort_key": self.sort_key_var.get(),
            "distance_max": self.entry_distance.get().strip() or "50",
            "show_stargate": self.show_stargate_var.get(),
            "show_visited": self.show_visited_var.get(),
            "last_current": self.entry_current.get().strip(),
            "last_target": self.entry_target.get().strip(),
        })
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def build_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=12)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(1, weight=1)

        self.control_frame = ttk.LabelFrame(self.main_frame, padding=12)
        self.control_frame.grid(row=0, column=0, sticky="new", padx=(0, 12))

        self.result_frame = ttk.LabelFrame(self.main_frame, padding=12)
        self.result_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)

        self.info_frame = ttk.LabelFrame(self.main_frame, padding=12)
        self.info_frame.grid(row=0, column=2, sticky="new", padx=(12, 0))

        self.label_language = ttk.Label(self.control_frame)
        self.label_language.grid(row=0, column=0, sticky="w")
        self.lang_display_var = tk.StringVar()
        self.lang_menu = ttk.Combobox(
            self.control_frame,
            textvariable=self.lang_display_var,
            values=["中文", "English"],
            state="readonly",
            width=26,
        )
        self.lang_menu.grid(row=1, column=0, sticky="ew", pady=(2, 8))

        self.label_current = ttk.Label(self.control_frame)
        self.label_current.grid(row=2, column=0, sticky="w")
        self.entry_current = AutocompleteEntry(self.name_list, self.control_frame, width=28)
        self.entry_current.grid(row=3, column=0, sticky="ew", pady=(2, 8))

        self.label_distance = ttk.Label(self.control_frame)
        self.label_distance.grid(row=4, column=0, sticky="w")
        self.entry_distance = ttk.Entry(self.control_frame, width=28)
        self.entry_distance.grid(row=5, column=0, sticky="ew", pady=(2, 8))

        self.label_target = ttk.Label(self.control_frame)
        self.label_target.grid(row=6, column=0, sticky="w")
        self.entry_target = AutocompleteEntry(self.name_list, self.control_frame, width=28)
        self.entry_target.grid(row=7, column=0, sticky="ew", pady=(2, 8))

        self.label_sort = ttk.Label(self.control_frame)
        self.label_sort.grid(row=8, column=0, sticky="w")
        self.sort_menu = ttk.Combobox(self.control_frame, state="readonly", width=26)
        self.sort_menu.grid(row=9, column=0, sticky="ew", pady=(2, 8))

        self.check_stargate = ttk.Checkbutton(self.control_frame, variable=self.show_stargate_var)
        self.check_stargate.grid(row=10, column=0, sticky="w")
        self.check_visited = ttk.Checkbutton(self.control_frame, variable=self.show_visited_var)
        self.check_visited.grid(row=11, column=0, sticky="w", pady=(0, 8))

        self.btn_search = ttk.Button(self.control_frame, command=self.search)
        self.btn_search.grid(row=12, column=0, sticky="ew")
        self.btn_confirm = ttk.Button(self.control_frame, command=self.confirm_explore)
        self.btn_confirm.grid(row=13, column=0, sticky="ew", pady=(6, 0))

        self.tree = ttk.Treeview(self.result_frame, columns=("name", "dc", "dt", "pc"), show="headings", height=18)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scroll.set)
        self.scroll.grid(row=0, column=1, sticky="ns")

        self.detail_label = ttk.Label(self.info_frame, textvariable=self.detail_var, wraplength=220, justify="left")
        self.detail_label.grid(row=0, column=0, sticky="w")

        self.control_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.lang_menu.bind("<<ComboboxSelected>>", self.on_language_changed)
        self.sort_menu.bind("<<ComboboxSelected>>", self.on_sort_changed)

    def apply_texts(self):
        self.root.title(self.tr("app_title"))
        self.control_frame.configure(text=self.tr("control_title"))
        self.result_frame.configure(text=self.tr("result_title"))
        self.info_frame.configure(text=self.tr("info_title"))

        self.label_language.configure(text=self.tr("language"))
        self.label_current.configure(text=self.tr("current_system"))
        self.label_distance.configure(text=self.tr("distance_limit"))
        self.label_target.configure(text=self.tr("target_system"))
        self.label_sort.configure(text=self.tr("sort_mode"))

        self.sort_key_to_display = {
            "sort_current": self.tr("sort_current"),
            "sort_target": self.tr("sort_target"),
            "sort_planets": self.tr("sort_planets"),
        }
        self.display_to_sort_key = {v: k for k, v in self.sort_key_to_display.items()}
        self.sort_menu["values"] = list(self.sort_key_to_display.values())
        self.sort_menu.set(self.sort_key_to_display.get(self.sort_key_var.get(), self.tr("sort_current")))

        self.check_stargate.configure(text=self.tr("show_stargate"))
        self.check_visited.configure(text=self.tr("show_visited"))
        self.btn_search.configure(text=self.tr("btn_search"))
        self.btn_confirm.configure(text=self.tr("btn_confirm"))

        self.tree.heading("name", text=self.tr("col_name"))
        self.tree.heading("dc", text=self.tr("col_dist_current"))
        self.tree.heading("dt", text=self.tr("col_dist_target"))
        self.tree.heading("pc", text=self.tr("col_planets"))
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("dc", width=100, anchor="center")
        self.tree.column("dt", width=100, anchor="center")
        self.tree.column("pc", width=80, anchor="center")

        self.detail_var.set(self.tr("detail_placeholder"))
        self.lang_display_var.set(self.tr("lang_zh") if self.lang_var.get() == "zh" else self.tr("lang_en"))
        self.render_results()

    def on_language_changed(self, _event):
        selected = self.lang_display_var.get()
        self.lang_var.set("zh" if selected in ("中文", "Chinese") else "en")
        self.apply_texts()
        self.save_settings()

    def on_sort_changed(self, _event):
        self.sort_key_var.set(self.display_to_sort_key[self.sort_menu.get()])
        self.sort_records()
        self.render_results()
        self.save_settings()

    def has_stargate(self, name):
        for const in self.constellations:
            if name in const:
                return True
        return False

    def get_value(self, name, key, default=0):
        item = self.system_map.get(name)
        if not item:
            return default
        return item.get(key, default)

    def search(self):
        current_name = self.entry_current.get().strip()
        target_name = self.entry_target.get().strip()
        self.entry_current.hide_listbox()
        self.entry_target.hide_listbox()

        if current_name not in self.system_map:
            messagebox.showwarning("Warning", self.tr("warn_missing_current"))
            return
        if target_name and target_name not in self.system_map:
            messagebox.showwarning("Warning", self.tr("warn_missing_target"))
            return

        try:
            distance_max = float(self.entry_distance.get().strip())
        except ValueError:
            messagebox.showwarning("Warning", self.tr("warn_distance_int"))
            return

        visited = self.load_json("visited.json")
        if current_name not in visited:
            visited.append(current_name)
            with open("visited.json", "w", encoding="utf-8") as f:
                json.dump(visited, f, ensure_ascii=False, indent=2)

        current_loc = self.system_map[current_name]["location"]
        target_loc = self.system_map[target_name]["location"] if target_name else None

        self.result_records = []
        for item in self.data:
            name = item["name"]
            c = item["location"]
            d_current = dist([current_loc["x"], current_loc["y"], current_loc["z"]], [c["x"], c["y"], c["z"]])
            if d_current == 0 or d_current >= distance_max:
                continue

            visited_bool = name in visited
            stargate_bool = self.has_stargate(name)
            if not self.show_visited_var.get() and visited_bool:
                continue
            if not self.show_stargate_var.get() and stargate_bool:
                continue

            d_target = float("inf")
            if target_loc:
                d_target = dist([target_loc["x"], target_loc["y"], target_loc["z"]], [c["x"], c["y"], c["z"]])

            self.result_records.append({
                "name": name,
                "d_current": d_current,
                "d_target": d_target,
                "planets": item.get("planetCount", 0),
            })

        if self.sort_key_var.get() == "sort_target" and not target_name:
            messagebox.showinfo(self.tr("tip"), self.tr("tip_target_missing"))

        self.sort_records()
        self.render_results()
        self.save_settings()

    def sort_records(self):
        if self.sort_key_var.get() == "sort_current":
            self.result_records.sort(key=lambda x: x["d_current"])
        elif self.sort_key_var.get() == "sort_target":
            self.result_records.sort(key=lambda x: x["d_target"])
        else:
            self.result_records.sort(key=lambda x: x["planets"], reverse=True)

    def render_results(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for rec in self.result_records:
            d_target = self.tr("dash") if rec["d_target"] == float("inf") else f"{rec['d_target']:.2f}"
            self.tree.insert("", tk.END, iid=rec["name"], values=(rec["name"], f"{rec['d_current']:.2f}", d_target, rec["planets"]))

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        name = selected[0]
        rec = next((x for x in self.result_records if x["name"] == name), None)
        if not rec:
            return

        visited = self.load_json("visited.json")
        radius = self.get_value(name, "outermostOrbitRadius", 0) / AU
        luminosity = self.get_value(name, "luminosity", 0) / 3.828e26
        ratio = 0 if radius == 0 else 100 * luminosity / (radius ** 2)
        d_target = self.tr("dash") if rec["d_target"] == float("inf") else f"{rec['d_target']:.2f}"

        self.detail_var.set(
            f"{self.tr('distance_current')}: {rec['d_current']:.2f}\n"
            f"{self.tr('distance_target')}: {d_target}\n"
            f"{self.tr('planet_count')}: {rec['planets']}\n"
            f"{self.tr('radius')}: {radius:.2f}\n"
            f"{self.tr('luminosity')}: {luminosity:.4f}\n"
            f"{self.tr('temp_ratio')}: {ratio:.2f}\n"
            f"{self.tr('has_stargate')}: {self.has_stargate(name)}\n"
            f"{self.tr('visited')}: {name in visited}"
        )

    def confirm_explore(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", self.tr("warn_no_selection"))
            return

        selected_name = selected[0]
        visited = self.load_json("visited.json")
        if selected_name not in visited:
            visited.append(selected_name)
            with open("visited.json", "w", encoding="utf-8") as f:
                json.dump(visited, f, ensure_ascii=False, indent=2)

        self.entry_current.delete(0, tk.END)
        self.entry_current.insert(0, selected_name)
        self.detail_var.set("")
        self.search()

    def on_close(self):
        self.save_settings()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def run_app(default_language="zh"):
    app = App(default_language=default_language)
    app.run()
