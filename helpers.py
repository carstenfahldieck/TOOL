# ===== PART: IMPORTS START =====
import os
import re
import shutil
from datetime import datetime
from tkinter import messagebox
# ===== PART: IMPORTS END =====


# ===== PART: HELPERS START =====
def remember_loaded_file_state(app, path):
    try:
        stat_info = os.stat(path)
        app.loaded_file_mtime = stat_info.st_mtime
        app.loaded_file_size = stat_info.st_size
    except Exception:
        app.loaded_file_mtime = None
        app.loaded_file_size = None


def was_file_changed_externally(app, path):
    if not os.path.exists(path):
        return False
    if app.current_file != path:
        return False
    if app.loaded_file_mtime is None:
        return False
    if app.loaded_file_size is None:
        return False

    try:
        stat_info = os.stat(path)
    except Exception:
        return False

    if stat_info.st_mtime != app.loaded_file_mtime:
        return True
    if stat_info.st_size != app.loaded_file_size:
        return True
    return False


def create_timestamp_backup(app, path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.dirname(path)
    backup_dir = os.path.join(base_dir, "backup")

    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    except Exception as exc:
        messagebox.showerror("Backup-Fehler", "Backup-Ordner konnte nicht erstellt werden:\n" + str(exc))
        app.status_var.set("Backup-Ordner fehlgeschlagen")
        return False

    filename = os.path.basename(path)
    backup_filename = filename + "." + timestamp + ".alt"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy2(path, backup_path)
    except Exception as exc:
        messagebox.showerror("Backup-Fehler", "Backup konnte nicht erstellt werden:\n" + str(exc))
        app.status_var.set("Backup fehlgeschlagen")
        return False

    return True


def find_part_index_by_name(app, name):
    index = 0
    while index < len(app.parts):
        if app.parts[index].name == name:
            return index
        index += 1
    return None


def find_part_index_by_name_fuzzy(app, name):
    exact = find_part_index_by_name(app, name)
    if exact is not None:
        return exact

    lowered = name.lower()

    index = 0
    while index < len(app.parts):
        if app.parts[index].name.lower() == lowered:
            return index
        index += 1

    index = 0
    while index < len(app.parts):
        part_name_lower = app.parts[index].name.lower()
        if (lowered in part_name_lower) or (part_name_lower in lowered):
            return index
        index += 1

    return None


def find_cfg_index_by_name(app, name):
    index = 0
    while index < len(app.config_vars):
        if app.config_vars[index].name == name:
            return index
        index += 1
    return None


def build_part_content_dict_from_editor(app):
    lines = app.text_editor.get("1.0", "end").split("\n")
    content_by_name = {}

    index = 0
    while index < len(app.parts):
        part = app.parts[index]
        inner_lines = lines[part.start + 1:part.end]
        content_by_name[part.name] = "\n".join(inner_lines)
        index += 1

    return content_by_name


def replace_part_in_text(full_text, part_name, new_inner_text):
    lines = full_text.split("\n")
    start_re = re.compile(r"^\s*(#|//)\s*=+\s*PART:\s*" + re.escape(part_name) + r"\s+START\s*=+\s*$")
    end_re = re.compile(r"^\s*(#|//)\s*=+\s*PART:\s*" + re.escape(part_name) + r"\s+END\s*=+\s*$")

    start_index = None
    end_index = None

    idx = 0
    while idx < len(lines):
        if start_re.match(lines[idx]):
            start_index = idx
            break
        idx += 1

    if start_index is None:
        return None

    idx = start_index + 1
    while idx < len(lines):
        if end_re.match(lines[idx]):
            end_index = idx
            break
        idx += 1

    if end_index is None:
        return None

    before = lines[:start_index + 1]
    after = lines[end_index:]

    replacement_lines = []
    if new_inner_text:
        replacement_lines = new_inner_text.split("\n")

    new_lines = before + replacement_lines + after
    return "\n".join(new_lines)
# ===== PART: HELPERS END =====
