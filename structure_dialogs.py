# ===== PART: IMPORTS START =====
from tkinter import messagebox, simpledialog
# ===== PART: IMPORTS END =====


# ===== PART: STRUCTURE_NAME_DIALOGS START =====
def prompt_unique_structure_name(
    app,
    initial_name,
    title_text,
    prompt_text,
    exclude_name=None,
    empty_warning_text="Der Name darf nicht leer sein",
    duplicate_title="Name existiert bereits",
    duplicate_intro_text="Ein Struktur-Name mit diesem Namen existiert bereits."
):
    effective_name = app._normalize_structure_name(initial_name)
    normalized_exclude = app._normalize_structure_name(exclude_name)

    while True:
        if effective_name == "":
            new_name = simpledialog.askstring(
                title_text,
                prompt_text,
                initialvalue=""
            )

            if new_name is None:
                try:
                    app.status_var.set("Vorgang abgebrochen")
                except Exception:
                    pass
                return None

            effective_name = app._normalize_structure_name(new_name)

            if effective_name == "":
                messagebox.showwarning("Hinweis", empty_warning_text)
                continue

        if not app.is_structure_name_in_use(
            effective_name,
            exclude_name=normalized_exclude
        ):
            return effective_name

        suggestions = app.build_structure_name_suggestions(
            effective_name,
            exclude_name=normalized_exclude
        )

        message = (
            duplicate_intro_text + "\n\n"
            "Vorhandener Name: " + effective_name + "\n\n"
            "Vorschläge:\n"
            "- " + suggestions[0] + "\n"
            "- " + suggestions[1] + "\n"
            "- " + suggestions[2] + "\n\n"
            "Bitte neuen Namen eingeben oder Abbrechen wählen."
        )

        new_name = simpledialog.askstring(
            duplicate_title,
            message,
            initialvalue=suggestions[0]
        )

        if new_name is None:
            try:
                app.status_var.set("Vorgang abgebrochen")
            except Exception:
                pass
            return None

        effective_name = app._normalize_structure_name(new_name)

        if effective_name == "":
            messagebox.showwarning("Hinweis", empty_warning_text)
            continue
# ===== PART: STRUCTURE_NAME_DIALOGS END =====

# ===== PART: STRUCTURE_NAME_DIALOG_LIVE START =====
import tkinter as tk

def open_structure_name_dialog_live(app, title="Name eingeben", initial_value=""):
    result = {"value": None, "position": "after"}

    win = tk.Toplevel(app.root)
    win.title(title)
    win.geometry("760x330")
    win.transient(app.root)
    win.grab_set()
    win.resizable(False, False)

    outer = tk.Frame(win, padx=10, pady=10)
    outer.pack(fill="both", expand=True)

    selected = None
    prev_name = None
    next_name = None

    if app.part_listbox.curselection():
        idx = app.part_listbox.curselection()[0]
        selected = app.parts[idx].name

        if idx > 0:
            prev_name = app.parts[idx - 1].name

        if idx < len(app.parts) - 1:
            next_name = app.parts[idx + 1].name

    dim_fg = "#777777"
    main_fg = "black"
    suggestion_fg = "#888888"

    # ===== Kontext =====
    context_frame = tk.Frame(outer)
    context_frame.pack(fill="x", pady=(0, 10))

    if prev_name:
        tk.Label(
            context_frame,
            text="PART: " + prev_name,
            anchor="center",
            fg=dim_fg
        ).pack(fill="x")

    if selected:
        tk.Label(
            context_frame,
            text="PART: " + selected,
            anchor="center",
            fg=main_fg,
            font=("TkDefaultFont", 10, "bold")
        ).pack(fill="x", pady=(1, 1))

    if next_name:
        tk.Label(
            context_frame,
            text="PART: " + next_name,
            anchor="center",
            fg=dim_fg
        ).pack(fill="x")

    # ===== Eingabe =====
    suggested_text = initial_value if initial_value else "NEUER_PART"

    tk.Label(outer, text="Name:", anchor="w").pack(fill="x", pady=(0, 2))

    entry_var = tk.StringVar(value=suggested_text)
    entry = tk.Entry(outer, textvariable=entry_var)
    entry.pack(fill="x")
    entry.config(fg=suggestion_fg)

    normal_bg = entry.cget("bg")
    invalid_bg = "#f4b6b6"

    # ===== Kürzfunktion =====
    def shorten_middle(text, max_len):
        if max_len < 5:
            return text[:max_len]

        if len(text) <= max_len:
            return text

        left_len = (max_len - 3) // 2
        right_len = max_len - 3 - left_len
        return text[:left_len] + "..." + text[-right_len:]

    # ===== Einfügen =====
    tk.Label(outer, text="Einfügen:", anchor="w").pack(fill="x", pady=(12, 4))

    insert_row = tk.Frame(outer)
    insert_row.pack(fill="x", pady=(0, 8))

    pos_var = tk.StringVar(value="after")

    # --- linker Radiobutton ---
    rb_before = tk.Radiobutton(insert_row, variable=pos_var, value="before")
    rb_before.pack(side="left", padx=(0, 0))
    rb_before.config(padx=0, pady=0, borderwidth=0, highlightthickness=0)

    # --- linker PART ---
    left_var = tk.StringVar(value="")
    left_label = tk.Label(insert_row, textvariable=left_var, anchor="w")
    left_label.pack(side="left", padx=(0, 2))

    # --- Trennstrich ---
    sep_label = tk.Label(insert_row, text="|", anchor="center")
    sep_label.pack(side="left", padx=(2, 2))

    # --- rechter PART ---
    right_var = tk.StringVar(value="")
    right_label = tk.Label(insert_row, textvariable=right_var, anchor="w")
    right_label.pack(side="left", padx=(2, 2))

    # --- rechter Radiobutton ---
    rb_after = tk.Radiobutton(insert_row, variable=pos_var, value="after")
    rb_after.pack(side="left", padx=(2, 0))
    rb_after.config(padx=0, pady=0, borderwidth=0, highlightthickness=0)

    # ===== Übernommen wird =====
    tk.Label(outer, text="Übernommen wird:", anchor="w").pack(fill="x", pady=(10, 0))
    effective_var = tk.StringVar(value="")
    tk.Label(outer, textvariable=effective_var, fg="blue", anchor="w").pack(fill="x")

    # ===== Buttons =====
    btn_frame = tk.Frame(outer)
    btn_frame.pack(fill="x", pady=(16, 0))

    ok_btn = tk.Button(btn_frame, text="OK", state="disabled", width=12)
    ok_btn.pack(side="left")

    cancel_btn = tk.Button(btn_frame, text="Abbrechen", width=12)
    cancel_btn.pack(side="left", padx=(8, 0))

    # ===== Logik =====
    def build_effective_name(current, suggested):
        if current == suggested:
            return suggested

        if len(current) < len(suggested):
            return current

        return current

    def update_insert_row():
        left_part_name = prev_name if prev_name else selected
        right_part_name = next_name if next_name else selected

        if left_part_name is None:
            left_part_name = ""
        if right_part_name is None:
            right_part_name = ""
        if left_part_name == "":
            left_part_name = selected if selected else ""
        if right_part_name == "":
            right_part_name = selected if selected else ""

        left_text = "PART: " + left_part_name if left_part_name != "" else ""
        right_text = "PART: " + right_part_name if right_part_name != "" else ""

        max_total = 72
        total_len = len(left_text) + len(right_text) + 3

        if total_len > max_total:
            free_for_parts = max_total - 3

            if len(left_text) <= free_for_parts // 2:
                left_max = len(left_text)
                right_max = free_for_parts - left_max
            elif len(right_text) <= free_for_parts // 2:
                right_max = len(right_text)
                left_max = free_for_parts - right_max
            else:
                left_max = free_for_parts // 2
                right_max = free_for_parts - left_max

            left_text = shorten_middle(left_text, left_max)
            right_text = shorten_middle(right_text, right_max)

        left_var.set(left_text)
        right_var.set(right_text)

        if selected is None:
            rb_before.configure(state="disabled")
            rb_after.configure(state="disabled")
        else:
            rb_before.configure(state="normal")
            rb_after.configure(state="normal")
            if pos_var.get() not in ("before", "after"):
                pos_var.set("after")

    def validate(*args):
        current = entry_var.get()
        effective = build_effective_name(current, suggested_text)

        effective_var.set(effective)

        if current == suggested_text:
            entry.config(fg=suggestion_fg)
        else:
            entry.config(fg="black")

        if effective.strip() == "":
            entry.config(bg=invalid_bg)
            ok_btn.config(state="disabled")
            update_insert_row()
            return

        normalized = app._normalize_structure_name(effective)

        if app.is_structure_name_in_use(normalized):
            entry.config(bg=invalid_bg)
            ok_btn.config(state="disabled")
            update_insert_row()
            return

        entry.config(bg=normal_bg)
        ok_btn.config(state="normal")
        update_insert_row()

    def on_ok():
        current = entry_var.get()
        effective = build_effective_name(current, suggested_text)

        result["value"] = effective
        result["position"] = pos_var.get()
        win.destroy()

    def on_cancel():
        win.destroy()

    def on_keypress(event):
        nav_keys = (
            "Left", "Right", "Up", "Down",
            "Home", "End", "Prior", "Next",
            "Tab", "Shift_L", "Shift_R",
            "Control_L", "Control_R", "Alt_L", "Alt_R"
        )

        if event.keysym in nav_keys:
            return

        entry.config(fg="black")

    entry.bind("<KeyPress>", on_keypress)
    entry_var.trace_add("write", validate)

    ok_btn.config(command=on_ok)
    cancel_btn.config(command=on_cancel)

    entry.focus_set()
    entry.icursor(0)

    validate()

    win.wait_window()
    return result
# ===== PART: STRUCTURE_NAME_DIALOG_LIVE END =====

# ===== PART: STRUCTURE_PLACEMENT_DIALOG_V1 START =====

import tkinter as tk

def open_structure_placement_dialog_v1(app, parts, selected_index=None, suggested_name="NEUER_PART", mode="create"):

 result = {

  "name": None,

  "position_index": None,

  "hashtags": [],

  "note": ""

 }

 # ===== UI SETTINGS START =====

 cfg_ui_window_width = 800

 cfg_ui_window_height = 520

 cfg_ui_padding_outer = 10

 cfg_ui_spacing_small = 4

 cfg_ui_spacing_medium = 8

 cfg_ui_list_height = 15

 cfg_ui_color_free = "#888888"
 cfg_ui_color_selected = "#3399ff"

 cfg_ui_color_preview = "#008800"

 cfg_ui_suggestion_fg = "#888888"

 cfg_ui_normal_fg = "black"

 cfg_ui_invalid_bg = "#f4b6b6"

 cfg_ui_normal_bg = "white"

 cfg_ui_name_hint_text = "NAME_EINGEBEN (LEERZEICHEN=_)"

 # ===== UI SETTINGS END =====

 win = tk.Toplevel(app.root)

 win.title("PART einfügen / verschieben")

 win.geometry(str(cfg_ui_window_width) + "x" + str(cfg_ui_window_height))

 win.transient(app.root)

 win.grab_set()

 outer = tk.Frame(
  win,
  padx=cfg_ui_padding_outer,
  pady=cfg_ui_padding_outer
 )

 outer.pack(fill="both", expand=True)

 # ===== Name =====

 tk.Label(outer, text="Name:", anchor="w").pack(fill="x")

 initial_name = str(suggested_name).strip().upper()

 if initial_name == "":
  initial_name = cfg_ui_name_hint_text

 name_var = tk.StringVar(value=initial_name)

 entry_name = tk.Entry(outer, textvariable=name_var, fg=cfg_ui_suggestion_fg)

 entry_name.pack(fill="x", pady=(0, cfg_ui_spacing_medium))
 entry_name.icursor(0)
 entry_name.selection_range(0, tk.END)

 suggestion_mode = {"value": True}

 # ===== Positionsliste =====

 tk.Label(outer, text="Position wählen:", anchor="w").pack(fill="x")

 frame_list = tk.Frame(outer)
 frame_list.pack(fill="both", expand=True)

 listbox_positions = tk.Listbox(frame_list, height=cfg_ui_list_height)
 listbox_positions.pack(side="left", fill="both", expand=True)

 scrollbar_positions = tk.Scrollbar(frame_list)
 scrollbar_positions.pack(side="right", fill="y")

 listbox_positions.config(yscrollcommand=scrollbar_positions.set)
 scrollbar_positions.config(command=listbox_positions.yview)

 # ===== Bemerkung =====

 tk.Label(outer, text="Bemerkung:", anchor="w").pack(fill="x", pady=(cfg_ui_spacing_medium, 0))

 note_var = tk.StringVar()
 entry_note = tk.Entry(outer, textvariable=note_var)
 entry_note.pack(fill="x", pady=(0, cfg_ui_spacing_small))

 # ===== Hashtags =====

 tk.Label(outer, text="Hashtags:", anchor="w").pack(fill="x")

 hashtags_var = tk.StringVar()
 entry_hashtags = tk.Entry(outer, textvariable=hashtags_var)
 entry_hashtags.pack(fill="x", pady=(0, cfg_ui_spacing_medium))

 # ===== Buttons =====

 frame_buttons = tk.Frame(outer)
 frame_buttons.pack(fill="x")

 btn_ok = tk.Button(frame_buttons, text="OK", width=12, state="disabled")
 btn_ok.pack(side="left")

 btn_cancel = tk.Button(frame_buttons, text="Abbrechen", width=12)
 btn_cancel.pack(side="left", padx=(cfg_ui_spacing_small, 0))

 selected_free_index = {"value": None}

 def normalize_name(value):

  raw = str(value)

  if raw == cfg_ui_name_hint_text:
   return ""

  raw = raw.replace(" ", "_")

  try:
   return app._normalize_structure_name(raw).upper()
  except Exception:
   return raw.strip().upper()

 def is_name_in_use(value, exclude_name=None):

  try:
   return app.is_structure_name_in_use(value, exclude_name=exclude_name)
  except TypeError:

   normalized = normalize_name(value)
   normalized_exclude = normalize_name(exclude_name) if exclude_name else None

   i = 0
   while i < len(parts):
    candidate = normalize_name(parts[i])

    if normalized_exclude is not None and candidate == normalized_exclude:
     i += 1
     continue

    if candidate == normalized:
     return True

    i += 1

   return False

  except Exception:

   normalized = normalize_name(value)
   normalized_exclude = normalize_name(exclude_name) if exclude_name else None

   i = 0
   while i < len(parts):
    candidate = normalize_name(parts[i])

    if normalized_exclude is not None and candidate == normalized_exclude:
     i += 1
     continue

    if candidate == normalized:
     return True

    i += 1

   return False

 def parse_hashtags(value):

  raw = str(value).strip()

  if raw == "":
   return []

  parts_raw = raw.split("#")
  result_tags = []

  i = 0
  while i < len(parts_raw):
   tag = parts_raw[i].strip()
   if tag != "":
    result_tags.append(tag)
   i += 1

  return result_tags

 def build_rows():

  rows = []

  if mode == "rename":
   i = 0
   while i < len(parts):
    rows.append({"kind": "part", "display": parts[i]})
    i += 1
   return rows

  rows.append({"kind": "free", "display": "[frei]"})

  index = 0
  while index < len(parts):
   rows.append({"kind": "part", "display": "PART: " + str(parts[index])})
   rows.append({"kind": "free", "display": "[frei]"})
   index += 1

  return rows

 def refresh_position_list():

  listbox_positions.delete(0, tk.END)

  rows = build_rows()
  preview_name = normalize_name(name_var.get())

  i = 0
  while i < len(rows):

   display_text = rows[i]["display"]

   if mode != "rename":
    if rows[i]["kind"] == "free" and selected_free_index["value"] == i:
     if preview_name != "":
      display_text = ">>> " + preview_name + " <<<"
     else:
      display_text = ">>> [frei] <<<"

   listbox_positions.insert(tk.END, display_text)

   if rows[i]["kind"] == "free":
    try:
     if selected_free_index["value"] == i and mode != "rename":
      listbox_positions.itemconfig(i, fg=cfg_ui_color_preview)
     else:
      listbox_positions.itemconfig(i, fg=cfg_ui_color_free)
    except Exception:
     pass

   i += 1

  if selected_free_index["value"] is not None:
   try:
    if selected_free_index["value"] >= 0 and selected_free_index["value"] < len(rows):
     listbox_positions.selection_clear(0, tk.END)
     listbox_positions.selection_set(selected_free_index["value"])
     listbox_positions.activate(selected_free_index["value"])
     listbox_positions.see(selected_free_index["value"])
   except Exception:
    pass
  else:
   if mode == "rename" and selected_index is not None:
    try:
     if selected_index >= 0 and selected_index < len(rows):
      listbox_positions.selection_clear(0, tk.END)
      listbox_positions.selection_set(selected_index)
      listbox_positions.activate(selected_index)
      listbox_positions.see(selected_index)
      selected_free_index["value"] = selected_index
    except Exception:
      selected_free_index["value"] = None
   elif mode != "rename" and selected_index is not None:
    try:
     preview_index = (selected_index * 2) + 2
     if preview_index >= 0 and preview_index < len(rows):
      listbox_positions.selection_clear(0, tk.END)
      listbox_positions.selection_set(preview_index)
      listbox_positions.activate(preview_index)
      listbox_positions.see(preview_index)
      selected_free_index["value"] = preview_index
    except Exception:
      selected_free_index["value"] = None

 def validate():

  raw_name = name_var.get()

  if suggestion_mode["value"] and raw_name == cfg_ui_name_hint_text:
   btn_ok.config(state="disabled")
   entry_name.config(bg=cfg_ui_normal_bg, fg=cfg_ui_suggestion_fg)
   return

  normalized_name = normalize_name(raw_name)

  if normalized_name == "":
   btn_ok.config(state="disabled")
   entry_name.config(bg=cfg_ui_invalid_bg, fg=cfg_ui_normal_fg)
   return

  exclude_name = None
  if mode == "rename":
   exclude_name = suggested_name

  if is_name_in_use(normalized_name, exclude_name=exclude_name):
   btn_ok.config(state="disabled")
   entry_name.config(bg=cfg_ui_invalid_bg, fg=cfg_ui_normal_fg)
   return

  if selected_free_index["value"] is None:
   btn_ok.config(state="disabled")
   entry_name.config(bg=cfg_ui_normal_bg, fg=cfg_ui_normal_fg)
   return

  btn_ok.config(state="normal")
  entry_name.config(bg=cfg_ui_normal_bg, fg=cfg_ui_normal_fg)

 def on_name_focus_in(event=None):
  if suggestion_mode["value"]:
   name_var.set("")
   entry_name.config(fg=cfg_ui_normal_fg)
   try:
    entry_name.icursor(0)
   except Exception:
    pass
   suggestion_mode["value"] = False
   validate()
   refresh_position_list()

 def on_name_keyrelease(event=None):

  current = name_var.get()
  upper = current.replace(" ", "_").upper()

  cursor = None
  try:
   cursor = entry_name.index(tk.INSERT)
  except Exception:
   cursor = None

  if current != upper:
   name_var.set(upper)
   try:
    if cursor is not None:
     entry_name.icursor(cursor)
   except Exception:
    pass

  validate()
  refresh_position_list()

 def on_position_select(event=None):

  sel = listbox_positions.curselection()
  if not sel:
   selected_free_index["value"] = None
   validate()
   refresh_position_list()
   return

  row_index = sel[0]
  rows = build_rows()

  if row_index < 0 or row_index >= len(rows):
   selected_free_index["value"] = None
   validate()
   refresh_position_list()
   return

  if mode == "rename":
   if rows[row_index]["kind"] == "part":
    selected_free_index["value"] = row_index
   else:
    selected_free_index["value"] = None
  else:
   if rows[row_index]["kind"] == "free":
    selected_free_index["value"] = row_index
   else:
    selected_free_index["value"] = None

  validate()
  refresh_position_list()

 def on_ok():

  name_text = normalize_name(name_var.get())

  if name_text == "":
   return

  exclude_name = None
  if mode == "rename":
   exclude_name = suggested_name

  if is_name_in_use(name_text, exclude_name=exclude_name):
   return

  row_index = selected_free_index["value"]
  if row_index is None:
   return

  hashtags = parse_hashtags(hashtags_var.get())

  result["name"] = name_text
  result["position_index"] = row_index
  result["hashtags"] = hashtags
  result["note"] = note_var.get().strip()

  win.destroy()

 def on_cancel():
  win.destroy()

 listbox_positions.bind("<<ListboxSelect>>", on_position_select)
 entry_name.bind("<FocusIn>", on_name_focus_in)
 entry_name.bind("<KeyRelease>", on_name_keyrelease)

 btn_ok.config(command=on_ok)
 btn_cancel.config(command=on_cancel)

 refresh_position_list()
 validate()

 entry_name.focus_set()

 win.wait_window()

 return result
# ===== PART: STRUCTURE_PLACEMENT_DIALOG_V1 END =====
# ===== PART: STRUCTURE_SIMPLE_DIALOG_V1 START =====
def open_structure_simple_dialog_v1(
    parent,
    suggested_name="",
    window_title="Neuer PART",
    hint_line_1="",
    hint_line_2="",
    show_hint_lines=False,
    enable_name_validation=True,
    use_grab=True,
    wait_for_close=True,
    external_name_validator=None,
    external_ok_validator=None
):
    result = {
        "name": None,
        "position_index": None,
        "note": "",
        "hashtags": "",
        "window": None,
        "name_var": None,
        "note_var": None,
        "tag_var": None,
        "hint1_var": None,
        "hint2_var": None,
        "btn_ok": None,
        "btn_cancel": None,
        "name_entry": None,
        "validate_func": None
    }

    win = tk.Toplevel(parent)
    win.title(window_title)
    win.geometry("400x300")
    win.transient(parent)

    if use_grab:
        win.grab_set()

    main_frame = tk.Frame(win, padx=10, pady=10)
    main_frame.pack(fill="both", expand=True)

    hint1_var = None
    hint2_var = None

    # ===== HINWEISE =====
    if show_hint_lines:
        hint1_var = tk.StringVar(value=hint_line_1)
        hint2_var = tk.StringVar(value=hint_line_2)

        hint1_label = tk.Label(main_frame, textvariable=hint1_var, anchor="w", justify="left")
        hint1_label.pack(fill="x", pady=(0, 2))

        hint2_label = tk.Label(main_frame, textvariable=hint2_var, anchor="w", justify="left")
        hint2_label.pack(fill="x", pady=(0, 10))

    # ===== NAME =====
    tk.Label(main_frame, text="Name").pack(anchor="w")

    name_var = tk.StringVar(value=suggested_name)
    name_entry = tk.Entry(main_frame, textvariable=name_var)
    name_entry.pack(fill="x", pady=(0, 10))

    # ===== NOTE =====
    tk.Label(main_frame, text="Bemerkung").pack(anchor="w")
    note_var = tk.StringVar()
    note_entry = tk.Entry(main_frame, textvariable=note_var)
    note_entry.pack(fill="x", pady=(0, 10))

    # ===== HASHTAGS =====
    tk.Label(main_frame, text="Hashtags").pack(anchor="w")
    tag_var = tk.StringVar()
    tag_entry = tk.Entry(main_frame, textvariable=tag_var)
    tag_entry.pack(fill="x", pady=(0, 10))

    # ===== BUTTONS =====
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))

    btn_ok = tk.Button(button_frame, text="OK")
    btn_ok.pack(side="left", expand=True, fill="x", padx=(0, 5))

    btn_cancel = tk.Button(button_frame, text="Abbrechen")
    btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def validate_name():
        value = name_var.get().strip()

        if not enable_name_validation:
            btn_ok.config(state="normal")
            name_entry.config(bg="white")
            return True

        if value == "":
            btn_ok.config(state="disabled")
            name_entry.config(bg="#f4b6b6")
            return False

        if external_name_validator is not None:
            try:
                is_ok = external_name_validator(value)
            except Exception:
                is_ok = False

            if not is_ok:
                btn_ok.config(state="disabled")
                name_entry.config(bg="#f4b6b6")
                return False

        # ===== ZUSATZPRÜFUNG FÜR OK =====
        if external_ok_validator is not None:
            try:
                is_ok = external_ok_validator()
            except Exception:
                is_ok = False

            if not is_ok:
                btn_ok.config(state="disabled")
                name_entry.config(bg="white")
                return False

        btn_ok.config(state="normal")
        name_entry.config(bg="white")
        return True

    def on_name_change(*args):
        validate_name()

    def on_ok():
        if not validate_name():
            return

        result["name"] = name_var.get().strip()
        result["note"] = note_var.get().strip()
        result["hashtags"] = tag_var.get().strip()
        win.destroy()

    def on_cancel():
        win.destroy()

    name_var.trace_add("write", on_name_change)

    btn_ok.config(command=on_ok)
    btn_cancel.config(command=on_cancel)

    validate_name()

    name_entry.focus_set()

    result["window"] = win
    result["name_var"] = name_var
    result["note_var"] = note_var
    result["tag_var"] = tag_var
    result["hint1_var"] = hint1_var
    result["hint2_var"] = hint2_var
    result["btn_ok"] = btn_ok
    result["btn_cancel"] = btn_cancel
    result["name_entry"] = name_entry
    result["validate_func"] = validate_name

    if wait_for_close:
        parent.wait_window(win)

        if not result["name"] and enable_name_validation:
            return None

    return result
# ===== PART: STRUCTURE_SIMPLE_DIALOG_V1 END =====
