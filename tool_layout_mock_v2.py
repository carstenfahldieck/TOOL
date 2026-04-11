import os
import tkinter as tk
from tkinter import ttk


# ===== PART: CONFIG START =====
CFG_APP_TITLE = "TOOL Layout Mock V2"
CFG_WINDOW_WIDTH = 1600
CFG_WINDOW_HEIGHT = 900

CFG_LEFT_WIDTH = 270
CFG_RIGHT_WIDTH = 320
CFG_OUTER_PAD = 6
CFG_INNER_PAD = 4

CFG_COLOR_BG = "#f3f3f3"
CFG_COLOR_PANEL = "#efefef"
CFG_COLOR_BORDER = "#b8b8b8"
CFG_COLOR_ACTIVE = "#dfe9ff"
CFG_COLOR_NEW = "#1f5fd1"
CFG_COLOR_ERROR = "#c62828"
CFG_COLOR_HINT = "#666666"
CFG_COLOR_VALUE_BG = "#ffffff"
CFG_COLOR_EDITOR_BG = "#ffffff"

CFG_SHOW_PARTS_2 = True
# ===== PART: CONFIG END =====


# ===== PART: DATA START =====
DEMO_PARTS = [
    "TEST_LOAD",
    "DD",
    "MEIN_TEST",
    "MAIN_TEST",
    "TEST_UPDATE_MARKER",
    "MEIN_TEST12",
    "MEIN_TEST11",
]

DEMO_NEXT_LEVEL = [
    "SUB: Beispiel_A",
    "JUMPER: Startpunkt",
    "BEMERKUNG: Hinweis hier",
]

DEMO_CFGS = [
    "cfg_ui_window_width",
    "cfg_ui_window_height",
    "cfg_ui_padding_outer",
    "cfg_ui_spacing_small",
    "cfg_ui_spacing_medium",
    "cfg_ui_list_height",
    "cfg_ui_color_free",
    "cfg_ui_color_preview",
]

DEMO_FILES_BY_PATH = [
    {
        "title": "Pfad 1",
        "path": r"C:\Users\carst\Desktop\Tool",
        "items": [
            {"name": "fake_target.py", "size": "1 KB", "date": "11.04.2026", "status": "aktiv"},
            {"name": "parts_logic.py", "size": "14 KB", "date": "11.04.2026", "status": "normal"},
            {"name": "structure_dialogs.py", "size": "16 KB", "date": "11.04.2026", "status": "normal"},
        ],
    },
    {
        "title": "Pfad 2",
        "path": r"C:\Users\carst\Downloads",
        "items": [
            {"name": "cfg_logic.py", "size": "7 KB", "date": "11.04.2026", "status": "normal"},
            {"name": "app_core.py", "size": "24 KB", "date": "11.04.2026", "status": "normal"},
            {"name": "broken_test.py", "size": "2 KB", "date": "10.04.2026", "status": "error"},
            {"name": "neue_datei.py", "size": "0 KB", "date": "11.04.2026", "status": "new"},
        ],
    },
]
# ===== PART: DATA END =====


# ===== PART: HELPERS START =====
def read_fake_target_text():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "fake_target.py")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return (
            "# Beispielinhalt\n"
            "# fake_target.py konnte nicht geladen werden.\n"
            "# Diese Mock-Version zeigt trotzdem das Layout.\n"
        )


def apply_tree_status_colors(tree):
    tree.tag_configure("active", background=CFG_COLOR_ACTIVE)
    tree.tag_configure("new", foreground=CFG_COLOR_NEW)
    tree.tag_configure("error", foreground=CFG_COLOR_ERROR)
# ===== PART: HELPERS END =====


# ===== PART: UI_BUILD START =====
class MockApp:
    def __init__(self, root):
        self.root = root
        self.root.title(CFG_APP_TITLE)
        self.root.geometry(f"{CFG_WINDOW_WIDTH}x{CFG_WINDOW_HEIGHT}")
        self.root.configure(bg=CFG_COLOR_BG)

        self.var_show_parts_2 = tk.BooleanVar(value=CFG_SHOW_PARTS_2)

        self.build_menu()
        self.build_toolbar()
        self.build_main_layout()
        self.fill_demo_content()

    def build_menu(self):
        menubar = tk.Menu(self.root)
        for title in ("Datei", "Bearbeiten", "Ansicht", "Extras", "Hilfe"):
            menubar.add_cascade(label=title, menu=tk.Menu(menubar, tearoff=0))
        self.root.config(menu=menubar)

    def build_toolbar(self):
        bar = tk.Frame(self.root, bg=CFG_COLOR_BG)
        bar.pack(fill="x", padx=CFG_OUTER_PAD, pady=(CFG_OUTER_PAD, 2))

        for text in ("Laden", "Speichern", "Alle speichern"):
            tk.Button(bar, text=text, width=10).pack(side="left", padx=(0, 4))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=6)

        for text in ("Feste Buttons", "PARTS", "Variablen", "Dateien"):
            tk.Button(bar, text=text, width=10).pack(side="left", padx=(0, 4))

        tk.Frame(bar, bg=CFG_COLOR_BG).pack(side="left", expand=True, fill="x")

        tk.Label(bar, text="Variable Buttons", bg=CFG_COLOR_BG).pack(side="left", padx=(0, 8))
        for text in ("Suche", "Import", "Export"):
            tk.Button(bar, text=text, width=8).pack(side="left", padx=(0, 4))

    def build_main_layout(self):
        body = tk.Frame(self.root, bg=CFG_COLOR_BG)
        body.pack(fill="both", expand=True, padx=CFG_OUTER_PAD, pady=(2, CFG_OUTER_PAD))

        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.left_col = tk.Frame(body, width=CFG_LEFT_WIDTH, bg=CFG_COLOR_BG)
        self.left_col.grid(row=0, column=0, sticky="nsw", padx=(0, CFG_INNER_PAD))
        self.left_col.grid_propagate(False)

        self.center_col = tk.Frame(body, bg=CFG_COLOR_BG)
        self.center_col.grid(row=0, column=1, sticky="nsew", padx=(0, CFG_INNER_PAD))
        self.center_col.grid_rowconfigure(0, weight=1)
        self.center_col.grid_columnconfigure(0, weight=1)

        self.right_col = tk.Frame(body, width=CFG_RIGHT_WIDTH, bg=CFG_COLOR_BG)
        self.right_col.grid(row=0, column=2, sticky="nse", padx=(0, 0))
        self.right_col.grid_propagate(False)

        self.build_left_column()
        self.build_center_column()
        self.build_right_column()

    def make_panel(self, parent, title):
        panel = tk.Frame(parent, bg=CFG_COLOR_PANEL, bd=1, relief="solid", highlightbackground=CFG_COLOR_BORDER)
        header = tk.Label(panel, text=title, anchor="w", bg=CFG_COLOR_PANEL, font=("Segoe UI", 8, "bold"))
        header.pack(fill="x", padx=4, pady=(3, 2))
        inner = tk.Frame(panel, bg=CFG_COLOR_PANEL)
        inner.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        return panel, inner

    def build_left_column(self):
        self.left_col.grid_rowconfigure(1, weight=0)
        self.left_col.grid_rowconfigure(2, weight=1)

        top_controls = tk.Frame(self.left_col, bg=CFG_COLOR_BG)
        top_controls.pack(fill="x", pady=(0, 4))

        tk.Checkbutton(
            top_controls,
            text="SUBS zusätzlich",
            variable=tk.BooleanVar(value=True),
            bg=CFG_COLOR_BG
        ).pack(anchor="w")
        tk.Checkbutton(
            top_controls,
            text="JUMPER zusätzlich",
            variable=tk.BooleanVar(value=True),
            bg=CFG_COLOR_BG
        ).pack(anchor="w")

        panel1, inner1 = self.make_panel(self.left_col, "PARTS Teil 1")
        panel1.pack(fill="x", pady=(0, 4))
        self.list_parts_1 = tk.Listbox(inner1, height=9, exportselection=False)
        self.list_parts_1.pack(fill="both", expand=True)

        panel2, inner2 = self.make_panel(self.left_col, "PARTS Teil 2 (optional / nächste Ebene)")
        panel2.pack(fill="x", pady=(0, 4))
        self.list_parts_2 = tk.Listbox(inner2, height=7, exportselection=False)
        self.list_parts_2.pack(fill="both", expand=True)

        panel3, inner3 = self.make_panel(self.left_col, "CFG_ Variablen")
        panel3.pack(fill="both", expand=True, pady=(0, 4))
        self.list_cfg = tk.Listbox(inner3, height=8, exportselection=False)
        self.list_cfg.pack(fill="both", expand=True)

        panel4, inner4 = self.make_panel(self.left_col, "CFG_ Bearbeiten")
        panel4.pack(fill="x", pady=(0, 4))
        tk.Label(inner4, text="Wert:", anchor="w", bg=CFG_COLOR_PANEL).pack(fill="x")
        self.entry_cfg_value = tk.Entry(inner4, bg=CFG_COLOR_VALUE_BG)
        self.entry_cfg_value.pack(fill="x", pady=(0, 4))

        panel5, inner5 = self.make_panel(self.left_col, "CFG_ Buttons")
        panel5.pack(fill="x")
        tk.Button(inner5, text="CFG anwenden", width=12).pack(side="left", padx=(0, 4))
        tk.Button(inner5, text="CFG neu lesen", width=12).pack(side="left")

    def build_center_column(self):
        panel, inner = self.make_panel(self.center_col, "Hauptfenster")
        panel.grid(row=0, column=0, sticky="nsew")
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            inner,
            wrap="none",
            bg=CFG_COLOR_EDITOR_BG,
            font=("Consolas", 10),
            undo=False
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        yscroll = tk.Scrollbar(inner, command=self.text.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=yscroll.set)

        xscroll = tk.Scrollbar(inner, orient="horizontal", command=self.text.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self.text.configure(xscrollcommand=xscroll.set)

    def build_right_column(self):
        path_button_bar = tk.Frame(self.right_col, bg=CFG_COLOR_BG)
        path_button_bar.pack(fill="x", pady=(0, 4))
        tk.Button(path_button_bar, text="Dateifenster", width=12).pack(side="left")

        for block in DEMO_FILES_BY_PATH:
            panel, inner = self.make_panel(self.right_col, block["title"])
            panel.pack(fill="both", expand=True, pady=(0, 4))

            path_lbl = tk.Label(inner, text=block["path"], anchor="w", bg=CFG_COLOR_PANEL, fg=CFG_COLOR_HINT)
            path_lbl.pack(fill="x", pady=(0, 4))

            tree = ttk.Treeview(
                inner,
                columns=("size", "date", "status"),
                show="tree headings",
                height=7
            )
            tree.heading("#0", text="Name", anchor="w")
            tree.heading("size", text="Größe", anchor="w")
            tree.heading("date", text="Datum", anchor="w")
            tree.heading("status", text="Status", anchor="w")

            tree.column("#0", width=150, anchor="w")
            tree.column("size", width=50, anchor="w")
            tree.column("date", width=75, anchor="w")
            tree.column("status", width=55, anchor="w")

            apply_tree_status_colors(tree)
            tree.pack(fill="both", expand=True)

            for item in block["items"]:
                tags = ()
                if item["status"] == "aktiv":
                    tags = ("active",)
                elif item["status"] == "new":
                    tags = ("new",)
                elif item["status"] == "error":
                    tags = ("error",)

                tree.insert(
                    "",
                    "end",
                    text=item["name"],
                    values=(item["size"], item["date"], item["status"]),
                    tags=tags
                )

        bottom_quick = tk.Frame(self.right_col, bg=CFG_COLOR_BG)
        bottom_quick.pack(fill="x", pady=(2, 0))
        tk.Button(bottom_quick, text="Helfer", width=10).pack(side="left", padx=(0, 4))
        tk.Button(bottom_quick, text="Update", width=10).pack(side="left")

    def fill_demo_content(self):
        for item in DEMO_PARTS:
            self.list_parts_1.insert("end", "[PY] " + item)

        for item in DEMO_NEXT_LEVEL:
            self.list_parts_2.insert("end", item)

        for item in DEMO_CFGS:
            self.list_cfg.insert("end", item)

        self.entry_cfg_value.insert(0, '"#3399ff"')

        self.text.delete("1.0", "end")
        self.text.insert("1.0", read_fake_target_text())


# ===== PART: ENTRY START =====
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("default")
    except Exception:
        pass
    MockApp(root)
    root.mainloop()
# ===== PART: ENTRY END =====
