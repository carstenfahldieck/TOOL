import tkinter as tk
from tkinter import messagebox


# ===== PART: PICKER_HELPERS START =====
def picker_trim_common_indent(block_lines):
    min_indent = None
    index = 0

    while index < len(block_lines):
        line = block_lines[index][1]
        if str(line).strip() != "":
            indent = len(line) - len(line.lstrip(" "))
            if min_indent is None or indent < min_indent:
                min_indent = indent
        index += 1

    if min_indent is None:
        min_indent = 0

    trimmed = []
    index = 0

    while index < len(block_lines):
        src_idx, line = block_lines[index]

        if line.strip() == "":
            trimmed.append((src_idx, ""))
        else:
            if len(line) >= min_indent:
                trimmed.append((src_idx, line[min_indent:]))
            else:
                trimmed.append((src_idx, line))

        index += 1

    return trimmed


def picker_collapse_inner_blank_runs(block_lines):
    result = []
    last_was_blank = False

    index = 0
    while index < len(block_lines):
        src_idx, line = block_lines[index]
        is_blank = (str(line).strip() == "")

        if is_blank:
            if not last_was_blank:
                result.append((src_idx, ""))
            last_was_blank = True
        else:
            result.append((src_idx, line))
            last_was_blank = False

        index += 1

    return result


def picker_clean_free_block(block_lines):
    block_lines = picker_trim_common_indent(block_lines)
    block_lines = picker_collapse_inner_blank_runs(block_lines)

    while len(block_lines) > 0 and str(block_lines[0][1]).strip() == "":
        del block_lines[0]

    while len(block_lines) > 0 and str(block_lines[-1][1]).strip() == "":
        del block_lines[-1]

    return block_lines


def picker_extract_part_name(line_text):
    text = str(line_text).strip()
    marker = "PART:"
    start_word = "START"

    if marker not in text or start_word not in text:
        return "UNBEKANNT"

    try:
        after_marker = text.split(marker, 1)[1]
        before_start = after_marker.rsplit(start_word, 1)[0]
        name = before_start.strip().strip("=-# ")
        if name != "":
            return name
    except Exception:
        pass

    return "UNBEKANNT"


def picker_toggle_color(color_name):
    if color_name == "yellow":
        return "green"
    return "yellow"
# ===== PART: PICKER_HELPERS END =====


# ===== PART: PICKER_DATA_BUILD START =====
def picker_build_rendered_items(lines):
    free_buffer = []
    current_color = "yellow"
    inside_part = False
    seen_first_free_block = False
    pending_parts = []

    rendered_items = []
    free_block_count = 0

    def append_part_group_if_needed():
        if len(pending_parts) == 0:
            return

        if len(rendered_items) > 0 and rendered_items[-1]["kind"] != "blank":
            rendered_items.append({"kind": "blank"})

        rendered_items.append({"kind": "divider"})

        part_index = 0
        while part_index < len(pending_parts):
            rendered_items.append({
                "kind": "part",
                "text": "PART: " + pending_parts[part_index]["name"]
            })
            part_index += 1

        rendered_items.append({"kind": "divider"})
        rendered_items.append({"kind": "blank"})

        del pending_parts[:]

    def append_free_block(cleaned_block):
        nonlocal current_color
        nonlocal seen_first_free_block
        nonlocal free_block_count

        if len(cleaned_block) == 0:
            return False

        if seen_first_free_block and len(pending_parts) > 0:
            append_part_group_if_needed()

        index = 0
        while index < len(cleaned_block):
            src_idx, line = cleaned_block[index]
            rendered_items.append({
                "kind": "block_line",
                "text": line,
                "color": current_color,
                "src_idx": src_idx
            })
            index += 1

        rendered_items.append({"kind": "blank"})

        seen_first_free_block = True
        free_block_count += 1
        current_color = picker_toggle_color(current_color)
        return True

    index = 0
    current_part_name = None

    while index < len(lines):
        line = lines[index]
        stripped = str(line).strip()

        is_part_start = ("PART" in stripped and "START" in stripped)
        is_part_end = ("PART" in stripped and "END" in stripped)

        if not inside_part:
            if is_part_start:
                cleaned = picker_clean_free_block(free_buffer)
                free_buffer = []

                append_free_block(cleaned)

                if seen_first_free_block:
                    current_part_name = picker_extract_part_name(stripped)
                else:
                    current_part_name = None

                inside_part = True
            else:
                free_buffer.append((index, line))
        else:
            if is_part_end:
                if seen_first_free_block and current_part_name is not None:
                    pending_parts.append({
                        "name": current_part_name
                    })

                inside_part = False
                current_part_name = None

        index += 1

    cleaned = picker_clean_free_block(free_buffer)
    append_free_block(cleaned)

    return {
        "items": rendered_items,
        "free_block_count": free_block_count
    }
# ===== PART: PICKER_DATA_BUILD END =====


# ===== PART: PICKER_VIEW_BUILD START =====
def picker_build_view(parent, rendered):
    wrapper = tk.Frame(parent, bg="white")
    wrapper.pack(fill=tk.BOTH, expand=True)

    text_widget = tk.Text(
        wrapper,
        wrap=tk.NONE,
        bg="white",
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground="#c8c8c8",
        padx=4,
        pady=4
    )
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scroll_y = tk.Scrollbar(wrapper, orient=tk.VERTICAL, command=text_widget.yview)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.configure(yscrollcommand=scroll_y.set)

    text_widget.tag_configure("block_yellow", background="#ffe699")
    text_widget.tag_configure("block_green", background="#c6efce")
    text_widget.tag_configure("part_line", foreground="#444444")
    text_widget.tag_configure("divider_line", foreground="#888888")

    items = rendered["items"]

    item_index = 0
    while item_index < len(items):
        item = items[item_index]
        kind = item["kind"]

        if kind == "blank":
            text_widget.insert("end", "\n")

        elif kind == "divider":
            text_widget.insert("end", "────────────────────────────────────────────────────────\n")
            line_no = int(text_widget.index("end-1c").split(".")[0])
            text_widget.tag_add(
                "divider_line",
                "{0}.0".format(line_no),
                "{0}.end".format(line_no)
            )

        elif kind == "part":
            text_widget.insert("end", item["text"] + "\n")
            line_no = int(text_widget.index("end-1c").split(".")[0])
            text_widget.tag_add(
                "part_line",
                "{0}.0".format(line_no),
                "{0}.end".format(line_no)
            )

        elif kind == "block_line":
            text_widget.insert("end", item["text"] + "\n")
            line_no = int(text_widget.index("end-1c").split(".")[0])

            if item["color"] == "yellow":
                text_widget.tag_add(
                    "block_yellow",
                    "{0}.0".format(line_no),
                    "{0}.end".format(line_no)
                )
            else:
                text_widget.tag_add(
                    "block_green",
                    "{0}.0".format(line_no),
                    "{0}.end".format(line_no)
                )

        item_index += 1

    text_widget.configure(state="normal")

    return {
        "wrapper": wrapper,
        "text_widget": text_widget
    }
# ===== PART: PICKER_VIEW_BUILD END =====


# ===== PART: ENTRY_POINT START =====
def show_block_picker_preview(master, target_file):
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        rendered = picker_build_rendered_items(lines)

        if rendered["free_block_count"] == 0:
            messagebox.showinfo(
                "Kein freier Bereich",
                "Es wurde kein freier Textbereich gefunden."
            )
            return

        win = tk.Toplevel(master)
        win.title("Block-Picker Vorschau")
        win.geometry("900x600")

        header = tk.Label(
            win,
            text="REPARATUR-STUFE 2: Freie Bereiche und PART-Zwischenblöcke sichtbar. Buttons noch nicht aktiv.",
            anchor="w",
            bg="#cc0000",
            fg="white",
            padx=8,
            pady=6
        )
        header.pack(fill=tk.X)

        picker_build_view(win, rendered)

    except Exception as e:
        messagebox.showerror("Fehler", str(e))
# ===== PART: ENTRY_POINT END =====
