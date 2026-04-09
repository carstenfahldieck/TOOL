# ===== PART: IMPORTS START =====
import tkinter as tk
# ===== PART: IMPORTS END =====


# ===== PART: DIALOG_LOGIC START =====
def ask_three_way(master, title, message, option1, option2, option3):
    """
    Zeigt einen Dialog mit 3 frei benannten Buttons.
    Rückgabe:
        "option1" | "option2" | "option3" | None

    optionX Format:
        ("Text", "hotkey")
    Beispiel:
        ("Vor", "v")
    """
    result = {"value": None}

    win = tk.Toplevel(master)
    win.title("[DIALOG] " + title)
    win.transient(master)
    win.grab_set()
    win.resizable(False, False)

    try:
        win.configure(padx=12, pady=12)
    except Exception:
        pass

    text_frame = tk.Frame(win)
    text_frame.pack(fill=tk.BOTH, expand=True)

    lbl = tk.Label(
        text_frame,
        text=message,
        justify=tk.LEFT,
        anchor="w",
        wraplength=460
    )
    lbl.pack(fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(win)
    button_frame.pack(fill=tk.X, pady=(12, 0))

    def choose(value):
        result["value"] = value
        try:
            win.grab_release()
        except Exception:
            pass
        win.destroy()

    def get_underline_index(text, hotkey):
        if not hotkey:
            return -1

        hotkey_lower = hotkey.lower()
        index = 0
        while index < len(text):
            if text[index].lower() == hotkey_lower:
                return index
            index += 1
        return -1

    btn1_text, btn1_key = option1
    btn2_text, btn2_key = option2
    btn3_text, btn3_key = option3

    btn1_underline = get_underline_index(btn1_text, btn1_key)
    btn2_underline = get_underline_index(btn2_text, btn2_key)
    btn3_underline = get_underline_index(btn3_text, btn3_key)

    btn1 = tk.Button(
        button_frame,
        text=btn1_text,
        width=16,
        underline=btn1_underline,
        command=lambda: choose("option1")
    )
    btn2 = tk.Button(
        button_frame,
        text=btn2_text,
        width=16,
        underline=btn2_underline,
        command=lambda: choose("option2")
    )
    btn3 = tk.Button(
        button_frame,
        text=btn3_text,
        width=16,
        underline=btn3_underline,
        command=lambda: choose("option3")
    )

    btn1.pack(side=tk.LEFT, padx=(0, 6))
    btn2.pack(side=tk.LEFT, padx=(0, 6))
    btn3.pack(side=tk.LEFT)

    key_map = {}

    if btn1_key:
        key_map[btn1_key.lower()] = "option1"
    if btn2_key:
        key_map[btn2_key.lower()] = "option2"
    if btn3_key:
        key_map[btn3_key.lower()] = "option3"

    def on_key(event):
        key = ""
        try:
            key = event.keysym.lower()
        except Exception:
            pass

        if key == "escape":
            choose("option3")
            return "break"

        if key in key_map:
            choose(key_map[key])
            return "break"

        return None

    def on_close():
        choose("option3")

    win.bind("<Key>", on_key)
    win.protocol("WM_DELETE_WINDOW", on_close)

    try:
        win.update_idletasks()
        master_x = master.winfo_rootx()
        master_y = master.winfo_rooty()
        master_w = master.winfo_width()
        master_h = master.winfo_height()
        win_w = win.winfo_reqwidth()
        win_h = win.winfo_reqheight()

        pos_x = master_x + max(0, (master_w - win_w) // 2)
        pos_y = master_y + max(0, (master_h - win_h) // 2)

        win.geometry("+{0}+{1}".format(pos_x, pos_y))
    except Exception:
        pass

    btn1.focus_set()
    win.wait_window()

    return result["value"]
# ===== PART: DIALOG_LOGIC END =====