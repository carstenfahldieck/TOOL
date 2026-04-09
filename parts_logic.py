# ===== PART: IMPORTS START =====
import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from helpers import find_part_index_by_name, find_part_index_by_name_fuzzy
from dialogs_custom import ask_three_way
# ===== PART: IMPORTS END =====


# ===== PART: DATA_STRUCTURES START =====
class Part:
    def __init__(self, name, start, end, marker_prefix):
        self.name = name
        self.start = start
        self.end = end
        self.marker_prefix = marker_prefix
# ===== PART: DATA_STRUCTURES END =====


# ===== PART: CLASS_MAIN START =====
class PartsLogicMixin:

    # ===== PART: PARSER_LOGIC START =====
    def scan_parts(self):
        self.parts = []
        self.part_listbox.delete(0, tk.END)

        text = self.text_editor.get("1.0", tk.END)
        lines = text.splitlines()

        start_re = re.compile(r"^\s*(#|//)\s*=+\s*PART:\s*(.+?)\s+START\s*=+\s*$")
        end_re = re.compile(r"^\s*(#|//)\s*=+\s*PART:\s*(.+?)\s+END\s*=+\s*$")

        stack = {}
        index = 0

        while index < len(lines):
            line = lines[index]

            start_match = start_re.match(line)
            if start_match:
                marker_prefix = start_match.group(1)
                part_name = start_match.group(2).strip()
                stack[part_name] = (index, marker_prefix)
                index += 1
                continue

            end_match = end_re.match(line)
            if end_match:
                marker_prefix = end_match.group(1)
                part_name = end_match.group(2).strip()

                if part_name in stack:
                    start_line, start_prefix = stack[part_name]
                    if start_prefix == marker_prefix:
                        self.parts.append(Part(part_name, start_line, index, marker_prefix))
                        del stack[part_name]

            index += 1

        self.parts.sort(key=lambda item: item.start)

        index = 0
        while index < len(self.parts):
            part = self.parts[index]
            prefix = "PY" if part.marker_prefix == "#" else "CS"
            suffix = " *" if part.name in self.dirty_part_names else ""
            self.part_listbox.insert(tk.END, "[{0}] {1}{2}".format(prefix, part.name, suffix))
            index += 1

        self.update_action_states()

    def on_part_select(self, event):
        if not self.part_listbox.curselection():
            self.update_action_states()
            return

        self.clear_replace_diff_marks()

        index = self.part_listbox.curselection()[0]
        part = self.parts[index]

        self.status_var.set("PART gewählt: " + part.name)
        self.apply_editor_marks(active_part_name=part.name)
        self.ensure_part_visible_nicely(part)

        try:
            self.highlight_cfgs_for_part(part)
        except Exception:
            pass

        self.update_action_states()
    # ===== PART: PARSER_LOGIC END =====

    # ===== PART: VIEW_HELPERS START =====
    def ensure_part_visible_nicely(self, part):
        start_line_1based = part.start + 1
        top_margin = 5
        desired_line = max(1, start_line_1based - top_margin)

        total_lines = len(self.text_editor.get("1.0", tk.END).splitlines())
        if total_lines <= 0:
            return

        fraction = float(desired_line - 1) / float(total_lines)
        self.text_editor.yview_moveto(fraction)
        self.text_editor.see("{0}.0".format(start_line_1based))

    def preview_target_part(self, part):
        if part is None:
            return

        start_index = "{0}.0".format(part.start + 1)
        end_index = "{0}.0 lineend".format(part.end + 1)

        self.text_editor.tag_add("replace_preview_target", start_index, end_index)
        self.ensure_part_visible_nicely(part)
    # ===== PART: VIEW_HELPERS END =====

    # ===== PART: RIGHT_DIFF_HELPERS START =====
    def clear_replace_diff_marks(self):
        self.replace_input.tag_remove("replace_diff_line", "1.0", tk.END)

    def mark_replace_diff_lines(self, old_lines, new_lines):
        self.clear_replace_diff_marks()

        max_len = len(old_lines)
        if len(new_lines) > max_len:
            max_len = len(new_lines)

        index = 0
        while index < max_len:
            old_line = ""
            new_line = ""

            if index < len(old_lines):
                old_line = old_lines[index]
            if index < len(new_lines):
                new_line = new_lines[index]

            if old_line != new_line:
                start_index = "{0}.0".format(index + 1)
                end_index = "{0}.0 lineend".format(index + 1)
                self.replace_input.tag_add("replace_diff_line", start_index, end_index)

            index += 1

    def preview_diff_for_target_part(self, part, incoming_inner_text):
        current_lines = self.text_editor.get("1.0", tk.END).splitlines()
        old_inner_lines = current_lines[part.start + 1:part.end]

        new_inner_lines = []
        cleaned_text = incoming_inner_text.rstrip("\n")
        if cleaned_text:
            new_inner_lines = cleaned_text.splitlines()

        self.mark_replace_diff_lines(old_inner_lines, new_inner_lines)
    # ===== PART: RIGHT_DIFF_HELPERS END =====

    # ===== PART: MARKING START =====
    def clear_all_highlights(self):
        self.text_editor.tag_remove("part_active", "1.0", tk.END)
        self.text_editor.tag_remove("cfg_highlight", "1.0", tk.END)
        self.text_editor.tag_remove("part_changed_soft", "1.0", tk.END)
        self.text_editor.tag_remove("replace_preview_target", "1.0", tk.END)

    def apply_editor_marks(self, active_part_name=None):
        self.clear_all_highlights()

        index = 0
        while index < len(self.parts):
            part = self.parts[index]
            start_index = "{0}.0".format(part.start + 1)
            end_index = "{0}.0 lineend".format(part.end + 1)

            if (part.name in self.last_changed_part_names) or (part.name in self.dirty_part_names):
                self.text_editor.tag_add("part_changed_soft", start_index, end_index)

            if active_part_name == part.name:
                self.text_editor.tag_add("part_active", start_index, end_index)

            index += 1
    # ===== PART: MARKING END =====

    # ===== PART: LINE_INSERT_HELPERS START =====
    def insert_block_with_spacing(self, lines, insert_index, block_lines):
        new_lines = lines[:]

        if insert_index > 0 and insert_index <= len(new_lines):
            prev_line = new_lines[insert_index - 1]
            if prev_line.strip() != "":
                block_lines = [""] + block_lines

        if insert_index < len(new_lines):
            next_line = new_lines[insert_index]
            if next_line.strip() != "":
                block_lines = block_lines + [""]

        return new_lines[:insert_index] + block_lines + new_lines[insert_index:]
    # ===== PART: LINE_INSERT_HELPERS END =====

    # ===== PART: ADD_PART START =====
    def add_new_part(self):
        part_name = simpledialog.askstring("Neuer PART", "Name des neuen PART:")
        if not part_name:
            return

        effective_name = self._normalize_structure_name(part_name)
        if effective_name == "":
            return

        while self.is_structure_name_in_use(effective_name):
            suggestions = self.build_structure_name_suggestions(effective_name)

            message = (
                "Ein PART mit diesem Namen existiert bereits in der aktuellen Datei.\n\n"
                "Vorhandener Name: " + effective_name + "\n\n"
                "Vorschläge:\n"
                "- " + suggestions[0] + "\n"
                "- " + suggestions[1] + "\n"
                "- " + suggestions[2] + "\n\n"
                "Bitte neuen Namen eingeben oder Abbrechen wählen."
            )

            new_name = simpledialog.askstring(
                "Name existiert bereits",
                message,
                initialvalue=suggestions[0]
            )

            if new_name is None:
                self.status_var.set("Einfügen abgebrochen")
                return

            effective_name = self._normalize_structure_name(new_name)

            if effective_name == "":
                messagebox.showwarning("Hinweis", "Der neue Name darf nicht leer sein")
                continue

        new_part_lines = [
            "# ===== PART: " + effective_name + " START =====",
            "",
            "# ===== PART: " + effective_name + " END ====="
        ]

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        insert_index = None

        if self.part_listbox.curselection():
            sel_index = self.part_listbox.curselection()[0]
            selected_part = self.parts[sel_index]

            answer = ask_three_way(
                self.root,
                "PART einfügen",
                "Wo soll der neue PART eingefügt werden?\n\n"
                "Gewählter PART: " + selected_part.name,
                ("Vor", "v"),
                ("Nach", "n"),
                ("Abbrechen", "a")
            )

            if answer == "option3" or answer is None:
                self.status_var.set("Einfügen abgebrochen")
                return

            if answer == "option1":
                insert_index = selected_part.start
            else:
                insert_index = selected_part.end + 1
        else:
            answer = ask_three_way(
                self.root,
                "PART einfügen",
                "Es ist noch kein Ziel-PART ausgewählt.\n\n"
                "Was soll passieren?",
                ("PART auswählen", "p"),
                ("Am Ende", "e"),
                ("Abbrechen", "a")
            )

            if answer == "option3" or answer is None:
                self.status_var.set("Einfügen abgebrochen")
                return

            if answer == "option1":
                self.status_var.set("Bitte links Ziel-PART auswählen und 'Neuer PART' erneut ausführen")
                return

            insert_index = len(lines)

        new_lines = self.insert_block_with_spacing(lines, insert_index, new_part_lines)

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(new_lines).rstrip("\n") + "\n")

        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")

        self.rescan_all()
        self.update_dirty_parts()

        new_index = find_part_index_by_name(self, effective_name)
        if new_index is not None:
            self.part_listbox.selection_clear(0, tk.END)
            self.part_listbox.selection_set(new_index)
            self.part_listbox.activate(new_index)
            self.on_part_select(None)

        self.status_var.set("Neuer PART erstellt: " + effective_name)
    # ===== PART: ADD_PART END =====

    # ===== PART: REMOVE_PART START =====
    def remove_selected_part(self):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Kein PART ausgewählt")
            return

        index = self.part_listbox.curselection()[0]
        part = self.parts[index]

        answer = ask_three_way(
            self.root,
            "PART löschen",
            "Was soll mit dem PART passieren?\n\n"
            "PART: " + part.name,
            ("Mit Backup", "m"),
            ("Ohne Backup", "o"),
            ("Abbrechen", "a")
        )

        if answer == "option3" or answer is None:
            self.status_var.set("PART löschen abgebrochen")
            return

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        removed = lines[part.start:part.end + 1]

        if answer == "option1":
            if not self.save_part_backup(part.name, removed):
                self.status_var.set("Backup abgebrochen")
                return

        new_lines = lines[:part.start] + lines[part.end + 1:]

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(new_lines).rstrip("\n") + "\n")

        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")

        self.rescan_all()
        self.update_dirty_parts()

        if len(self.parts) > 0:
            new_index = index
            if new_index >= len(self.parts):
                new_index = len(self.parts) - 1

            self.part_listbox.selection_clear(0, tk.END)
            self.part_listbox.selection_set(new_index)
            self.part_listbox.activate(new_index)
            self.on_part_select(None)
        else:
            self.clear_all_highlights()
            self.cfg_listbox.selection_clear(0, tk.END)
            self.cfg_name_var.set("")
            self.cfg_value_var.set("")
            self.cfg_line_var.set("")
            self.cfg_value_entry.delete("1.0", tk.END)

        self.status_var.set("PART gelöscht: " + part.name)

    def save_part_backup(self, name, lines):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "{0}_backup_{1}.txt".format(name, ts)

        path = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".txt"
        )
        if not path:
            return False

        f = open(path, "w", encoding="utf-8")
        f.write("\n".join(lines).rstrip("\n") + "\n")
        f.close()

        return True
    # ===== PART: REMOVE_PART END =====

    # ===== PART: INSERT_HELPERS START =====
    def _normalize_structure_name(self, name):
        if name is None:
            return ""

        text = str(name).strip().upper()

        while "  " in text:
            text = text.replace("  ", " ")

        return text

    def is_structure_name_in_use(self, name, exclude_name=None):
        normalized_name = self._normalize_structure_name(name)
        normalized_exclude = self._normalize_structure_name(exclude_name)

        if normalized_name == "":
            return False

        index = 0
        while index < len(self.parts):
            existing_name = self._normalize_structure_name(self.parts[index].name)

            if existing_name == normalized_name:
                if normalized_exclude != "" and existing_name == normalized_exclude:
                    index += 1
                    continue
                return True

            index += 1

        return False

    def build_structure_name_suggestions(self, base_name, exclude_name=None):
        normalized_base = self._normalize_structure_name(base_name)
        normalized_exclude = self._normalize_structure_name(exclude_name)

        if normalized_base == "":
            normalized_base = "NEUER_NAME"

        suggestions = []
        counter = 2

        while len(suggestions) < 3:
            candidate = normalized_base + "_" + str(counter)

            if candidate == normalized_exclude:
                counter += 1
                continue

            if not self.is_structure_name_in_use(candidate, exclude_name=normalized_exclude):
                suggestions.append(candidate)

            counter += 1

        return suggestions

    def rename_full_part_markers(self, full_part_text, old_name, new_name):
        old_name = self._normalize_structure_name(old_name)
        new_name = self._normalize_structure_name(new_name)

        if old_name == "" or new_name == "":
            return full_part_text

        lines = full_part_text.splitlines()
        new_lines = []

        start_re = re.compile(r"^(\s*)(#|//)(\s*=+\s*PART:\s*)" + re.escape(old_name) + r"(\s+START\s*=+\s*)$")
        end_re = re.compile(r"^(\s*)(#|//)(\s*=+\s*PART:\s*)" + re.escape(old_name) + r"(\s+END\s*=+\s*)$")

        index = 0
        while index < len(lines):
            line = lines[index]

            start_match = start_re.match(line)
            if start_match:
                line = (
                    start_match.group(1)
                    + start_match.group(2)
                    + start_match.group(3)
                    + new_name
                    + start_match.group(4)
                )
            else:
                end_match = end_re.match(line)
                if end_match:
                    line = (
                        end_match.group(1)
                        + end_match.group(2)
                        + end_match.group(3)
                        + new_name
                        + end_match.group(4)
                    )

            new_lines.append(line)
            index += 1

        return "\n".join(new_lines)

    def ask_insert_position_for_part(self, incoming_part_name):
        if self.part_listbox.curselection():
            sel_index = self.part_listbox.curselection()[0]
            selected_part = self.parts[sel_index]

            answer = ask_three_way(
                self.root,
                "PART einfügen",
                "PART '" + incoming_part_name + "' soll eingefügt werden.\n\n"
                "Wo soll er eingefügt werden?\n\n"
                "Gewählter PART: " + selected_part.name,
                ("Vor", "v"),
                ("Nach", "n"),
                ("Abbrechen", "a")
            )

            if answer == "option3" or answer is None:
                return None

            if answer == "option1":
                return selected_part.start
            return selected_part.end + 1

        answer = ask_three_way(
            self.root,
            "PART einfügen",
            "PART '" + incoming_part_name + "' soll eingefügt werden.\n\n"
            "Es ist kein PART ausgewählt.",
            ("PART auswählen", "p"),
            ("Am Ende", "e"),
            ("Abbrechen", "a")
        )

        if answer == "option3" or answer is None:
            return None

        if answer == "option1":
            self.status_var.set("Bitte links Ziel-PART auswählen und den Vorgang erneut ausführen")
            return None

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        return len(lines)

    def insert_new_part_block_from_text(self, full_part_text, incoming_part_name):
        effective_name = self._normalize_structure_name(incoming_part_name)

        if effective_name == "":
            messagebox.showwarning("Hinweis", "PART-Name fehlt")
            self.status_var.set("Einfügen abgebrochen")
            return False

        while self.is_structure_name_in_use(effective_name):
            suggestions = self.build_structure_name_suggestions(effective_name)

            message = (
                "Ein PART mit diesem Namen existiert bereits in der aktuellen Datei.\n\n"
                "Vorhandener Name: " + effective_name + "\n\n"
                "Vorschläge:\n"
                "- " + suggestions[0] + "\n"
                "- " + suggestions[1] + "\n"
                "- " + suggestions[2] + "\n\n"
                "Bitte neuen Namen eingeben oder Abbrechen wählen."
            )

            new_name = simpledialog.askstring(
                "Name existiert bereits",
                message,
                initialvalue=suggestions[0]
            )

            if new_name is None:
                self.status_var.set("Einfügen abgebrochen")
                return False

            effective_name = self._normalize_structure_name(new_name)

            if effective_name == "":
                messagebox.showwarning("Hinweis", "Der neue Name darf nicht leer sein")
                continue

        if effective_name != incoming_part_name:
            full_part_text = self.rename_full_part_markers(
                full_part_text,
                incoming_part_name,
                effective_name
            )

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        insert_index = self.ask_insert_position_for_part(effective_name)

        if insert_index is None:
            self.status_var.set("Einfügen abgebrochen")
            return False

        incoming_lines = full_part_text.splitlines()
        new_lines = self.insert_block_with_spacing(lines, insert_index, incoming_lines)

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(new_lines).rstrip("\n") + "\n")

        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")

        self.rescan_all()
        self.update_dirty_parts()

        new_index = find_part_index_by_name(self, effective_name)
        if new_index is not None:
            self.part_listbox.selection_clear(0, tk.END)
            self.part_listbox.selection_set(new_index)
            self.part_listbox.activate(new_index)
            self.on_part_select(None)

        self.status_var.set("Neuer PART eingefügt: " + effective_name)
        return True
    # ===== PART: INSERT_HELPERS END =====

# ===== PART: REPLACE_LOGIC START =====
    def _safe_undo_push_snapshot(self):
        try:
            if not hasattr(self, "_safe_undo_stack"):
                self._safe_undo_stack = []

            current_text = self.text_editor.get("1.0", tk.END)
            self._safe_undo_stack.append(current_text)

            if len(self._safe_undo_stack) > 20:
                self._safe_undo_stack.pop(0)
        except Exception:
            pass

    def _replace_main_editor_text_single_undo_step(self, new_full_text):
        widget = self.text_editor

        self._safe_undo_push_snapshot()

        try:
            old_autosep = widget.cget("autoseparators")
        except Exception:
            old_autosep = True

        try:
            widget.config(autoseparators=False)
        except Exception:
            pass

        try:
            widget.edit_separator()
        except Exception:
            pass

        widget.delete("1.0", tk.END)
        widget.insert("1.0", new_full_text)

        try:
            widget.edit_separator()
        except Exception:
            pass

        try:
            widget.config(autoseparators=old_autosep)
        except Exception:
            pass

    def _safe_undo_restore(self):
        try:
            if hasattr(self, "_safe_undo_stack") and self._safe_undo_stack:
                last_text = self._safe_undo_stack.pop()

                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", last_text)

                self.rescan_all()
                self.update_dirty_parts()
                self.apply_editor_marks()
                self.status_var.set("Sicherheits-Undo ausgeführt")
                return True
        except Exception:
            pass

        return False

    def _file_contains_part_name(self, path, part_name):
        try:
            f = open(path, "r", encoding="utf-8")
            content = f.read()
            f.close()
        except Exception:
            return False

        return ("PART: " + part_name + " START") in content

    def _select_part_in_current_file_by_name(self, part_name):
        index = 0
        while index < len(self.parts):
            if self.parts[index].name == part_name:
                self.part_listbox.selection_clear(0, tk.END)
                self.part_listbox.selection_set(index)
                self.part_listbox.activate(index)
                self.on_part_select(None)
                return self.parts[index]
            index += 1
        return None

    def _build_replace_preview_data(self, part, replacement_text):
        old_lines = self.text_editor.get("1.0", tk.END).splitlines()
        old_inner_lines = old_lines[part.start + 1:part.end]

        cleaned_text = replacement_text.rstrip("\n")
        new_inner_lines = []
        if cleaned_text:
            new_inner_lines = cleaned_text.split("\n")

        changed_count = 0
        max_len = len(old_inner_lines)
        if len(new_inner_lines) > max_len:
            max_len = len(new_inner_lines)

        index = 0
        while index < max_len:
            old_line = ""
            new_line = ""

            if index < len(old_inner_lines):
                old_line = old_inner_lines[index]
            if index < len(new_inner_lines):
                new_line = new_inner_lines[index]

            if old_line != new_line:
                changed_count += 1

            index += 1

        old_text = "\n".join(old_inner_lines)
        new_text = "\n".join(new_inner_lines)

        return old_text, new_text, changed_count

    def _mark_preview_line_diff(self, text_widget, old_lines, new_lines, tag_name):
        max_len = len(old_lines)
        if len(new_lines) > max_len:
            max_len = len(new_lines)

        index = 0
        while index < max_len:
            old_line = ""
            new_line = ""

            if index < len(old_lines):
                old_line = old_lines[index]
            if index < len(new_lines):
                new_line = new_lines[index]

            if old_line != new_line:
                start_index = "{0}.0".format(index + 1)
                end_index = "{0}.0 lineend".format(index + 1)
                text_widget.tag_add(tag_name, start_index, end_index)

            index += 1

    def _is_word_char(self, ch):
        if not ch:
            return False
        return ch.isalnum() or ch == "_"

    def _expand_diff_to_token_bounds(self, line_text, start_col, end_col):
        if not line_text:
            return start_col, end_col

        if start_col < 0:
            start_col = 0
        if end_col < start_col:
            end_col = start_col
        if end_col >= len(line_text):
            end_col = len(line_text) - 1

        left = start_col
        right = end_col

        if left < len(line_text):
            if self._is_word_char(line_text[left]):
                while left > 0 and self._is_word_char(line_text[left - 1]):
                    left -= 1

        if right < len(line_text):
            if self._is_word_char(line_text[right]):
                while right + 1 < len(line_text) and self._is_word_char(line_text[right + 1]):
                    right += 1

        return left, right

    def _mark_preview_char_diff(self, old_widget, new_widget, old_lines, new_lines):
        max_lines = len(old_lines)
        if len(new_lines) > max_lines:
            max_lines = len(new_lines)

        row = 0
        while row < max_lines:
            old_line = ""
            new_line = ""

            if row < len(old_lines):
                old_line = old_lines[row]
            if row < len(new_lines):
                new_line = new_lines[row]

            if old_line != new_line:
                old_len = len(old_line)
                new_len = len(new_line)
                max_len = old_len
                if new_len > max_len:
                    max_len = new_len

                diffs = []
                i = 0
                while i < max_len:
                    oc = ""
                    nc = ""

                    if i < old_len:
                        oc = old_line[i]
                    if i < new_len:
                        nc = new_line[i]

                    if oc != nc:
                        diffs.append(i)

                    i += 1

                if diffs:
                    start_col = diffs[0]
                    end_col = diffs[-1]

                    old_start = start_col
                    old_end = end_col
                    new_start = start_col
                    new_end = end_col

                    if old_len > 0:
                        if old_start >= old_len:
                            old_start = old_len - 1
                        if old_end >= old_len:
                            old_end = old_len - 1
                        if old_start < 0:
                            old_start = 0
                        if old_end < old_start:
                            old_end = old_start
                        old_start, old_end = self._expand_diff_to_token_bounds(old_line, old_start, old_end)

                    if new_len > 0:
                        if new_start >= new_len:
                            new_start = new_len - 1
                        if new_end >= new_len:
                            new_end = new_len - 1
                        if new_start < 0:
                            new_start = 0
                        if new_end < new_start:
                            new_end = new_start
                        new_start, new_end = self._expand_diff_to_token_bounds(new_line, new_start, new_end)

                    if old_len > 0:
                        old_widget.tag_add(
                            "char_changed_old",
                            "{0}.{1}".format(row + 1, old_start),
                            "{0}.{1}".format(row + 1, old_end + 1)
                        )

                    if new_len > 0:
                        new_widget.tag_add(
                            "char_changed_new",
                            "{0}.{1}".format(row + 1, new_start),
                            "{0}.{1}".format(row + 1, new_end + 1)
                        )

            row += 1

    def _get_first_changed_preview_line(self, old_lines, new_lines):
        max_len = len(old_lines)
        if len(new_lines) > max_len:
            max_len = len(new_lines)

        index = 0
        while index < max_len:
            old_line = ""
            new_line = ""

            if index < len(old_lines):
                old_line = old_lines[index]
            if index < len(new_lines):
                new_line = new_lines[index]

            if old_line != new_line:
                return index + 1

            index += 1

        return 1

    def _scroll_preview_both_to_line(self, old_widget, new_widget, target_line):
        try:
            total_old = len(old_widget.get("1.0", tk.END).splitlines())
            total_new = len(new_widget.get("1.0", tk.END).splitlines())
            total_lines = total_old
            if total_new > total_lines:
                total_lines = total_new

            if total_lines <= 1:
                old_widget.see("{0}.0".format(target_line))
                new_widget.see("{0}.0".format(target_line))
                return

            top_line = target_line - 3
            if top_line < 1:
                top_line = 1

            fraction = float(top_line - 1) / float(total_lines)
            old_widget.yview_moveto(fraction)
            new_widget.yview_moveto(fraction)

            old_widget.see("{0}.0".format(target_line))
            new_widget.see("{0}.0".format(target_line))
        except Exception:
            pass

    def _show_replace_preview_dialog(self, part, replacement_text):
        old_text, new_text, changed_count = self._build_replace_preview_data(part, replacement_text)

        dialog = tk.Toplevel(self.root)
        dialog.title("Vorschau vor Ersetzen")
        dialog.geometry("1200x720")
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.grid_rowconfigure(1, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_columnconfigure(1, weight=1)

        target_file = ""
        if self.current_file:
            target_file = self.current_file

        info_text = (
            "Datei: {0}\n"
            "PART: {1}\n"
            "Geänderte Zeilen: {2}"
        ).format(target_file, part.name, changed_count)

        info = tk.Label(
            dialog,
            text=info_text,
            justify=tk.LEFT,
            anchor="w",
            padx=12,
            pady=8
        )
        info.grid(row=0, column=0, columnspan=2, sticky="ew")

        left_frame = tk.LabelFrame(dialog, text="ALT")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        right_frame = tk.LabelFrame(dialog, text="NEU")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        old_widget = tk.Text(left_frame, wrap=tk.NONE)
        old_widget.grid(row=0, column=0, sticky="nsew")

        new_widget = tk.Text(right_frame, wrap=tk.NONE)
        new_widget.grid(row=0, column=0, sticky="nsew")

        old_widget.insert("1.0", old_text)
        new_widget.insert("1.0", new_text)

        old_scroll_y = tk.Scrollbar(left_frame, orient=tk.VERTICAL)
        old_scroll_y.grid(row=0, column=1, sticky="ns")

        new_scroll_y = tk.Scrollbar(right_frame, orient=tk.VERTICAL)
        new_scroll_y.grid(row=0, column=1, sticky="ns")

        def scroll_both(*args):
            old_widget.yview(*args)
            new_widget.yview(*args)

        def sync_old(first, last):
            old_scroll_y.set(first, last)
            new_scroll_y.set(first, last)

        def sync_new(first, last):
            old_scroll_y.set(first, last)
            new_scroll_y.set(first, last)

        old_widget.configure(yscrollcommand=sync_old)
        new_widget.configure(yscrollcommand=sync_new)
        old_scroll_y.configure(command=scroll_both)
        new_scroll_y.configure(command=scroll_both)

        old_scroll_x = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=old_widget.xview)
        old_scroll_x.grid(row=1, column=0, sticky="ew")
        old_widget.configure(xscrollcommand=old_scroll_x.set)

        new_scroll_x = tk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=new_widget.xview)
        new_scroll_x.grid(row=1, column=0, sticky="ew")
        new_widget.configure(xscrollcommand=new_scroll_x.set)

        def on_mousewheel(event):
            delta = 0
            try:
                if event.delta != 0:
                    if event.delta > 0:
                        delta = -1
                    else:
                        delta = 1
                elif hasattr(event, "num"):
                    if event.num == 4:
                        delta = -1
                    elif event.num == 5:
                        delta = 1
            except Exception:
                pass

            if delta != 0:
                old_widget.yview_scroll(delta, "units")
                new_widget.yview_scroll(delta, "units")
            return "break"

        old_widget.bind("<MouseWheel>", on_mousewheel)
        new_widget.bind("<MouseWheel>", on_mousewheel)
        old_widget.bind("<Button-4>", on_mousewheel)
        old_widget.bind("<Button-5>", on_mousewheel)
        new_widget.bind("<Button-4>", on_mousewheel)
        new_widget.bind("<Button-5>", on_mousewheel)

        old_widget.tag_configure("line_changed_old", background="#ffe08a")
        new_widget.tag_configure("line_changed_new", background="#c6f7c3")

        old_widget.tag_configure("char_changed_old", background="#ff7f7f")
        new_widget.tag_configure("char_changed_new", background="#6ee56e")

        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        self._mark_preview_line_diff(old_widget, old_lines, new_lines, "line_changed_old")
        self._mark_preview_line_diff(new_widget, old_lines, new_lines, "line_changed_new")
        self._mark_preview_char_diff(old_widget, new_widget, old_lines, new_lines)

        first_changed_line = self._get_first_changed_preview_line(old_lines, new_lines)
        self._scroll_preview_both_to_line(old_widget, new_widget, first_changed_line)

        old_widget.configure(state="disabled")
        new_widget.configure(state="disabled")

        result = {"apply": False}

        button_row = tk.Frame(dialog)
        button_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        def do_apply(event=None):
            result["apply"] = True
            dialog.destroy()

        def do_cancel(event=None):
            result["apply"] = False
            dialog.destroy()

        btn_apply = tk.Button(button_row, text="Übernehmen", width=14, command=do_apply)
        btn_apply.pack(side=tk.RIGHT, padx=(5, 0))

        btn_cancel = tk.Button(button_row, text="Abbrechen", width=14, command=do_cancel)
        btn_cancel.pack(side=tk.RIGHT)

        dialog.bind("<Return>", do_apply)
        dialog.bind("<Escape>", do_cancel)

        btn_apply.focus_set()
        dialog.wait_window()

        return result["apply"]

    def replace_part(self):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Kein PART ausgewählt")
            return

        index = self.part_listbox.curselection()[0]
        part = self.parts[index]

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        inner_lines = lines[part.start + 1:part.end]

        self.replace_input.delete("1.0", tk.END)
        self.replace_input.insert("1.0", "\n".join(inner_lines))
        self.clear_replace_diff_marks()
        self.detected_part_var.set("Manueller Modus für PART: " + part.name)
        self.status_var.set("PART-Inhalt geladen")
        self.update_action_states()

    def paste_clipboard_to_replace_box(self):
        try:
            clip_text = self.root.clipboard_get()
        except Exception:
            messagebox.showerror("Zwischenablage-Fehler", "Zwischenablage ist leer oder kein Text")
            return

        self.replace_input.delete("1.0", tk.END)
        self.replace_input.insert("1.0", clip_text)
        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")
        self.status_var.set("Zwischenablage eingefügt")
        self.update_action_states()

    def replace_from_clipboard(self):
        try:
            clip_text = self.root.clipboard_get()
        except Exception:
            messagebox.showerror("Zwischenablage-Fehler", "Zwischenablage ist leer oder kein Text")
            return

        self.replace_input.delete("1.0", tk.END)
        self.replace_input.insert("1.0", clip_text)
        self.apply_replace_from_box()

    def clear_replace_box(self):
        self.replace_input.delete("1.0", tk.END)
        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")

        active_part_name = None
        if self.part_listbox.curselection():
            index = self.part_listbox.curselection()[0]
            active_part_name = self.parts[index].name

        self.apply_editor_marks(active_part_name=active_part_name)
        self.status_var.set("Ersetzen-Feld geleert")
        self.update_action_states()

    def detect_target_part_from_replace_box(self):
        replace_text = self.replace_input.get("1.0", tk.END).strip()
        if not replace_text:
            messagebox.showwarning("Hinweis", "Ersetzen-Feld ist leer")
            return

        detected_name, inner_text = self.extract_part_name_and_inner_text(replace_text)

        if not detected_name:
            messagebox.showwarning("Hinweis", "Kein PART erkannt")
            return

        matching_files = []

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]
            if self._file_contains_part_name(path, detected_name):
                matching_files.append(path)
            index += 1

        if len(matching_files) == 0:
            self.status_var.set("Kein passender PART gefunden: " + detected_name)
            messagebox.showwarning("Hinweis", "Kein passender PART in geladenen Dateien gefunden")
            self.highlight_matching_project_files([])
            self.pending_target_part_name = None
            return

        if self.current_file and self._file_contains_part_name(self.current_file, detected_name):
            self.pending_target_part_name = detected_name
            self.clear_matching_project_files()

            part = self._select_part_in_current_file_by_name(detected_name)
            if part is not None:
                self.apply_editor_marks(active_part_name=part.name)
                self.preview_target_part(part)
                self.preview_diff_for_target_part(part, inner_text)

            self.status_var.set("Aktive Datei passt bereits: " + detected_name)
            return

        if len(matching_files) == 1:
            target_path = matching_files[0]

            self.pending_target_part_name = detected_name
            self.highlight_matching_project_files([target_path])
            self.switch_to_project_file(target_path)

            part_index = find_part_index_by_name_fuzzy(self, detected_name)
            if part_index is not None:
                part = self.parts[part_index]
                self.apply_editor_marks(active_part_name=part.name)
                self.preview_target_part(part)
                self.preview_diff_for_target_part(part, inner_text)

            self.status_var.set("Ziel automatisch gefunden: " + detected_name)
            return

        self.pending_target_part_name = detected_name
        self.highlight_matching_project_files(matching_files)

        self.status_var.set(
            "Mehrere mögliche Ziele gefunden für PART: " + detected_name
        )

        messagebox.showinfo(
            "Mehrere Treffer",
            "Mehrere passende Dateien gefunden.\n\n"
            "Wenn die richtige Datei bereits aktiv ist, einfach erneut 'Ersetzen' drücken.\n"
            "Sonst gewünschte Datei auswählen."
        )

    def apply_replace_from_box(self):
        replace_text = self.replace_input.get("1.0", tk.END).strip()

        if not replace_text:
            messagebox.showwarning("Hinweis", "Kein Inhalt zum Ersetzen vorhanden")
            return

        detected_name, inner_text = self.extract_part_name_and_inner_text(replace_text)

        if not detected_name:
            messagebox.showwarning("Fehler", "Kein gültiger PART erkannt")
            return

        if self.current_file and self._file_contains_part_name(self.current_file, detected_name):
            found_part = self._select_part_in_current_file_by_name(detected_name)

            if found_part is not None:
                if getattr(self, "preview_replace_var", None) is not None and self.preview_replace_var.get():
                    if not self._show_replace_preview_dialog(found_part, inner_text):
                        self.status_var.set("Ersetzen abgebrochen")
                        return

                self.replace_part_content(found_part, inner_text)
                self.clear_replace_box()
                self.clear_matching_project_files()
                self.pending_target_part_name = None
                self.status_var.set("PART ersetzt in aktiver Datei")
                return

        matching_files = []

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]
            if self._file_contains_part_name(path, detected_name):
                matching_files.append(path)
            index += 1

        if len(matching_files) == 0:
            messagebox.showerror(
                "Kein Ziel gefunden",
                "PART '{0}' wurde in keiner Datei gefunden.".format(detected_name)
            )
            self.highlight_matching_project_files([])
            self.pending_target_part_name = None
            return

        if len(matching_files) == 1:
            target = matching_files[0]
            self.pending_target_part_name = detected_name

            if self.current_file != target:
                self.load_file_by_path(target)

            found_part = self._select_part_in_current_file_by_name(detected_name)

            if found_part is None:
                messagebox.showerror(
                    "Fehler",
                    "PART wurde nach Dateiwechsel nicht gefunden: {0}".format(detected_name)
                )
                return

            if getattr(self, "preview_replace_var", None) is not None and self.preview_replace_var.get():
                if not self._show_replace_preview_dialog(found_part, inner_text):
                    self.status_var.set("Ersetzen abgebrochen")
                    return

            self.replace_part_content(found_part, inner_text)
            self.clear_replace_box()
            self.clear_matching_project_files()
            self.pending_target_part_name = None
            self.status_var.set("Automatisch richtige Datei gewählt und ersetzt")
            return

        self.pending_target_part_name = detected_name
        self.highlight_matching_project_files(matching_files)

        messagebox.showwarning(
            "Mehrere Treffer",
            "PART '{0}' wurde in mehreren Dateien gefunden.\n\n"
            "Wenn die gewünschte Datei jetzt aktiv ist, einfach erneut 'Ersetzen' drücken.\n"
            "Sonst gewünschte Datei auswählen (hellblau markiert) und danach erneut 'Ersetzen' drücken.".format(detected_name)
        )

    def replace_part_content(self, part, replacement_text):
        cleaned_text = replacement_text.rstrip("\n")

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        before = lines[:part.start + 1]
        after = lines[part.end:]

        replacement_lines = []
        if cleaned_text:
            replacement_lines = cleaned_text.split("\n")

        new_lines = before + replacement_lines + after
        new_full_text = "\n".join(new_lines).rstrip("\n") + "\n"

        self._replace_main_editor_text_single_undo_step(new_full_text)

        self.clear_replace_diff_marks()
        self.detected_part_var.set("Kein Ziel erkannt")
        self.last_changed_part_names = set([part.name])

        self.rescan_all()
        self.update_dirty_parts()
        self.apply_editor_marks(active_part_name=part.name)
        self.ensure_part_visible_nicely(part)
# ===== PART: REPLACE_LOGIC END =====

# ===== PART: EXPORT_IMPORT START =====

    def import_part_file(self):
        from import_target_dialog import ImportTargetDialog

        path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[("PART-Dateien", "*.py *.txt"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                import_text = f.read()
        except Exception as exc:
            messagebox.showerror("Import-Fehler", str(exc))
            return

        if not import_text.strip():
            messagebox.showwarning("Hinweis", "Import-Datei ist leer")
            return

        detected_name, cleaned_text = self.extract_part_name_and_inner_text(import_text)

        if not detected_name:
            messagebox.showwarning("Hinweis", "Kein gültiger PART erkannt")
            return

        dlg = ImportTargetDialog(
            self.root,
            part_name=detected_name,
            current_file=self.current_file,
            recent_files=self.project_files[:3],
            open_files=self.project_files
        )
        self.root.wait_window(dlg)

        target_path = dlg.selected_file

        if not target_path:
            self.append_assistant_log("Import abgebrochen: keine Zieldatei gewählt")
            return

        if self.current_file != target_path:
            if not self.confirm_discard_unsaved_changes():
                return
            self.load_file_by_path(target_path)

        index = find_part_index_by_name_fuzzy(self, detected_name)

        if index is not None:
            answer = ask_three_way(
                self.root,
                "Import anwenden",
                "PART existiert bereits:\n\n" + detected_name,
                ("Ersetzen", "e"),
                ("Nur laden", "l"),
                ("Abbrechen", "a")
            )

            if answer == "option1":
                self.replace_input.delete("1.0", tk.END)
                self.replace_input.insert("1.0", cleaned_text)
                self.detect_target_part_from_replace_box()
                self.apply_replace_from_box()
                self.append_assistant_log("Import ersetzt in: " + os.path.basename(target_path))

        else:
            answer = ask_three_way(
                self.root,
                "Neuen PART importieren",
                "Neuer PART:\n\n" + detected_name,
                ("Einfügen", "e"),
                ("Nur laden", "l"),
                ("Abbrechen", "a")
            )

            if answer == "option1":
                self.insert_new_part_block_from_text(cleaned_text, detected_name)
                self.append_assistant_log("Import eingefügt in: " + os.path.basename(target_path))

# ===== PART: EXPORT_IMPORT END =====
# ===== PART: CLASS_MAIN END =====


# ===== PART: RENAME_SELECTED_MARKER START =====
    def _build_renamed_boundary_line_from_existing(self, line_text, old_name, new_name):
        if line_text is None:
            return None

        old_name = self._normalize_marker_name(old_name)
        new_name = self._normalize_marker_name(new_name)

        if old_name == "" or new_name == "":
            return line_text

        pattern = re.compile(
            r"^(\s*)(#|//)(\s*=+\s*[A-Z_]+\s*:\s*)"
            + re.escape(old_name)
            + r"(\s+(START|END)\s*=+\s*)$"
        )

        match = pattern.match(line_text)
        if not match:
            return line_text

        return (
            match.group(1)
            + match.group(2)
            + match.group(3)
            + new_name
            + match.group(4)
        )

    def _rename_selected_block_boundaries(self, new_name):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Bitte zuerst links einen PART auswählen")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        sel_index = self.part_listbox.curselection()[0]
        if sel_index < 0 or sel_index >= len(self.parts):
            messagebox.showwarning("Hinweis", "Auswahl ist ungültig")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        selected_part = self.parts[sel_index]
        old_name = self._normalize_marker_name(selected_part.name)
        new_name = self._normalize_marker_name(new_name)

        if old_name == "":
            messagebox.showwarning("Hinweis", "Der aktuelle PART-Name ist leer")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if new_name == "":
            messagebox.showwarning("Hinweis", "Der neue Name darf nicht leer sein")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if new_name == old_name:
            self.status_var.set("Name unverändert")
            return False

        if self.is_structure_name_in_use(new_name, exclude_name=old_name):
            messagebox.showwarning(
                "Hinweis",
                "Ein PART mit diesem Namen existiert bereits in der aktuellen Datei"
            )
            self.status_var.set("Umbenennen abgebrochen")
            return False

        lines = self.text_editor.get("1.0", tk.END).splitlines()

        if selected_part.start < 0 or selected_part.start >= len(lines):
            messagebox.showwarning("Hinweis", "START-Zeile konnte nicht gefunden werden")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if selected_part.end < 0 or selected_part.end >= len(lines):
            messagebox.showwarning("Hinweis", "END-Zeile konnte nicht gefunden werden")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        lines[selected_part.start] = self._build_renamed_boundary_line_from_existing(
            lines[selected_part.start],
            old_name,
            new_name
        )
        lines[selected_part.end] = self._build_renamed_boundary_line_from_existing(
            lines[selected_part.end],
            old_name,
            new_name
        )

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(lines).rstrip("\n") + "\n")

        try:
            self.clear_replace_diff_marks()
        except Exception:
            pass

        try:
            self.detected_part_var.set("Kein Ziel erkannt")
        except Exception:
            pass

        self.last_changed_part_names = set([new_name])
        self.rescan_all()
        self.update_dirty_parts()

        new_index = find_part_index_by_name(self, new_name)
        if new_index is not None:
            try:
                self.part_listbox.selection_clear(0, tk.END)
                self.part_listbox.selection_set(new_index)
                self.part_listbox.activate(new_index)
                self.on_part_select(None)
            except Exception:
                pass

        self.status_var.set("PART umbenannt: " + old_name + " -> " + new_name)
        return True

    def rename_selected_part(self):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Bitte zuerst links einen PART auswählen")
            self.status_var.set("Umbenennen abgebrochen")
            return

        sel_index = self.part_listbox.curselection()[0]
        if sel_index < 0 or sel_index >= len(self.parts):
            messagebox.showwarning("Hinweis", "Auswahl ist ungültig")
            self.status_var.set("Umbenennen abgebrochen")
            return

        selected_part = self.parts[sel_index]
        old_name = self._normalize_marker_name(selected_part.name)

        new_name = simpledialog.askstring(
            "PART umbenennen",
            "Neuen Namen für '" + old_name + "' eingeben:",
            initialvalue=old_name
        )

        if new_name is None:
            self.status_var.set("Umbenennen abgebrochen")
            return

        self._rename_selected_block_boundaries(new_name)
# ===== PART: RENAME_SELECTED_MARKER END =====


# ===== PART: RENAME_SELECTED_PART START =====
    def _build_renamed_part_boundary_line_from_existing(self, line_text, old_name, new_name):
        if line_text is None:
            return None

        old_name_raw = ""
        if old_name is not None:
            old_name_raw = str(old_name).strip()

        new_name = self._normalize_structure_name(new_name)

        if old_name_raw == "" or new_name == "":
            return line_text

        pattern = re.compile(
            r"^(\s*)(#|//)(\s*=+\s*PART:\s*)"
            + re.escape(old_name_raw)
            + r"(\s+(START|END)\s*=+\s*)$"
        )

        match = pattern.match(line_text)
        if not match:
            return line_text

        return (
            match.group(1)
            + match.group(2)
            + match.group(3)
            + new_name
            + match.group(4)
        )

    def _rename_selected_part_boundaries(self, new_name):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Bitte zuerst links einen PART auswählen")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        sel_index = self.part_listbox.curselection()[0]
        if sel_index < 0 or sel_index >= len(self.parts):
            messagebox.showwarning("Hinweis", "Auswahl ist ungültig")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        selected_part = self.parts[sel_index]

        old_name_raw = ""
        if selected_part.name is not None:
            old_name_raw = str(selected_part.name).strip()

        old_name_display = self._normalize_structure_name(selected_part.name)

        raw_new_name = new_name
        new_name = self._normalize_structure_name(new_name)

        if old_name_raw == "":
            messagebox.showwarning("Hinweis", "Der aktuelle PART-Name ist leer")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if new_name == "":
            messagebox.showwarning("Hinweis", "Der neue Name darf nicht leer sein")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if self._normalize_structure_name(old_name_raw) == new_name:
            self.status_var.set("Name unverändert")
            return False

        if self.is_structure_name_in_use(new_name, exclude_name=old_name_raw):
            suggestions = self.build_structure_name_suggestions(new_name, exclude_name=old_name_raw)

            message = (
                "Ein PART mit diesem Namen existiert bereits in der aktuellen Datei.\n\n"
                "Gewünschter Name: " + new_name + "\n\n"
                "Vorschläge:\n"
                "- " + suggestions[0] + "\n"
                "- " + suggestions[1] + "\n"
                "- " + suggestions[2] + "\n\n"
                "Bitte neuen Namen eingeben oder Abbrechen wählen."
            )

            follow_up_name = simpledialog.askstring(
                "Name existiert bereits",
                message,
                initialvalue=suggestions[0]
            )

            if follow_up_name is None:
                self.status_var.set("Umbenennen abgebrochen")
                return False

            return self._rename_selected_part_boundaries(follow_up_name)

        lines = self.text_editor.get("1.0", tk.END).splitlines()

        if selected_part.start < 0 or selected_part.start >= len(lines):
            messagebox.showwarning("Hinweis", "START-Zeile konnte nicht gefunden werden")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        if selected_part.end < 0 or selected_part.end >= len(lines):
            messagebox.showwarning("Hinweis", "END-Zeile konnte nicht gefunden werden")
            self.status_var.set("Umbenennen abgebrochen")
            return False

        old_start_line = lines[selected_part.start]
        old_end_line = lines[selected_part.end]

        new_start_line = self._build_renamed_part_boundary_line_from_existing(
            old_start_line,
            old_name_raw,
            new_name
        )
        new_end_line = self._build_renamed_part_boundary_line_from_existing(
            old_end_line,
            old_name_raw,
            new_name
        )

        if new_start_line == old_start_line and new_end_line == old_end_line:
            messagebox.showwarning(
                "Hinweis",
                "Die Marker-Zeilen konnten nicht eindeutig angepasst werden.\n\n"
                "Bitte prüfe, ob der ausgewählte Bereich wirklich ein normaler PART ist."
            )
            self.status_var.set("Umbenennen abgebrochen")
            return False

        lines[selected_part.start] = new_start_line
        lines[selected_part.end] = new_end_line

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(lines).rstrip("\n") + "\n")

        try:
            self.clear_replace_diff_marks()
        except Exception:
            pass

        try:
            self.detected_part_var.set("Kein Ziel erkannt")
        except Exception:
            pass

        self.last_changed_part_names = set([new_name])
        self.rescan_all()
        self.update_dirty_parts()

        new_index = find_part_index_by_name(self, new_name)
        if new_index is not None:
            try:
                self.part_listbox.selection_clear(0, tk.END)
                self.part_listbox.selection_set(new_index)
                self.part_listbox.activate(new_index)
                self.on_part_select(None)
            except Exception:
                pass

        if raw_new_name is not None and str(raw_new_name).strip() != new_name:
            self.status_var.set("PART umbenannt: " + old_name_display + " -> " + new_name + " (automatisch auf GROSS gesetzt)")
        else:
            self.status_var.set("PART umbenannt: " + old_name_display + " -> " + new_name)

        return True

    def rename_selected_part(self):
        if not self.part_listbox.curselection():
            messagebox.showwarning("Hinweis", "Bitte zuerst links einen PART auswählen")
            self.status_var.set("Umbenennen abgebrochen")
            return

        sel_index = self.part_listbox.curselection()[0]
        if sel_index < 0 or sel_index >= len(self.parts):
            messagebox.showwarning("Hinweis", "Auswahl ist ungültig")
            self.status_var.set("Umbenennen abgebrochen")
            return

        selected_part = self.parts[sel_index]
        old_name = ""
        if selected_part.name is not None:
            old_name = str(selected_part.name).strip()

        new_name = simpledialog.askstring(
            "PART umbenennen",
            "Neuen Namen für '" + old_name + "' eingeben:",
            initialvalue=old_name
        )

        if new_name is None:
            self.status_var.set("Umbenennen abgebrochen")
            return

        self._rename_selected_part_boundaries(new_name)
# ===== PART: RENAME_SELECTED_PART END =====

# ===== PART: CREATE_PART_FROM_SELECTION START =====
    def create_part_from_selection(self):
        blocks = self._find_unstructured_text_blocks()

        if len(blocks) == 0:
            messagebox.showwarning(
                "Hinweis",
                "Es wurden keine freien Textblöcke gefunden."
            )
            self.status_var.set("Keine freien Textblöcke gefunden")
            return

        sel_start, sel_end = self._show_unstructured_block_picker_dialog(blocks)

        if sel_start is None or sel_end is None:
            self.status_var.set("Block-Auswahl abgebrochen")
            return

        messagebox.showinfo(
            "DEBUG AUSWAHL",
            "Gewählt:\nStart = " + str(sel_start) + "\nEnde = " + str(sel_end)
        )
        self.status_var.set("Block-Auswahl erfolgreich")
# ===== PART: CREATE_PART_FROM_SELECTION END =====
