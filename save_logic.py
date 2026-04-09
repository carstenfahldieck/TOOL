
# ===== PART: IMPORTS START =====
import os
import re
from tkinter import filedialog, messagebox

from helpers import (
    remember_loaded_file_state,
    was_file_changed_externally,
    create_timestamp_backup,
    build_part_content_dict_from_editor,
    replace_part_in_text,
)
from dialogs_custom import ask_three_way
# ===== PART: IMPORTS END =====


# ===== PART: CLASS_MAIN START =====
class SaveLogicMixin:

    # ===== PART: FILE_IO_HELPERS START =====
    def remember_loaded_file_state(self, path):
        remember_loaded_file_state(self, path)

    def was_file_changed_externally(self, path):
        return was_file_changed_externally(self, path)

    def create_timestamp_backup(self, path):
        return create_timestamp_backup(self, path)

    def get_current_editor_text(self):
        return self.text_editor.get("1.0", "end").rstrip("\n")

    def mark_current_text_as_clean(self):
        self.loaded_text_snapshot = self.get_current_editor_text()

    def has_unsaved_changes(self):
        return self.get_current_editor_text() != self.loaded_text_snapshot

    def confirm_discard_unsaved_changes(self):
        if not self.has_unsaved_changes():
            return True

        answer = ask_three_way(
            self.root,
            "Ungespeicherte Änderungen",
            "Es gibt ungespeicherte Änderungen.\n\n"
            "Was soll passieren?",
            ("Speichern", "s"),
            ("Verwerfen", "v"),
            ("Abbrechen", "a")
        )

        if answer == "option3" or answer is None:
            self.status_var.set("Aktion abgebrochen")
            return False

        if answer == "option1":
            if self.current_file:
                self.save_file()
            else:
                self.save_file_as()

            if self.has_unsaved_changes():
                self.status_var.set("Speichern abgebrochen")
                return False

        return True

    def request_close(self):
        if not self.confirm_discard_unsaved_changes():
            return
        self.root.destroy()
    # ===== PART: FILE_IO_HELPERS END =====


    # ===== PART: IMPORT_SCAN_HELPERS START =====
    def extract_python_import_candidates(self, path):
        related = []

        if not path:
            return related

        if not path.lower().endswith(".py"):
            return related

        try:
            f = open(path, "r", encoding="utf-8")
            content = f.read()
            f.close()
        except Exception:
            return related

        base_dir = os.path.dirname(path)
        current_norm = self.normalize_project_path(path)

        import_re = re.compile(r"^\s*import\s+([A-Za-z_][A-Za-z0-9_\.]*)", re.MULTILINE)
        from_re = re.compile(r"^\s*from\s+([A-Za-z_][A-Za-z0-9_\.]*)\s+import\s+", re.MULTILINE)

        module_names = []

        index = 0
        imports_found = import_re.findall(content)
        while index < len(imports_found):
            module_names.append(imports_found[index])
            index += 1

        index = 0
        from_found = from_re.findall(content)
        while index < len(from_found):
            module_names.append(from_found[index])
            index += 1

        seen = set()
        index = 0
        while index < len(module_names):
            module_name = module_names[index].strip()
            index += 1

            if not module_name:
                continue
            if module_name.startswith("."):
                continue

            top_name = module_name.split(".")[0].strip()
            if not top_name:
                continue

            candidate = os.path.join(base_dir, top_name + ".py")
            if not os.path.exists(candidate):
                continue

            candidate_norm = self.normalize_project_path(candidate)
            if candidate_norm == current_norm:
                continue
            if candidate_norm in seen:
                continue

            seen.add(candidate_norm)
            related.append(candidate)

        related.sort()
        return related

    def scan_related_python_files_recursive(self, start_path):
        found = []
        queue = []
        visited = set()

        if not start_path:
            return found

        queue.append(start_path)

        while len(queue) > 0:
            current_path = queue.pop(0)
            if not current_path:
                continue

            current_norm = self.normalize_project_path(current_path)
            if current_norm in visited:
                continue

            visited.add(current_norm)

            direct_related = self.extract_python_import_candidates(current_path)

            index = 0
            while index < len(direct_related):
                related_path = direct_related[index]
                related_norm = self.normalize_project_path(related_path)

                if related_norm not in visited:
                    queue.append(related_path)

                already_in_found = False
                sub_index = 0
                while sub_index < len(found):
                    if self.normalize_project_path(found[sub_index]) == related_norm:
                        already_in_found = True
                        break
                    sub_index += 1

                if not already_in_found and related_norm != self.normalize_project_path(start_path):
                    found.append(related_path)

                index += 1

        found.sort()
        return found
    # ===== PART: IMPORT_SCAN_HELPERS END =====


    # ===== PART: RELATED_FILES_DIALOG START =====
    def ask_load_related_files(self, main_path, related_files):
        if not related_files:
            return "only_main"

        display_names = []
        index = 0
        while index < len(related_files):
            display_names.append(os.path.basename(related_files[index]))
            index += 1

        answer = ask_three_way(
            self.root,
            "Zugehörige Dateien gefunden",
            "ACHTUNG\n\n"
            "Zugehörige Dateien gefunden:\n\n- "
            + "\n- ".join(display_names),
            ("Zugehörige laden", "z"),
            ("Nur diese Datei", "n"),
            ("Abbrechen", "a")
        )

        if answer == "option1":
            return "load_related"
        if answer == "option2":
            return "only_main"
        return "cancel"

    def add_related_files_to_project(self, related_files):
        index = 0
        while index < len(related_files):
            self.add_project_file(related_files[index])
            index += 1
    # ===== PART: RELATED_FILES_DIALOG END =====


    # ===== PART: FILE_IO START =====
    def new_file(self):
        if not self.confirm_discard_unsaved_changes():
            return

        path = filedialog.asksaveasfilename(
            title="Neue Datei anlegen",
            defaultextension=".py",
            filetypes=[
                ("Python-Dateien", "*.py"),
                ("C#-Dateien", "*.cs"),
                ("Text-Dateien", "*.txt"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            self.status_var.set("Neue Datei abgebrochen")
            return

        if os.path.exists(path):
            overwrite = messagebox.askyesno(
                "Datei existiert bereits",
                "Die Datei existiert bereits:\n\n"
                + path
                + "\n\nSoll sie als leere Datei neu angelegt werden?"
            )
            if not overwrite:
                self.status_var.set("Neue Datei abgebrochen")
                return

        try:
            f = open(path, "w", encoding="utf-8")
            f.write("")
            f.close()
        except Exception as exc:
            messagebox.showerror("Fehler beim Anlegen", str(exc))
            self.status_var.set("Neue Datei fehlgeschlagen")
            return

        self.load_file_by_path(path)
        self.status_var.set("Neue Datei angelegt: " + os.path.basename(path))

    def load_file(self):
        if not self.confirm_discard_unsaved_changes():
            return

        path = filedialog.askopenfilename(
            filetypes=[("Code-Dateien", "*.py *.cs *.txt"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return

        related_files = self.scan_related_python_files_recursive(path)
        load_mode = self.ask_load_related_files(path, related_files)

        if load_mode == "cancel":
            self.status_var.set("Laden abgebrochen")
            return

        self.load_file_by_path(path)

        if load_mode == "load_related":
            self.add_related_files_to_project(related_files)
            self.status_var.set("Datei geladen + zugehörige Dateien erkannt")

    def load_file_by_path(self, path):
        try:
            f = open(path, "r", encoding="utf-8")
            content = f.read()
            f.close()
        except Exception as exc:
            messagebox.showerror("Fehler beim Laden", str(exc))
            return

        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)

        try:
            self.text_editor.edit_reset()
            self.text_editor.edit_separator()
        except Exception:
            pass

        self.current_file = path
        self.current_file_var.set(path)
        self.add_project_file(path)
        self.remember_loaded_file_state(path)
        self.update_window_title()
        self.rescan_all()
        self.remember_loaded_part_snapshot()
        self.last_changed_part_names = set()
        self.apply_editor_marks()
        self.mark_current_text_as_clean()
        self.update_action_states()
        self.status_var.set("Datei geladen")

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return

        if not self.prepare_save_target(self.current_file):
            return

        if self.write_current_editor_to_path(self.current_file):
            self.remember_loaded_file_state(self.current_file)
            self.rescan_all()
            self.remember_loaded_part_snapshot()
            self.current_file_var.set(self.current_file)
            self.add_project_file(self.current_file)
            self.update_window_title()
            self.last_changed_part_names = set()
            self.apply_editor_marks()
            self.mark_current_text_as_clean()
            self.update_action_states()
            self.status_var.set("Datei gespeichert")

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python-Dateien", "*.py"),
                ("C#-Dateien", "*.cs"),
                ("Text-Dateien", "*.txt"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            return

        if not self.prepare_save_target(path):
            return

        if self.write_current_editor_to_path(path):
            self.current_file = path
            self.current_file_var.set(path)
            self.add_project_file(path)
            self.remember_loaded_file_state(path)
            self.rescan_all()
            self.remember_loaded_part_snapshot()
            self.update_window_title()
            self.last_changed_part_names = set()
            self.apply_editor_marks()
            self.mark_current_text_as_clean()
            self.update_action_states()
            self.status_var.set("Datei gespeichert unter")

    def prepare_save_target(self, path):
        if path and self.current_file == path:
            if self.was_file_changed_externally(path):
                answer = ask_three_way(
                    self.root,
                    "Datei wurde extern geändert",
                    "Die Datei wurde außerhalb dieses Programms geändert.\n\n"
                    "Was soll passieren?",
                    ("Komplett speichern", "k"),
                    ("Nur geänderte Teile", "g"),
                    ("Abbrechen", "a")
                )

                if answer == "option3" or answer is None:
                    self.status_var.set("Speichern abgebrochen")
                    return False

                if answer == "option2":
                    return self.save_only_changed_parts(path)

        if path and self.current_file == path:
            if not self.create_timestamp_backup(path):
                return False

        return True

    def create_emergency_backup(self, path):
        if not path:
            return True

        try:
            folder = os.path.dirname(path)
            filename = os.path.basename(path)
            backup_dir = os.path.join(folder, "_tool_emergency_backup")

            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            backup_path = os.path.join(backup_dir, filename)

            current_disk_text = ""
            if os.path.exists(path):
                f = open(path, "r", encoding="utf-8")
                current_disk_text = f.read()
                f.close()

            f = open(backup_path, "w", encoding="utf-8")
            f.write(current_disk_text)
            f.close()
            return True
        except Exception as exc:
            answer = messagebox.askyesno(
                "Backup-Warnung",
                "Die automatische Rettungskopie konnte nicht erstellt werden.\n\n"
                + str(exc)
                + "\n\nTrotzdem speichern?"
            )
            return answer

    def write_current_editor_to_path(self, path):
        new_text = self.text_editor.get("1.0", "end").rstrip("\n")
        old_text = self.loaded_text_snapshot if hasattr(self, "loaded_text_snapshot") else ""

        new_len = len(new_text.strip())
        old_len = len(old_text.strip())

        if old_len > 200 and new_len < 50:
            answer = messagebox.askyesno(
                "ACHTUNG – Datei fast leer!",
                "Die Datei hatte vorher Inhalt und ist jetzt fast leer.\n\n"
                "ALT: {0} Zeichen\nNEU: {1} Zeichen\n\n"
                "Wirklich speichern?\n\n"
                "→ NEIN = Abbrechen (empfohlen)\n"
                "→ JA = Trotzdem speichern".format(old_len, new_len)
            )
            if not answer:
                self.status_var.set("Speichern abgebrochen (Leerschutz)")
                return False

        if not self.create_emergency_backup(path):
            self.status_var.set("Speichern abgebrochen (Backup)")
            return False

        try:
            f = open(path, "w", encoding="utf-8")
            f.write(new_text + "\n")
            f.close()
        except Exception as exc:
            messagebox.showerror("Fehler beim Speichern", str(exc))
            return False
        return True

    def clear_view(self, force_ignore_dirty=False):
        if (not force_ignore_dirty) and (not self.confirm_discard_unsaved_changes()):
            return

        self.text_editor.delete("1.0", "end")
        self.part_listbox.delete(0, "end")
        self.cfg_listbox.delete(0, "end")
        self.cfg_value_entry.delete("1.0", "end")
        self.replace_input.delete("1.0", "end")

        try:
            self.text_editor.edit_reset()
            self.text_editor.edit_separator()
        except Exception:
            pass

        self.parts = []
        self.config_vars = []
        self.current_file = None
        self.loaded_file_mtime = None
        self.loaded_file_size = None
        self.loaded_part_content_by_name = {}
        self.dirty_part_names = set()
        self.last_changed_part_names = set()

        self.project_files = []

        if hasattr(self, "matching_project_files"):
            self.matching_project_files = set()

        index = 0
        while hasattr(self, "project_file_buttons") and index < len(self.project_file_buttons):
            try:
                self.project_file_buttons[index].destroy()
            except Exception:
                pass
            index += 1

        self.project_file_buttons = []

        self.current_file_var.set("Keine Datei geladen")
        self.cfg_count_var.set("0 gefunden")
        self.cfg_name_var.set("")
        self.cfg_value_var.set("")
        self.cfg_line_var.set("")
        self.detected_part_var.set("Kein Ziel erkannt")

        self.clear_all_highlights()
        self.clear_replace_diff_marks()
        self.update_window_title()
        self.mark_current_text_as_clean()
        self.update_action_states()
        self.status_var.set("Ansicht komplett geleert")
    # ===== PART: FILE_IO END =====


    # ===== PART: SAVE_ALL START =====
    def save_all_changed_files(self):
        if not hasattr(self, "project_files") or len(self.project_files) == 0:
            self.status_var.set("Keine Dateien geladen")
            return

        saved_count = 0
        error_count = 0
        current_active = self.current_file

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]

            try:
                self.load_file_by_path(path)

                if self.has_unsaved_changes():
                    if self.prepare_save_target(path):
                        if self.write_current_editor_to_path(path):
                            self.remember_loaded_file_state(path)
                            saved_count += 1
                        else:
                            error_count += 1
            except Exception:
                error_count += 1

            index += 1

        if current_active:
            try:
                self.load_file_by_path(current_active)
            except Exception:
                pass

        self.update_action_states()
        self.status_var.set(
            "Alle speichern: {0} gespeichert, {1} Fehler".format(saved_count, error_count)
        )
    # ===== PART: SAVE_ALL END =====


    # ===== PART: SMART_SAVE START =====
    def remember_loaded_part_snapshot(self):
        self.loaded_part_content_by_name = build_part_content_dict_from_editor(self)
        self.dirty_part_names = set()
        self.scan_parts()

    def update_dirty_parts(self):
        current_parts = build_part_content_dict_from_editor(self)
        dirty = set()

        for part_name in current_parts:
            old_value = self.loaded_part_content_by_name.get(part_name)
            new_value = current_parts.get(part_name)
            if old_value != new_value:
                dirty.add(part_name)

        self.dirty_part_names = dirty
        self.scan_parts()
        self.update_action_states()

    def save_only_changed_parts(self, path):
        self.update_dirty_parts()

        if not self.dirty_part_names:
            messagebox.showinfo("Hinweis", "Es wurden keine geänderten PARTS gefunden.")
            self.status_var.set("Keine geänderten PARTS")
            return False

        changed_list = sorted(list(self.dirty_part_names))
        text = (
            "Folgende PARTS wurden geändert:\n\n- "
            + "\n- ".join(changed_list)
            + "\n\nNur diese PARTS in die externe Datei übernehmen?"
        )

        if not messagebox.askyesno("Nur geänderte Teile speichern", text):
            self.status_var.set("Speichern abgebrochen")
            return False

        try:
            f = open(path, "r", encoding="utf-8")
            external_text = f.read()
            f.close()
        except Exception as exc:
            messagebox.showerror("Fehler beim Laden", str(exc))
            return False

        merged_text = external_text
        current_parts = build_part_content_dict_from_editor(self)

        index = 0
        while index < len(changed_list):
            part_name = changed_list[index]
            if part_name not in current_parts:
                messagebox.showwarning("Hinweis", "PART nicht gefunden im Editor: " + part_name)
                index += 1
                continue

            merged_text = replace_part_in_text(merged_text, part_name, current_parts[part_name])
            if merged_text is None:
                messagebox.showwarning("Hinweis", "PART in externer Datei nicht gefunden: " + part_name)
                return False

            index += 1

        if not self.create_timestamp_backup(path):
            return False

        try:
            f = open(path, "w", encoding="utf-8")
            f.write(merged_text.rstrip("\n") + "\n")
            f.close()
        except Exception as exc:
            messagebox.showerror("Fehler beim Speichern", str(exc))
            return False

        self.current_file = path
        self.current_file_var.set(path)
        self.add_project_file(path)
        self.remember_loaded_file_state(path)
        self.load_file_by_path(path)
        self.status_var.set("Nur geänderte PARTS gespeichert")
        return False
    # ===== PART: SMART_SAVE END =====
# ===== PART: CLASS_MAIN END ===
