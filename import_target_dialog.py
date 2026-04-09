# ===== PART: IMPORTS START =====
import tkinter as tk
from tkinter import ttk
# ===== PART: IMPORTS END =====


# ===== PART: DATA START =====
CURRENT_FILE = "fake_target.py"

RECENT_FILES = [
    "parts_logic.py",
    "app_core.py",
]

OPEN_FILES = [
    "fake_target.py",
    "parts_logic.py",
    "app_core.py",
    "cfg_logic.py",
    "save_logic.py",
]
# ===== PART: DATA END =====


# ===== PART: TOOLTIP START =====
class HoverTip:
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tip = None
        self.after_id = None

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event):
        self._cancel()
        self.after_id = self.widget.after(700, self._show)

    def _on_leave(self, event=None):
        self._cancel()
        self._hide()

    def _cancel(self):
        if self.after_id is not None:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def _show(self):
        self._hide()

        text = self.text_func()
        if not text:
            return

        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)

        x = self.widget.winfo_rootx() + 24
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(
            self.tip,
            text=text,
            justify=tk.LEFT,
            anchor="w",
            padx=8,
            pady=6,
            relief=tk.SOLID,
            borderwidth=1,
            wraplength=420,
            background="#fff8dc"
        )
        label.pack()

    def _hide(self):
        if self.tip is not None:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None
# ===== PART: TOOLTIP END =====


# ===== PART: DIALOG START =====
class ImportTargetDialog(tk.Toplevel):
    def __init__(self, master, part_name, current_file, recent_files, open_files):
        tk.Toplevel.__init__(self, master)
        self.title("Zieldatei für Import wählen")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        self.selected_file = None
        self.part_name = part_name
        self.current_file = current_file
        self.recent_files = recent_files[:]
        self.open_files = open_files[:]

        self._build_ui()
        self._center_on_parent(master)

    def _build_ui(self):
        outer = tk.Frame(self, padx=12, pady=12)
        outer.pack(fill="both", expand=True)

        info = tk.Label(
            outer,
            text=(
                "Importierter PART:\n"
                + self.part_name
                + "\n\n"
                + "Bitte Zieldatei bewusst auswählen.\n"
                + "Die aktuell geöffnete Datei steht oben."
            ),
            justify=tk.LEFT,
            anchor="w"
        )
        info.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(outer)
        row1.pack(fill="x", pady=(0, 6))

        tk.Label(row1, text="Aktuelle Datei:").pack(side="left")

        current_button = tk.Button(
            row1,
            text=self.current_file,
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=3,
            background="#d8f0d2",
            activebackground="#c7e9bf",
            command=lambda: self._use_direct(self.current_file)
        )
        current_button.pack(side="left", padx=(8, 0))

        HoverTip(
            current_button,
            lambda: (
                "Gerade aktive Datei.\n"
                "Wenn das dein Ziel ist, reicht ein Klick auf diesen Button."
            )
        )

        sep1 = ttk.Separator(outer, orient="horizontal")
        sep1.pack(fill="x", pady=8)

        box = tk.LabelFrame(outer, text="Datei aus Vorschlagsliste wählen", padx=8, pady=8)
        box.pack(fill="x")

        self.dropdown_map = {}
        display_values = []

        if self.current_file:
            text = "[AKTUELL] " + self.current_file
            display_values.append(text)
            self.dropdown_map[text] = self.current_file

        index = 0
        while index < len(self.recent_files):
            name = self.recent_files[index]
            if name and name != self.current_file:
                text = "[LETZT] " + name
                display_values.append(text)
                self.dropdown_map[text] = name
            index += 1

        index = 0
        while index < len(self.open_files):
            name = self.open_files[index]
            if name and name != self.current_file and name not in self.recent_files:
                text = "[OFFEN] " + name
                display_values.append(text)
                self.dropdown_map[text] = name
            index += 1

        self.combo_var = tk.StringVar()
        if len(display_values) > 0:
            self.combo_var.set(display_values[0])

        combo = ttk.Combobox(
            box,
            textvariable=self.combo_var,
            values=display_values,
            state="readonly",
            width=45
        )
        combo.pack(fill="x")

        HoverTip(
            combo,
            lambda: (
                "Oben steht immer die aktuelle Datei.\n"
                "Darunter die letzten Dateien.\n"
                "Danach weitere offene Dateien."
            )
        )

        btn_row = tk.Frame(outer)
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(
            btn_row,
            text="Diese Datei verwenden",
            width=20,
            command=self._use_dropdown
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Abbrechen",
            width=14,
            command=self._cancel
        ).pack(side="right")

    def _use_direct(self, path):
        self.selected_file = path
        self.destroy()

    def _use_dropdown(self):
        display = self.combo_var.get().strip()
        path = self.dropdown_map.get(display)
        if not path:
            return
        self.selected_file = path
        self.destroy()

    def _cancel(self):
        self.selected_file = None
        self.destroy()

    def _center_on_parent(self, master):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (width // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (height // 2)
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))
# ===== PART: DIALOG END =====


# ===== PART: APP START =====
class DemoApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("FAKE – Zieldatei Dialog V1")
        self.geometry("720x360")
        self.after(100, self.open_dialog)

        self.result_var = tk.StringVar()
        self.result_var.set("Noch keine Auswahl")

    def open_dialog(self):
        dlg = ImportTargetDialog(
            self,
            part_name="POPUP_CONTROL_TEST",
            current_file=CURRENT_FILE,
            recent_files=RECENT_FILES,
            open_files=OPEN_FILES
        )
        self.wait_window(dlg)

        if dlg.selected_file:
            self.result_var.set("Gewählte Zieldatei: " + dlg.selected_file)
        else:
            self.result_var.set("Auswahl abgebrochen")

        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    app = DemoApp()
    app.mainloop()
# ===== PART: APP END =====
