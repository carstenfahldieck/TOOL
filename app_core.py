# ===== PART: IMPORTS START =====
import os
import sys
import json
import subprocess
import ui_layout
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tool_meta import get_app_title
from ui_layout import build_main_ui
from ui_menu import create_menu_bar, bind_shortcuts
from parts_logic import PartsLogicMixin
from cfg_logic import CfgLogicMixin
from save_logic import SaveLogicMixin
from test_darkblue_check import show_block_picker_preview
# ===== PART: IMPORTS END =====


# ===== PART: CLASS_MAIN START =====
class CodeEditorApp(
    PartsLogicMixin,
    SaveLogicMixin,
    CfgLogicMixin
):

# ===== PART: TEST_BUTTON_HANDLER START =====
    def test_button_action(self):
        try:
            self.append_assistant_log("TEST: Block-Picker-Testfenster starten")
        except Exception:
            pass

        try:
            target_file = self.current_file
            if not target_file:
                target_file = "fake_target.py"

            show_block_picker_preview(self.root, target_file)
        except Exception as exc:
            try:
                messagebox.showerror("Fehler im TEST", str(exc))
            except Exception:
                pass
# ===== PART: TEST_BUTTON_HANDLER END =====

    def __init__(self, root):
        self.root = root
        self.root.title(get_app_title())
        self.root.geometry("1450x780")

        try:
            self.root.state("zoomed")
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
        self.loaded_text_snapshot = ""

        self.project_files = []
        self.project_file_buttons = []
        self.matching_project_files = set()
        self.project_main_file = None

        self.current_file_var = tk.StringVar()
        self.current_file_var.set("Keine Datei geladen")

        self.current_file_display_var = tk.StringVar()
        self.current_file_display_var.set("Keine Datei geladen")

        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")

        self.cfg_count_var = tk.StringVar()
        self.cfg_count_var.set("0 gefunden")

        self.detected_part_var = tk.StringVar()
        self.detected_part_var.set("Kein Ziel erkannt")

        self.cfg_name_var = tk.StringVar()
        self.cfg_value_var = tk.StringVar()
        self.cfg_line_var = tk.StringVar()

        self.assistant_abort_requested = False
        self.assistant_is_running = False

        self.session_file_path = os.path.join(
            os.getcwd(),
            "_carsten_tool_restart_session.json"
        )

        self.build_ui()
        self.build_menu()
        self.bind_shortcuts()
        self.root.protocol("WM_DELETE_WINDOW", self.request_close)
        self.update_action_states()

        if not self.run_startup_self_check():
            return

        self.root.after(100, self.restore_session_after_restart)

    # ===== PART: UI_SETUP START =====
    def build_ui(self):
        build_main_ui(self)

    def build_menu(self):
        create_menu_bar(self)

    def bind_shortcuts(self):
        bind_shortcuts(self)
    # ===== PART: UI_SETUP END =====

# ===== PART: STARTUP_PARAM_LOAD START =====
    def load_startup_file_with_related(self, startup_path):
        if not startup_path:
            return

        try:
            normalized_startup = os.path.abspath(startup_path)
        except Exception:
            normalized_startup = startup_path

        if not os.path.exists(normalized_startup):
            try:
                self.append_assistant_log("Startparameter-Datei nicht gefunden: " + str(normalized_startup))
            except Exception:
                pass
            try:
                self.status_var.set("Startdatei nicht gefunden")
            except Exception:
                pass
            return

        try:
            self.load_file_by_path(normalized_startup)
        except Exception as exc:
            try:
                self.append_assistant_log("Fehler beim Laden per Startparameter: " + str(exc))
            except Exception:
                pass
            try:
                self.status_var.set("Startdatei fehlgeschlagen")
            except Exception:
                pass
            return

        try:
            self.append_assistant_log("Startparameter geladen: " + str(normalized_startup))
        except Exception:
            pass

        try:
            self.status_var.set("Startdatei geladen")
        except Exception:
            pass
    # ===== PART: STARTUP_PARAM_LOAD END =====




# ===== PART: TEST_RUNNER START =====
    def run_current_file(self):
        if not self.current_file:
            messagebox.showwarning("Hinweis", "Keine Datei geladen")
            self.status_var.set("TEST abgebrochen")
            return

        if not self.current_file.lower().endswith(".py"):
            messagebox.showwarning("Hinweis", "Nur Python-Dateien können mit TEST gestartet werden")
            self.status_var.set("TEST abgebrochen")
            return

        try:
            subprocess.Popen([sys.executable, self.current_file], cwd=os.path.dirname(self.current_file))
            try:
                self.append_assistant_log("TEST gestartet: " + self.current_file)
            except Exception:
                pass
            self.status_var.set("TEST gestartet")
        except Exception as exc:
            messagebox.showerror("TEST-Fehler", str(exc))
            self.status_var.set("TEST fehlgeschlagen")
    # ===== PART: TEST_RUNNER END =====



    # ===== PART: STARTUP_SELF_CHECK START =====
    def collect_startup_self_check_errors(self):
        errors = []

        required_methods = [
            "new_file",
            "load_file",
            "save_file",
            "save_file_as",
            "save_all_changed_files",
            "clear_view",
            "request_close",
            "replace_part",
            "export_selected_part",
            "import_part_file",
            "paste_clipboard_to_replace_box",
            "clear_replace_box",
            "detect_target_part_from_replace_box",
            "apply_replace_from_box",
            "replace_from_clipboard",
            "scan_config_vars",
            "add_project_file_via_dialog",
            "close_current_project_file",
            "close_all_project_files",
            "undo_action",
            "redo_action",
            "add_new_part",
            "remove_selected_part",
            "restart_application",
            "append_assistant_log",
            "clear_assistant_log",
            "request_abort_assistant_run",
            "load_update_plugin",
            "parse_update_plugin_text",
            "validate_loaded_update_plugin_plan",
            "start_loaded_update_plugin_run",
        ]

        index = 0
        while index < len(required_methods):
            name = required_methods[index]
            obj = getattr(self, name, None)
            if obj is None or not callable(obj):
                errors.append("Methode fehlt: " + name)
            index += 1

        required_attrs = [
            "text_editor",
            "replace_input",
            "part_listbox",
            "cfg_listbox",
            "cfg_value_entry",
            "project_files_frame",
            "btn_paste_box",
            "btn_clear_box",
            "btn_detect_target",
            "btn_apply_replace",
            "btn_cfg_apply",
            "btn_cfg_rescan",
            "assistant_log_text",
            "btn_assistant_load_plugin",
            "btn_assistant_validate_plugin",
            "btn_assistant_start_plugin",
        ]

        index = 0
        while index < len(required_attrs):
            name = required_attrs[index]
            if not hasattr(self, name):
                errors.append("UI-Element fehlt: " + name)
            index += 1

        if not hasattr(self, "menu_datei"):
            errors.append("Menü fehlt: menu_datei")
        if not hasattr(self, "menu_part"):
            errors.append("Menü fehlt: menu_part")
        if not hasattr(self, "menu_bearbeiten"):
            errors.append("Menü fehlt: menu_bearbeiten")
        if not hasattr(self, "menu_extras"):
            errors.append("Menü fehlt: menu_extras")

        try:
            text = self.text_editor.get("1.0", "end")
            if text is None:
                errors.append("Texteditor liefert keinen Inhalt")
        except Exception:
            errors.append("Texteditor kann nicht gelesen werden")

        return errors

    def run_startup_self_check(self):
        errors = self.collect_startup_self_check_errors()

        if len(errors) == 0:
            self.status_var.set("Bereit")
            return True

        text = "Selbstprüfung fehlgeschlagen.\n\n"
        index = 0
        while index < len(errors):
            text += "- " + errors[index] + "\n"
            index += 1

        self.status_var.set("Selbstprüfung FEHLER")

        try:
            messagebox.showerror("Selbstprüfung", text)
        except Exception:
            pass

        try:
            self.root.after(200, self.root.destroy)
        except Exception:
            pass

        return False
    # ===== PART: STARTUP_SELF_CHECK END =====

    # ===== PART: RESCAN START =====
    def rescan_all(self):
        self.scan_parts()
        self.scan_config_vars()
        self.status_var.set(
            "Parts: {0} | CFG: {1}".format(len(self.parts), len(self.config_vars))
        )
        self.update_action_states()
    # ===== PART: RESCAN END =====

    # ===== PART: PROJECT_FILES START =====

    # ===== PART: PROJECT_FILES_PATHS START =====
    def normalize_project_path(self, path):
        return os.path.normcase(os.path.abspath(path))

    def _get_project_main_file(self):
        if not hasattr(self, "project_main_file"):
            self.project_main_file = None

        if self.project_main_file:
            main_norm = self.normalize_project_path(self.project_main_file)

            index = 0
            while index < len(self.project_files):
                if self.normalize_project_path(self.project_files[index]) == main_norm:
                    return self.project_main_file
                index += 1

        if len(self.project_files) > 0:
            self.project_main_file = self.project_files[0]
            return self.project_main_file

        self.project_main_file = None
        return None

    def _set_project_main_file_if_missing(self, path):
        if not hasattr(self, "project_main_file"):
            self.project_main_file = None

        if not self.project_main_file:
            self.project_main_file = path

    def _insert_project_file_sorted(self, path):
        new_name = os.path.basename(path).lower()

        matching = set()
        if hasattr(self, "matching_project_files"):
            matching = self.matching_project_files

        main_file = self._get_project_main_file()
        main_norm = None
        if main_file:
            main_norm = self.normalize_project_path(main_file)

        insert_index = len(self.project_files)

        index = 0
        while index < len(self.project_files):
            existing = self.project_files[index]
            existing_name = os.path.basename(existing).lower()
            existing_norm = self.normalize_project_path(existing)

            if main_norm and existing_norm == main_norm:
                index += 1
                continue

            if existing_norm in matching:
                insert_index = index
                break

            if new_name < existing_name:
                insert_index = index
                break

            index += 1

        self.project_files.insert(insert_index, path)
    # ===== PART: PROJECT_FILES_PATHS END =====


    # ===== PART: PROJECT_FILES_ADD START =====
    def add_project_file(self, path):
        if not path:
            return

        normalized = self.normalize_project_path(path)

        if not hasattr(self, "session_new_files"):
            self.session_new_files = set()

        index = 0
        while index < len(self.project_files):
            if self.normalize_project_path(self.project_files[index]) == normalized:
                self._set_project_main_file_if_missing(path)
                self.refresh_project_file_buttons()
                return
            index += 1

        self._set_project_main_file_if_missing(path)

        if len(self.project_files) == 0:
            self.project_files.append(path)
        else:
            self._insert_project_file_sorted(path)

        self.refresh_project_file_buttons()

    def add_project_file_via_dialog(self):
        path = tk.filedialog.askopenfilename(
            filetypes=[("Code-Dateien", "*.py *.cs *.txt"), ("Alle Dateien", "*.*")]
        )
        if not path:
            return

        self.add_project_file(path)
        self.status_var.set("Datei zur Leiste hinzugefügt: " + os.path.basename(path))
        self.update_action_states()
    # ===== PART: PROJECT_FILES_ADD END =====


    # ===== PART: PROJECT_FILES_MATCHING START =====
    def highlight_matching_project_files(self, matching_paths):
        self.matching_project_files = set()

        index = 0
        while index < len(matching_paths):
            self.matching_project_files.add(
                self.normalize_project_path(matching_paths[index])
            )
            index += 1

        self.refresh_project_file_buttons()

    def clear_matching_project_files(self):
        self.matching_project_files = set()
        self.refresh_project_file_buttons()
    # ===== PART: PROJECT_FILES_MATCHING END =====


    # ===== PART: PROJECT_FILES_SWITCH START =====
    def switch_to_project_file(self, path):
        if not path:
            return

        normalized_target = self.normalize_project_path(path)
        normalized_current = None

        if self.current_file:
            normalized_current = self.normalize_project_path(self.current_file)

        if normalized_current == normalized_target:
            if hasattr(self, "matching_project_files") and len(self.matching_project_files) > 0:
                self.clear_matching_project_files()

            pending_part_name = getattr(self, "pending_target_part_name", None)
            if pending_part_name:
                self.select_part_by_name(pending_part_name)
                self.pending_target_part_name = None

            self.status_var.set("Datei ist bereits aktiv: " + os.path.basename(path))
            return

        if not self.confirm_discard_unsaved_changes():
            return

        self.load_file_by_path(path)

        if hasattr(self, "matching_project_files") and len(self.matching_project_files) > 0:
            self.clear_matching_project_files()

        pending_part_name = getattr(self, "pending_target_part_name", None)
        if pending_part_name:
            if self.select_part_by_name(pending_part_name):
                self.status_var.set(
                    "Datei gewechselt und PART gewählt: " + pending_part_name
                )
            else:
                self.status_var.set(
                    "Datei gewechselt, PART nicht gefunden: " + pending_part_name
                )
            self.pending_target_part_name = None
    # ===== PART: PROJECT_FILES_SWITCH END =====


    # ===== PART: PROJECT_FILES_CLOSE START =====
    def close_current_project_file(self):
        if not self.current_file:
            self.status_var.set("Keine aktive Datei zum Schließen")
            return

        if not self.confirm_discard_unsaved_changes():
            return

        current_normalized = self.normalize_project_path(self.current_file)

        remaining_files = []
        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]
            if self.normalize_project_path(path) != current_normalized:
                remaining_files.append(path)
            index += 1

        was_main = False
        main_file = self._get_project_main_file()
        if main_file and self.normalize_project_path(main_file) == current_normalized:
            was_main = True

        self.project_files = remaining_files

        if was_main:
            if len(self.project_files) > 0:
                self.project_main_file = self.project_files[0]
            else:
                self.project_main_file = None

        next_file = None
        if len(self.project_files) > 0:
            next_file = self.project_files[0]

        if next_file is not None:
            self.load_file_by_path(next_file)
            self.status_var.set("Datei geschlossen, nächste Datei geladen")
        else:
            self.clear_view(force_ignore_dirty=True)
            self.status_var.set("Datei geschlossen")

        self.refresh_project_file_buttons()
        self.update_action_states()

    def close_all_project_files(self):
        if len(self.project_files) == 0 and not self.current_file:
            self.status_var.set("Keine Dateien zum Schließen")
            return

        if not self.confirm_discard_unsaved_changes():
            return

        self.project_files = []
        self.matching_project_files = set()
        self.pending_target_part_name = None
        self.project_main_file = None

        index = 0
        while index < len(self.project_file_buttons):
            try:
                self.project_file_buttons[index].destroy()
            except Exception:
                pass
            index += 1
        self.project_file_buttons = []

        self.clear_view(force_ignore_dirty=True)
        self.refresh_project_file_buttons()
        self.update_action_states()
        self.status_var.set("Alle Dateien geschlossen")
    # ===== PART: PROJECT_FILES_CLOSE END =====


    # ===== PART: PROJECT_FILES_UI START =====
    def refresh_project_file_buttons(self):
        index = 0
        while index < len(self.project_file_buttons):
            try:
                self.project_file_buttons[index].destroy()
            except Exception:
                pass
            index += 1
        self.project_file_buttons = []

        current_normalized = None
        if self.current_file:
            current_normalized = self.normalize_project_path(self.current_file)

        matching_set = set()
        if hasattr(self, "matching_project_files"):
            matching_set = self.matching_project_files

        session_new_set = set()
        if hasattr(self, "session_new_files"):
            session_new_set = self.session_new_files

        main_file = self._get_project_main_file()
        main_norm = None
        if main_file:
            main_norm = self.normalize_project_path(main_file)

        display_list = []
        normal_list = []
        matching_list = []

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]
            norm = self.normalize_project_path(path)

            if main_norm and norm == main_norm:
                index += 1
                continue

            if norm in matching_set:
                matching_list.append(path)
            else:
                normal_list.append(path)

            index += 1

        normal_list.sort(key=lambda x: os.path.basename(x).lower())
        matching_list.sort(key=lambda x: os.path.basename(x).lower())

        if main_file:
            display_list.append(main_file)

        index = 0
        while index < len(normal_list):
            display_list.append(normal_list[index])
            index += 1

        index = 0
        while index < len(matching_list):
            display_list.append(matching_list[index])
            index += 1

        index = 0
        while index < len(display_list):
            path = display_list[index]
            short_name = os.path.basename(path)
            normalized = self.normalize_project_path(path)

            if main_norm and normalized == main_norm:
                caption = short_name.upper()
            else:
                caption = short_name

            if current_normalized == normalized and self.has_unsaved_changes():
                caption += " *"

            relief_value = tk.RAISED
            background_value = "#d4f7d4"
            fg_value = "black"

            # Priorität:
            # 1) aktiv + neu = dunkelblau
            # 2) aktiv = gelb
            # 3) Treffer = rot
            # 4) neu = hellblau
            # 5) normal = grün
            if current_normalized == normalized and normalized in session_new_set:
                relief_value = tk.SUNKEN
                background_value = "#0050a0"
                fg_value = "white"
            elif current_normalized == normalized:
                relief_value = tk.SUNKEN
                background_value = "#fff2a8"
                fg_value = "black"
            elif normalized in matching_set:
                background_value = "#f7caca"
                fg_value = "black"
            elif normalized in session_new_set:
                background_value = "#cce8ff"
                fg_value = "black"

            button = tk.Button(
                self.project_files_frame,
                text=caption,
                relief=relief_value,
                bg=background_value,
                fg=fg_value,
                activebackground=background_value,
                activeforeground=fg_value,
                command=lambda p=path: self.switch_to_project_file(p)
            )
            button.pack(side=tk.LEFT, padx=(0, 4))

            self.project_file_buttons.append(button)
            index += 1
    # ===== PART: PROJECT_FILES_UI END =====
    # ===== PART: PROJECT_FILES END =====


# ===== PART: PROJECT_FILES_IO START =====
    def _get_parts_export_dir(self):
        return os.path.join(os.getcwd(), "_parts_export")

    def export_selected_part(self):
        return PartsLogicMixin.export_selected_part(self)
    # ===== PART: PROJECT_FILES_IO END =====

# ===== PART: ASSISTANT_LOGIC START =====

    # ===== PART: ASSISTANT_LOG START =====
    def append_assistant_log(self, text):
        if not hasattr(self, "assistant_log_text"):
            return

        try:
            timestamp = ""
            try:
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S") + " | "
            except Exception:
                pass

            self.assistant_log_text.insert("end", timestamp + text + "\n")
            self.assistant_log_text.see("end")

            # --- FILE LOG ---
            try:
                import os
                log_path = os.path.join(os.getcwd(), "assistant_log.txt")
                f = open(log_path, "a", encoding="utf-8")
                f.write(timestamp + text + "\n")
                f.close()
            except Exception:
                pass

        except Exception:
            pass

    def clear_assistant_log(self):
        if not hasattr(self, "assistant_log_text"):
            return

        try:
            self.assistant_log_text.delete("1.0", "end")
        except Exception:
            pass

        self.append_assistant_log("Ablaufprotokoll geleert")
    # ===== PART: ASSISTANT_LOG END =====


    # ===== PART: ASSISTANT_RUN_CONTROL START =====
    def request_abort_assistant_run(self):
        self.assistant_abort_requested = True
        self.append_assistant_log("Abbruch angefordert (ESC)")
        self.status_var.set("Assistent: Abbruch angefordert")

    def start_assistant_run(self, title_text):
        self.assistant_abort_requested = False
        self.assistant_is_running = True
        self.append_assistant_log("Start: " + title_text)
        self.status_var.set("Assistent läuft")

    def finish_assistant_run(self, title_text):
        self.assistant_is_running = False
        self.append_assistant_log("Fertig: " + title_text)
        self.status_var.set("Assistent fertig")

    def abort_assistant_run_if_requested(self):
        if self.assistant_abort_requested:
            self.assistant_is_running = False
            self.append_assistant_log("Vom Benutzer abgebrochen")
            self.status_var.set("Assistent abgebrochen")
            return True
        return False

    def assistant_step(self, text, delay_ms=400):
        if self.abort_assistant_run_if_requested():
            return False

        self.append_assistant_log(text)

        try:
            self.root.update()
        except Exception:
            pass

        try:
            wait_var = tk.BooleanVar(value=False)
            self.root.after(delay_ms, lambda: wait_var.set(True))
            self.root.wait_variable(wait_var)
        except Exception:
            pass

        if self.abort_assistant_run_if_requested():
            return False

        return True
    # ===== PART: ASSISTANT_RUN_CONTROL END =====


    # ===== PART: ASSISTANT_PLUGIN_IO START =====
    def _disable_preview_if_active(self):
        try:
            if hasattr(self, "preview_replace_var"):
                if self.preview_replace_var.get():
                    self.preview_replace_var.set(False)
                    self.append_assistant_log("Vorschau automatisch deaktiviert")
        except Exception:
            pass

        try:
            if hasattr(self, "preview_active") and self.preview_active:
                self.preview_active = False
        except Exception:
            pass

    def _move_used_plugin_file(self):
        if not getattr(self, "loaded_update_plugin_path", None):
            return

        try:
            base_dir = os.path.dirname(self.loaded_update_plugin_path)
            target_dir = os.path.join(base_dir, "_used_plugins")

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            file_name = os.path.basename(self.loaded_update_plugin_path)
            target_path = os.path.join(target_dir, file_name)

            if os.path.exists(target_path):
                import time
                name, ext = os.path.splitext(file_name)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                target_path = os.path.join(target_dir, name + "_" + timestamp + ext)

            import shutil
            shutil.move(self.loaded_update_plugin_path, target_path)

            self.append_assistant_log("Plugin verschoben nach: " + target_path)

        except Exception as exc:
            self.append_assistant_log("WARNUNG: Plugin konnte nicht verschoben werden: " + str(exc))

    def _clear_loaded_update_plugin(self):
        self.loaded_update_plugin_path = None
        self.loaded_update_plugin_text = ""
        self.loaded_update_plugin_data = None
        self.loaded_update_plugin_validation = None

    def load_update_plugin(self):
        self._disable_preview_if_active()

        start_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(start_dir):
            start_dir = os.getcwd()

        plugin_path = tk.filedialog.askopenfilename(
            title="Update-Plugin laden",
            initialdir=start_dir,
            filetypes=[
                ("Dev Updates", "*.devupdate"),
                ("Plugin-Dateien", "*.txt *.patch *.plugin *.py"),
                ("Alle Dateien", "*.*"),
            ],
        )

        if not plugin_path:
            self.append_assistant_log("Plugin-Laden abgebrochen")
            return

        self._clear_loaded_update_plugin()
        self.start_assistant_run("Plugin laden")

        if not self.assistant_step("Plugin-Datei gewählt: " + os.path.basename(plugin_path)):
            return

        try:
            f = open(plugin_path, "r", encoding="utf-8")
            plugin_text = f.read()
            f.close()
        except Exception as exc:
            self.append_assistant_log("Fehler beim Lesen: " + str(exc))
            self.status_var.set("Plugin konnte nicht gelesen werden")
            self.assistant_is_running = False
            return

        self.loaded_update_plugin_path = plugin_path
        self.loaded_update_plugin_text = plugin_text
        self.loaded_update_plugin_data = self.parse_update_plugin_text(plugin_text)
        self.loaded_update_plugin_validation = None

        if not self.assistant_step("Plugin-Datei wurde gelesen"):
            return

        validation = self.validate_loaded_update_plugin_plan()

        if not validation.get("ok", False):
            self.append_assistant_log("Plugin-Prüfung fehlgeschlagen")
            self.append_assistant_log("Installation nicht möglich – Update wurde nicht gestartet")
            self.finish_assistant_run("Plugin geladen")
            self._show_update_validation_error_dialog(validation)
            return

        self.append_assistant_log("Plugin-Prüfung erfolgreich – warte auf Entscheidung")

        do_update = self._show_update_ready_dialog(self.loaded_update_plugin_data)

        if do_update:
            self.append_assistant_log("Benutzer hat 'Update durchführen' gewählt")
            self.finish_assistant_run("Plugin geladen")
            self.start_loaded_update_plugin_run()
        else:
            self.append_assistant_log("Update vom Benutzer abgebrochen")
            self.finish_assistant_run("Plugin geladen")
            self.status_var.set("Update abgebrochen")
    # ===== PART: ASSISTANT_PLUGIN_IO END =====


    # ===== PART: ASSISTANT_TESTS START =====
    def run_test_assistant_flow(self):
        self.start_assistant_run("Test-Ablauf")

        if not self.assistant_step("Plugin wird geladen..."):
            return

        if not self.assistant_step("Datei erkannt: example.py"):
            return

        if not self.assistant_step("Datei wird geöffnet..."):
            return

        if not self.assistant_step("Text wird in Ersetzen-Helfer eingefügt..."):
            return

        if not self.assistant_step("Ziel wird erkannt..."):
            return

        preview_old = False
        try:
            preview_old = self.preview_replace_var.get()
            self.preview_replace_var.set(False)
        except Exception:
            pass

        if not self.assistant_step("Ersetzen wird durchgeführt..."):
            try:
                self.preview_replace_var.set(preview_old)
            except Exception:
                pass
            return

        try:
            self.apply_replace_from_box()
        except Exception:
            pass

        if not self.assistant_step("Datei wird gespeichert..."):
            try:
                self.preview_replace_var.set(preview_old)
            except Exception:
                pass
            return

        try:
            self.save_file()
        except Exception:
            pass

        try:
            self.preview_replace_var.set(preview_old)
        except Exception:
            pass

        if not self.assistant_step("Ablauf abgeschlossen"):
            return

        self.finish_assistant_run("Test-Ablauf fertig")
    # ===== PART: ASSISTANT_TESTS END =====


    # ===== PART: ASSISTANT_VERSIONING START =====
    def _normalize_version_text(self, version_text):
        if version_text is None:
            return ""

        text = str(version_text).strip()
        if text == "":
            return ""

        parts = text.split(".")
        clean_parts = []

        index = 0
        while index < len(parts):
            part = parts[index].strip()
            if part == "":
                clean_parts.append("0")
            else:
                clean_parts.append(part)
            index += 1

        while len(clean_parts) < 4:
            clean_parts.append("0")

        if len(clean_parts) > 4:
            clean_parts = clean_parts[:4]

        return ".".join(clean_parts)

    def _version_tuple(self, version_text):
        normalized = self._normalize_version_text(version_text)
        if normalized == "":
            return None

        parts = normalized.split(".")
        values = []

        index = 0
        while index < len(parts):
            try:
                values.append(int(parts[index]))
            except Exception:
                return None
            index += 1

        return tuple(values)
    # ===== PART: ASSISTANT_VERSIONING END =====


    # ===== PART: ASSISTANT_DIALOGS START =====
    def _show_warning_dialog(self, title, warning_lines):
        if not warning_lines:
            return

        try:
            messagebox.showwarning(title, "\n".join(warning_lines))
        except Exception:
            pass

    def _show_restart_required_dialog(self):
        try:
            messagebox.showinfo(
                "Neustart erforderlich",
                "Dieses Update verlangt einen Neustart.\n\n"
                "Bitte speichere deine Arbeiten und starte das Tool neu."
            )
        except Exception:
            pass

    def _show_update_validation_error_dialog(self, validation):
        errors = []
        if validation and "errors" in validation:
            errors = validation["errors"]

        text = "Update kann nicht ausgeführt werden.\n\n"

        index = 0
        while index < len(errors):
            text += "- " + errors[index] + "\n"
            index += 1

        try:
            messagebox.showerror("Update-Fehler", text)
        except Exception:
            pass

    def _show_update_ready_dialog(self, data):
        title = data.get("info_title", "").strip()
        description = data.get("info_description", "").strip()

        action_name = data.get("action", "").strip().upper()
        file_name = data.get("file", "").strip()
        part_name = data.get("part", "").strip()

        text = ""

        if title:
            text += title + "\n\n"
        else:
            text += "Update bereit\n\n"

        if description:
            text += description.strip() + "\n\n"
        else:
            if action_name:
                text += "Aktion: " + action_name + "\n"
            if file_name:
                text += "Datei: " + file_name + "\n"
            if part_name:
                text += "PART: " + part_name + "\n"
            text += "\n"

        text += "Update durchführen?"

        try:
            return messagebox.askyesno("Update bereit", text)
        except Exception:
            return False
    # ===== PART: ASSISTANT_DIALOGS END =====


    # ===== PART: ASSISTANT_PLUGIN_PARSE START =====
    def parse_update_plugin_text(self, text):
        result = {
            "tool": "",
            "target_version": "",
            "update_version": "",
            "restart": "",
            "file": "",
            "part": "",
            "action": "REPLACE_PART",
            "position": "",
            "target_part": "",
            "content": "",
            "raw_text": text,
            "info_title": "",
            "info_description": "",
            "info_author": "",
        }

        lines = text.splitlines()
        body_start = len(lines)

        index = 0
        while index < len(lines):
            line = lines[index].strip()

            if line == "":
                index += 1
                continue

            upper_line = line.upper()

            if upper_line.startswith("TOOL:"):
                result["tool"] = line[5:].strip()
            elif upper_line.startswith("TARGET_VERSION:"):
                result["target_version"] = line[len("TARGET_VERSION:"):].strip()
            elif upper_line.startswith("UPDATE_VERSION:"):
                result["update_version"] = line[len("UPDATE_VERSION:"):].strip()
            elif upper_line.startswith("RESTART:"):
                result["restart"] = line[len("RESTART:"):].strip()
            elif upper_line.startswith("FILE:"):
                result["file"] = line[5:].strip()
                body_start = index + 1
                break
            elif upper_line.startswith("PART:"):
                result["part"] = line[5:].strip()
            elif upper_line.startswith("ACTION:"):
                result["action"] = line[7:].strip()
            elif upper_line.startswith("POSITION:"):
                result["position"] = line[len("POSITION:"):].strip()
            elif upper_line.startswith("TARGET_PART:"):
                result["target_part"] = line[len("TARGET_PART:"):].strip()

            index += 1

        index = body_start
        while index < len(lines):
            line = lines[index].strip()
            upper_line = line.upper()

            if line == "":
                body_start = index + 1
                break

            if upper_line.startswith("PART:"):
                result["part"] = line[5:].strip()
            elif upper_line.startswith("ACTION:"):
                result["action"] = line[7:].strip()
            elif upper_line.startswith("FILE:") and not result["file"]:
                result["file"] = line[5:].strip()
            elif upper_line.startswith("POSITION:"):
                result["position"] = line[len("POSITION:"):].strip()
            elif upper_line.startswith("TARGET_PART:"):
                result["target_part"] = line[len("TARGET_PART:"):].strip()

            index += 1

        body_lines = lines[body_start:]

        info_index = -1
        index = 0
        while index < len(body_lines):
            if body_lines[index].strip() == "---INFO---":
                info_index = index
                break
            index += 1

        content_lines = body_lines
        info_lines = []

        if info_index >= 0:
            content_lines = body_lines[:info_index]
            info_lines = body_lines[info_index + 1:]

        result["content"] = "\n".join(content_lines).strip()

        description_lines = []
        reading_description = False

        index = 0
        while index < len(info_lines):
            raw_line = info_lines[index]
            line = raw_line.strip()
            upper_line = line.upper()

            if upper_line.startswith("TITLE:"):
                result["info_title"] = line[len("TITLE:"):].strip()
                reading_description = False
            elif upper_line.startswith("AUTHOR:"):
                result["info_author"] = line[len("AUTHOR:"):].strip()
                reading_description = False
            elif upper_line.startswith("DESCRIPTION:"):
                reading_description = True
                first_text = line[len("DESCRIPTION:"):].strip()
                if first_text:
                    description_lines.append(first_text)
            else:
                if reading_description:
                    description_lines.append(raw_line.rstrip())

            index += 1

        result["info_description"] = "\n".join(description_lines).strip()

        return result
    # ===== PART: ASSISTANT_PLUGIN_PARSE END =====


    # ===== PART: ASSISTANT_PLUGIN_TARGETS START =====
    def _find_project_file_by_name(self, file_name):
        if not file_name:
            return None

        target_name = os.path.basename(file_name).lower()

        if self.current_file:
            if os.path.basename(self.current_file).lower() == target_name:
                return self.current_file

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]
            if os.path.basename(path).lower() == target_name:
                return path
            index += 1

        return None
    # ===== PART: ASSISTANT_PLUGIN_TARGETS END =====



# ===== PART: EXTRACT_PART_HELPER START =====
    def extract_part_name_and_inner_text(self, full_text):
        if not full_text:
            return None, None

        lines = full_text.splitlines()
        start_index = None
        end_index = None
        part_name = None

        index = 0
        while index < len(lines):
            stripped = lines[index].strip()

            if stripped.startswith("# ===== PART: ") and stripped.endswith(" START ====="):
                start_index = index
                middle = stripped[len("# ===== PART: "):]
                middle = middle[:-len(" START =====")]
                part_name = middle.strip()
                index += 1
                continue

            if stripped.startswith("# ===== PART: ") and stripped.endswith(" END ====="):
                end_index = index
                break

            index += 1

        if start_index is None or end_index is None or part_name is None:
            return None, None

        inner_lines = lines[start_index + 1:end_index]
        inner_text = "\n".join(inner_lines)
        return part_name, inner_text
    # ===== PART: EXTRACT_PART_HELPER END =====

    # ===== PART: ASSISTANT_PLUGIN_VALIDATE START =====
    def validate_loaded_update_plugin_plan(self):
        validation = {
            "ok": False,
            "errors": [],
            "warnings": [],
            "resolved_target_path": None,
            "resolved_target_part": None,
        }

        self.loaded_update_plugin_validation = validation

        if not getattr(self, "loaded_update_plugin_data", None):
            validation["errors"].append("Es wurde noch kein Plugin geladen.")
            self.append_assistant_log("Prüfung fehlgeschlagen: Kein Plugin geladen")
            self.status_var.set("Plugin-Prüfung FEHLER")
            return validation

        data = self.loaded_update_plugin_data

        file_name = data.get("file", "").strip()
        part_name = data.get("part", "").strip()
        action_name = data.get("action", "REPLACE_PART").strip().upper()
        position_name = data.get("position", "").strip().upper()
        target_part_name = data.get("target_part", "").strip()
        content = data.get("content", "").strip()

        def _resolve_existing_file_for_update(name):
            if not name:
                return None

            loaded_path = self._find_project_file_by_name(name)
            if loaded_path and os.path.exists(loaded_path):
                return loaded_path

            candidate_paths = []

            if os.path.isabs(name):
                candidate_paths.append(name)
            else:
                candidate_paths.append(os.path.abspath(os.path.join(os.getcwd(), name)))

                if self.current_file:
                    try:
                        base_dir = os.path.dirname(self.current_file)
                        candidate_paths.append(os.path.abspath(os.path.join(base_dir, name)))
                    except Exception:
                        pass

                main_file = self._get_project_main_file()
                if main_file:
                    try:
                        main_dir = os.path.dirname(main_file)
                        candidate_paths.append(os.path.abspath(os.path.join(main_dir, name)))
                    except Exception:
                        pass

            seen = set()
            index = 0
            while index < len(candidate_paths):
                path = candidate_paths[index]
                norm = self.normalize_project_path(path)

                if norm in seen:
                    index += 1
                    continue
                seen.add(norm)

                if os.path.exists(path):
                    return path

                index += 1

            return None

        if not file_name:
            validation["errors"].append("FILE fehlt")

        if action_name not in ["REPLACE_PART", "ADD_PART", "REMOVE_PART", "CREATE_FILE"]:
            validation["errors"].append("Aktion unbekannt: " + action_name)

        if action_name in ["REPLACE_PART", "ADD_PART", "REMOVE_PART"] and not part_name:
            validation["errors"].append("PART fehlt")

        if action_name in ["REPLACE_PART", "ADD_PART", "CREATE_FILE"] and not content:
            validation["errors"].append("CONTENT fehlt")

        if action_name == "ADD_PART":
            if position_name not in ["TOP", "BOTTOM", "BEFORE", "AFTER"]:
                validation["errors"].append("POSITION ungültig: " + position_name)

            if position_name in ["BEFORE", "AFTER"] and not target_part_name:
                validation["errors"].append("TARGET_PART fehlt")

        if action_name == "CREATE_FILE":
            if file_name:
                target_path = file_name
                if not os.path.isabs(target_path):
                    target_path = os.path.join(os.getcwd(), target_path)
                target_path = os.path.abspath(target_path)

                if os.path.exists(target_path):
                    validation["errors"].append("Datei existiert bereits: " + os.path.basename(target_path))
                else:
                    validation["resolved_target_path"] = target_path
        else:
            target_path = _resolve_existing_file_for_update(file_name)
            if not target_path:
                validation["errors"].append("Datei nicht gefunden: " + file_name)
            else:
                validation["resolved_target_path"] = target_path

                try:
                    with open(target_path, "r", encoding="utf-8") as f:
                        target_text = f.read()
                except Exception as exc:
                    validation["errors"].append("Datei konnte nicht gelesen werden: " + str(exc))
                    target_text = ""

                marker_start = "PART: " + part_name + " START"
                marker_end = "PART: " + part_name + " END"

                if action_name == "REPLACE_PART":
                    if marker_start not in target_text or marker_end not in target_text:
                        validation["errors"].append("PART existiert nicht für REPLACE")
                    else:
                        validation["resolved_target_part"] = part_name

                elif action_name == "ADD_PART":
                    if marker_start in target_text or marker_end in target_text:
                        validation["errors"].append("PART existiert bereits")

                    if position_name in ["BEFORE", "AFTER"] and target_part_name:
                        target_start = "PART: " + target_part_name + " START"
                        target_end = "PART: " + target_part_name + " END"

                        if target_start not in target_text or target_end not in target_text:
                            validation["errors"].append("TARGET_PART existiert nicht")
                        else:
                            validation["resolved_target_part"] = target_part_name

                elif action_name == "REMOVE_PART":
                    if marker_start not in target_text or marker_end not in target_text:
                        validation["errors"].append("PART existiert nicht für REMOVE")
                    else:
                        validation["resolved_target_part"] = part_name

        validation["ok"] = len(validation["errors"]) == 0

        if validation["ok"]:
            self.append_assistant_log("Plugin-Prüfung erfolgreich")
            self.status_var.set("Plugin-Prüfung OK")
        else:
            index = 0
            while index < len(validation["errors"]):
                self.append_assistant_log("FEHLER: " + validation["errors"][index])
                index += 1
            self.status_var.set("Plugin-Prüfung FEHLER")

        return validation
    # ===== PART: ASSISTANT_PLUGIN_VALIDATE END =====


        # ===== PART: ASSISTANT_PLUGIN_EXECUTE START =====
    def start_loaded_update_plugin_run(self):
        try:
            if hasattr(self, "_create_full_project_backup_v2"):
                self.append_assistant_log("DEV Backup V2 wird erstellt...")
                self._create_full_project_backup_v2()
                self.append_assistant_log("DEV Backup V2 abgeschlossen")
            else:
                self.append_assistant_log("WARNUNG: Backup-Funktion fehlt (_create_full_project_backup_v2)")
        except Exception as exc:
            self.append_assistant_log("FEHLER DEV BACKUP V2: " + str(exc))

        self.start_assistant_run("Update starten")

        if not self.assistant_step("Sicherheitsprüfung wird vorbereitet..."):
            return

        validation = self.validate_loaded_update_plugin_plan()

        if not validation.get("ok", False):
            self.append_assistant_log("STOP: Update abgebrochen")
            self.append_assistant_log("Grund: Validierung fehlgeschlagen")
            self.status_var.set("Update abgebrochen")
            self.assistant_is_running = False
            return

        data = self.loaded_update_plugin_data
        action = data.get("action", "").upper()
        plugin_content = data.get("content", "")
        position = data.get("position", "").upper()
        target_part = data.get("target_part", "")
        restart_value = data.get("restart", "").strip().upper()
        part_name = data.get("part", "")

        if restart_value:
            self.append_assistant_log("Neustart erforderlich: " + restart_value)

        if not self.assistant_step("Sicherheitsprüfung erfolgreich"):
            return

        target_path = validation.get("resolved_target_path")
        success = False

        if target_path is None:
            self.append_assistant_log("STOP: Zieldatei fehlt")
            self.status_var.set("Update fehlgeschlagen")
            self.assistant_is_running = False
            return

        def _same_path(a, b):
            try:
                return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))
            except Exception:
                return a == b

        def _is_project_file_loaded(path):
            try:
                index = 0
                while index < len(self.project_files):
                    if _same_path(self.project_files[index], path):
                        return True
                    index += 1
            except Exception:
                pass
            return False

        def _load_target_into_editor(path):
            try:
                if self.current_file and _same_path(self.current_file, path):
                    self.append_assistant_log("Hinweis: Zieldatei ist bereits aktiv")
                    return True

                if _is_project_file_loaded(path):
                    if not self.confirm_discard_unsaved_changes():
                        self.append_assistant_log("STOP: Dateiwechsel abgebrochen")
                        self.status_var.set("Update abgebrochen")
                        return False

                    self.append_assistant_log(
                        "Hinweis: Bereits geladene Datei wird für Update aktiviert: "
                        + os.path.basename(path)
                    )
                    self.load_file_by_path(path)
                    return self.current_file is not None and _same_path(self.current_file, path)

                try:
                    answer = messagebox.askyesno(
                        "Datei öffnen für Update",
                        "Die Datei '" + os.path.basename(path) + "' ist noch nicht geladen.\n\n"
                        "Soll sie für das Update geöffnet werden?"
                    )
                except Exception:
                    answer = True

                if not answer:
                    self.append_assistant_log("STOP: Laden vom Nutzer abgelehnt")
                    self.status_var.set("Update abgebrochen")
                    return False

                if not self.confirm_discard_unsaved_changes():
                    self.append_assistant_log("STOP: Dateiwechsel abgebrochen")
                    self.status_var.set("Update abgebrochen")
                    return False

                self.append_assistant_log(
                    "Hinweis: Datei war noch nicht geladen und wird für Update geöffnet: "
                    + os.path.basename(path)
                )
                self.load_file_by_path(path)
                return self.current_file is not None and _same_path(self.current_file, path)

            except Exception as exc:
                self.append_assistant_log("FEHLER beim Laden der Zieldatei: " + str(exc))
                self.status_var.set("Update fehlgeschlagen")
                return False

        def _set_editor_text_only(new_lines):
            new_text = "\n".join(new_lines).rstrip("\n") + "\n"

            self.text_editor.delete("1.0", "end")
            self.text_editor.insert("1.0", new_text)

            try:
                self.text_editor.edit_reset()
                self.text_editor.edit_separator()
            except Exception:
                pass

            try:
                self.clear_replace_diff_marks()
            except Exception:
                pass

            try:
                self.detected_part_var.set("Kein Ziel erkannt")
            except Exception:
                pass

            self.rescan_all()
            self.update_dirty_parts()
            self.update_action_states()

        def _select_part_if_present(name):
            if not name:
                return False

            index = 0
            while index < len(self.parts):
                if self.parts[index].name == name:
                    try:
                        self.part_listbox.selection_clear(0, tk.END)
                        self.part_listbox.selection_set(index)
                        self.part_listbox.activate(index)
                        self.on_part_select(None)
                    except Exception:
                        pass
                    return True
                index += 1

            return False

        def _select_nearest_part_by_line(line_index):
            if len(self.parts) == 0:
                try:
                    self.clear_all_highlights()
                except Exception:
                    pass
                return

            best_index = 0
            best_distance = None

            index = 0
            while index < len(self.parts):
                part = self.parts[index]

                if line_index < part.start:
                    distance = part.start - line_index
                elif line_index > part.end:
                    distance = line_index - part.end
                else:
                    distance = 0

                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_index = index

                index += 1

            try:
                self.part_listbox.selection_clear(0, tk.END)
                self.part_listbox.selection_set(best_index)
                self.part_listbox.activate(best_index)
                self.on_part_select(None)
            except Exception:
                pass

        if action == "CREATE_FILE":
            try:
                path = data.get("file", "")
                if not path:
                    self.append_assistant_log("FEHLER CREATE_FILE: FILE fehlt")
                    self.status_var.set("Update fehlgeschlagen")
                    self.assistant_is_running = False
                    return

                if not hasattr(self, "session_new_files"):
                    self.session_new_files = set()

                create_path = target_path
                create_dir = os.path.dirname(create_path)
                if create_dir and not os.path.exists(create_dir):
                    os.makedirs(create_dir)

                if not os.path.exists(create_path):
                    f = open(create_path, "w", encoding="utf-8")
                    f.write("")
                    f.close()

                try:
                    self.add_project_file(create_path)
                except Exception:
                    pass

                if not _load_target_into_editor(create_path):
                    self.assistant_is_running = False
                    return

                normalized_create = self.normalize_project_path(create_path)
                self.session_new_files.add(normalized_create)

                content_text = plugin_content
                if content_text is None:
                    content_text = ""

                if content_text != "" and not content_text.endswith("\n"):
                    content_text += "\n"

                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content_text)

                try:
                    self.text_editor.edit_reset()
                    self.text_editor.edit_separator()
                except Exception:
                    pass

                try:
                    self.clear_replace_diff_marks()
                except Exception:
                    pass

                try:
                    self.detected_part_var.set("Kein Ziel erkannt")
                except Exception:
                    pass

                self.last_changed_part_names = set()
                self.rescan_all()
                self.update_dirty_parts()
                self.refresh_project_file_buttons()
                self.update_action_states()

                self.append_assistant_log("CREATE_FILE im Monitor vorbereitet")
                self.status_var.set("Neue Datei im Monitor vorbereitet – bitte prüfen und selbst speichern")
                success = True

            except Exception as exc:
                self.append_assistant_log("FEHLER CREATE_FILE: " + str(exc))

        elif action == "ADD_PART":
            try:
                if not _load_target_into_editor(target_path):
                    self.assistant_is_running = False
                    return

                lines = self.text_editor.get("1.0", tk.END).splitlines()
                insert_index = len(lines)

                if position == "TOP":
                    insert_index = 0
                elif position == "BOTTOM":
                    insert_index = len(lines)
                elif position in ["BEFORE", "AFTER"]:
                    start_marker = "PART: " + target_part + " START"
                    end_marker = "PART: " + target_part + " END"

                    i = 0
                    while i < len(lines):
                        stripped = lines[i].strip()

                        if start_marker in stripped:
                            if position == "BEFORE":
                                insert_index = i
                            else:
                                j = i
                                while j < len(lines):
                                    stripped_j = lines[j].strip()
                                    if end_marker in stripped_j:
                                        insert_index = j + 1
                                        break
                                    j += 1
                            break
                        i += 1

                block = plugin_content.splitlines()

                if hasattr(self, "insert_block_with_spacing"):
                    new_lines = self.insert_block_with_spacing(lines, insert_index, block)
                else:
                    new_lines = lines[:insert_index] + [""] + block + [""] + lines[insert_index:]

                _set_editor_text_only(new_lines)
                self.last_changed_part_names = set([part_name])

                if not _select_part_if_present(part_name):
                    try:
                        self.apply_editor_marks()
                    except Exception:
                        pass

                self.append_assistant_log("ADD_PART im Monitor eingefügt")
                self.status_var.set("ADD_PART im Monitor eingefügt – bitte prüfen und selbst speichern")
                success = True

            except Exception as exc:
                self.append_assistant_log("FEHLER ADD_PART: " + str(exc))

        elif action == "REMOVE_PART":
            try:
                if not _load_target_into_editor(target_path):
                    self.assistant_is_running = False
                    return

                lines = self.text_editor.get("1.0", tk.END).splitlines()

                start_marker = "PART: " + part_name + " START"
                end_marker = "PART: " + part_name + " END"

                start_index = None
                end_index = None

                i = 0
                while i < len(lines):
                    stripped = lines[i].strip()

                    if start_marker in stripped:
                        start_index = i

                    if end_marker in stripped:
                        end_index = i
                        break

                    i += 1

                if start_index is None or end_index is None:
                    self.append_assistant_log("FEHLER: PART nicht gefunden für REMOVE")
                    self.status_var.set("Update fehlgeschlagen")
                    self.assistant_is_running = False
                    return

                removed_block = lines[start_index:end_index + 1]

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = "removed_{0}_{1}.txt".format(part_name, timestamp)
                backup_path = os.path.join(os.getcwd(), backup_name)

                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(removed_block).rstrip("\n") + "\n")

                new_lines = lines[:start_index] + lines[end_index + 1:]

                _set_editor_text_only(new_lines)
                self.last_changed_part_names = set()

                _select_nearest_part_by_line(start_index)

                self.append_assistant_log("REMOVE_PART im Monitor ausgeführt")
                self.append_assistant_log("Backup gespeichert: " + backup_name)
                self.status_var.set("REMOVE_PART im Monitor ausgeführt – bitte prüfen und selbst speichern")
                success = True

            except Exception as exc:
                self.append_assistant_log("FEHLER REMOVE_PART: " + str(exc))

        elif action == "REPLACE_PART":
            try:
                if not _load_target_into_editor(target_path):
                    self.assistant_is_running = False
                    return

                self.replace_input.delete("1.0", "end")
                self.replace_input.insert("1.0", plugin_content)
                self.detect_target_part_from_replace_box()
                self.apply_replace_from_box()

                self.append_assistant_log("REPLACE im Monitor ausgeführt")
                self.status_var.set("REPLACE im Monitor ausgeführt – bitte prüfen und selbst speichern")
                success = True

            except Exception as exc:
                self.append_assistant_log("FEHLER REPLACE: " + str(exc))

        else:
            self.append_assistant_log("STOP: Aktion unbekannt: " + action)

        if success:
            if not self.assistant_step("Update im Monitor angewendet"):
                return

            if not self.assistant_step("Plugin wird archiviert..."):
                return

            try:
                self._move_used_plugin_file()
                self.append_assistant_log("Plugin archiviert")
            except Exception as exc:
                self.append_assistant_log("WARNUNG: Plugin konnte nicht verschoben werden: " + str(exc))

            if not self.assistant_step("Update abgeschlossen"):
                return

            self.finish_assistant_run("Update fertig")

            if restart_value == "YES":
                self.append_assistant_log("Hinweis: Bitte Tool erst nach dem Speichern neu starten")
                self._show_restart_required_dialog()
        else:
            self.append_assistant_log("Update NICHT erfolgreich – Plugin bleibt erhalten")
            self.status_var.set("Update fehlgeschlagen")
            self.assistant_is_running = False
    # ===== PART: ASSISTANT_PLUGIN_EXECUTE END =====
# ===== PART: ASSISTANT_LOGIC END =====

# ===== PART: SEARCH START =====
    def open_search_window(self):
        try:
            if hasattr(self, "search_window") and self.search_window is not None:
                try:
                    self.search_window.deiconify()
                    self.search_window.lift()
                    self.search_window.focus_force()
                    if hasattr(self, "search_entry") and self.search_entry is not None:
                        self.search_entry.focus_set()
                        self.search_entry.selection_range(0, tk.END)
                    return
                except Exception:
                    pass

            self.search_window = tk.Toplevel(self.root)
            self.search_window.title("Suchen")

            width = 460
            height = 190

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            x = int((screen_width / 2) - (width / 2))
            y = int((screen_height / 2) - (height / 2))

            self.search_window.geometry("{0}x{1}+{2}+{3}".format(width, height, x, y))
            self.search_window.resizable(False, False)

            try:
                self.search_window.transient(self.root)
            except Exception:
                pass

            if not hasattr(self, "search_matches"):
                self.search_matches = []
            if not hasattr(self, "search_current_index"):
                self.search_current_index = -1
            if not hasattr(self, "search_text_var"):
                self.search_text_var = tk.StringVar()

            self.search_result_var = tk.StringVar()
            self.search_result_var.set("Noch keine Suche gestartet")

            frame = tk.Frame(self.search_window, padx=10, pady=10)
            frame.pack(fill="both", expand=True)

            lbl = tk.Label(frame, text="Suchtext:")
            lbl.pack(anchor="w")

            self.search_entry = tk.Entry(frame, textvariable=self.search_text_var)
            self.search_entry.pack(fill="x", pady=(0, 10))
            self.search_entry.focus_set()
            self.search_entry.selection_range(0, tk.END)

            btn_frame = tk.Frame(frame)
            btn_frame.pack(fill="x", pady=(0, 8))

            btn_find = tk.Button(
                btn_frame,
                text="Suchen",
                width=10,
                command=self.search_in_editor
            )
            btn_find.pack(side="left", padx=(0, 6))

            btn_next = tk.Button(
                btn_frame,
                text="Nächster",
                width=10,
                command=self.search_next_match
            )
            btn_next.pack(side="left", padx=(0, 6))

            btn_prev = tk.Button(
                btn_frame,
                text="Vorheriger",
                width=10,
                command=self.search_previous_match
            )
            btn_prev.pack(side="left", padx=(0, 6))

            btn_close = tk.Button(
                btn_frame,
                text="Schließen",
                width=10,
                command=self.close_search_window
            )
            btn_close.pack(side="right")

            info = tk.Label(
                frame,
                textvariable=self.search_result_var,
                anchor="w",
                justify="left"
            )
            info.pack(fill="x")

            try:
                self.search_window.bind("<Return>", lambda event: self.search_in_editor())
                self.search_window.bind("<F3>", lambda event: self.search_next_match())
                self.search_window.bind("<Shift-F3>", lambda event: self.search_previous_match())
                self.search_window.bind("<Escape>", lambda event: self.close_search_window())
            except Exception:
                pass

        except Exception as e:
            try:
                messagebox.showerror("Fehler", str(e))
            except Exception:
                pass

    def close_search_window(self):
        try:
            self.text_editor.tag_remove("search_match", "1.0", tk.END)
            self.text_editor.tag_remove("search_current", "1.0", tk.END)
        except Exception:
            pass

        try:
            if hasattr(self, "search_window") and self.search_window is not None:
                self.search_window.destroy()
        except Exception:
            pass

        self.search_window = None

    def _apply_search_tags(self):
        try:
            self.text_editor.tag_remove("search_match", "1.0", tk.END)
            self.text_editor.tag_remove("search_current", "1.0", tk.END)

            self.text_editor.tag_config("search_match", background="#fff2a8")
            self.text_editor.tag_config("search_current", background="#ffb347")

            index = 0
            while index < len(self.search_matches):
                start_pos, end_pos = self.search_matches[index]
                self.text_editor.tag_add("search_match", start_pos, end_pos)
                index += 1

            if self.search_current_index >= 0 and self.search_current_index < len(self.search_matches):
                start_pos, end_pos = self.search_matches[self.search_current_index]
                self.text_editor.tag_add("search_current", start_pos, end_pos)
                self.text_editor.mark_set(tk.INSERT, start_pos)
                self.text_editor.see(start_pos)
        except Exception:
            pass

    def _update_search_status(self):
        try:
            count = len(self.search_matches)
            if count <= 0:
                self.search_result_var.set("Kein Treffer gefunden – Suche wurde ausgeführt")
                self.status_var.set("Suche: kein Treffer")
            else:
                self.search_result_var.set(
                    "Treffer {0} von {1}".format(self.search_current_index + 1, count)
                )
                self.status_var.set(
                    "Suche: Treffer {0} von {1}".format(self.search_current_index + 1, count)
                )
        except Exception:
            pass

    def search_in_editor(self):
        try:
            text = self.search_text_var.get()
            self.search_matches = []
            self.search_current_index = -1

            self.text_editor.tag_remove("search_match", "1.0", tk.END)
            self.text_editor.tag_remove("search_current", "1.0", tk.END)

            if not text:
                self.search_result_var.set("Bitte Suchtext eingeben")
                self.status_var.set("Suche: kein Text")
                return

            start = "1.0"
            while True:
                pos = self.text_editor.search(text, start, stopindex=tk.END, nocase=True)
                if not pos:
                    break

                end = "{0}+{1}c".format(pos, len(text))
                self.search_matches.append((pos, end))
                start = end

            if len(self.search_matches) > 0:
                self.search_current_index = 0

            self._apply_search_tags()
            self._update_search_status()

            try:
                if hasattr(self, "search_entry") and self.search_entry is not None:
                    self.search_entry.focus_set()
                    self.search_entry.selection_range(0, tk.END)
                if hasattr(self, "search_window") and self.search_window is not None:
                    self.search_window.lift()
            except Exception:
                pass

        except Exception as e:
            try:
                messagebox.showerror("Fehler", str(e))
            except Exception:
                pass

    def search_next_match(self):
        try:
            if not hasattr(self, "search_matches") or len(self.search_matches) == 0:
                self.search_in_editor()
                return

            self.search_current_index += 1
            if self.search_current_index >= len(self.search_matches):
                self.search_current_index = 0

            self._apply_search_tags()
            self._update_search_status()
        except Exception:
            pass

    def search_previous_match(self):
        try:
            if not hasattr(self, "search_matches") or len(self.search_matches) == 0:
                self.search_in_editor()
                return

            self.search_current_index -= 1
            if self.search_current_index < 0:
                self.search_current_index = len(self.search_matches) - 1

            self._apply_search_tags()
            self._update_search_status()
        except Exception:
            pass
# ===== PART: SEARCH END =====



    # ===== PART: SESSION_RESTORE START =====
    def get_current_selected_part_name(self):
        if not self.part_listbox.curselection():
            return None

        index = self.part_listbox.curselection()[0]
        if index < 0 or index >= len(self.parts):
            return None

        return self.parts[index].name

    def write_restart_session_file(self):
        data = {
            "current_file": self.current_file,
            "selected_part": self.get_current_selected_part_name(),
            "project_files": self.project_files[:],
            "project_main_file": self.project_main_file,
        }

        f = open(self.session_file_path, "w", encoding="utf-8")
        json.dump(data, f, indent=2)
        f.close()

    def remove_restart_session_file(self):
        try:
            if os.path.exists(self.session_file_path):
                os.remove(self.session_file_path)
        except Exception:
            pass

    def restore_session_after_restart(self):
        if not os.path.exists(self.session_file_path):
            return

        try:
            f = open(self.session_file_path, "r", encoding="utf-8")
            data = json.load(f)
            f.close()
        except Exception:
            self.remove_restart_session_file()
            return

        self.remove_restart_session_file()

        restored_project_files = data.get("project_files", [])
        restored_current_file = data.get("current_file")
        restored_part_name = data.get("selected_part")
        restored_main_file = data.get("project_main_file")

        self.project_main_file = restored_main_file

        index = 0
        while index < len(restored_project_files):
            path = restored_project_files[index]
            if path and os.path.exists(path):
                self.add_project_file(path)
            index += 1

        if restored_current_file and os.path.exists(restored_current_file):
            self.load_file_by_path(restored_current_file)

            if restored_part_name:
                self.select_part_by_name(restored_part_name)

            self.status_var.set("Sitzung nach Neustart wiederhergestellt")

    def select_part_by_name(self, part_name):
        if not part_name:
            return False

        index = 0
        while index < len(self.parts):
            if self.parts[index].name == part_name:
                self.part_listbox.selection_clear(0, tk.END)
                self.part_listbox.selection_set(index)
                self.part_listbox.activate(index)
                self.on_part_select(None)
                return True
            index += 1

        return False
    # ===== PART: SESSION_RESTORE END =====

    # ===== PART: RESTART START =====
    def restart_application(self):
        if not self.confirm_discard_unsaved_changes():
            return

        try:
            self.write_restart_session_file()
        except Exception as exc:
            messagebox.showerror(
                "Neustart-Fehler",
                "Sitzung konnte nicht gespeichert werden:\n\n" + str(exc)
            )
            self.status_var.set("Neustart fehlgeschlagen")
            return

        try:
            cmd = [sys.executable] + sys.argv
            subprocess.Popen(cmd, cwd=os.getcwd())
        except Exception as exc:
            messagebox.showerror("Neustart-Fehler", str(exc))
            self.status_var.set("Neustart fehlgeschlagen")
            return

        self.status_var.set("Tool wird neu gestartet")
        self.root.after(150, self.root.destroy)
    # ===== PART: RESTART END =====

    # ===== PART: UNDO_REDO START =====
    def get_active_undo_widget(self):
        widget = self.root.focus_get()
        if widget is self.text_editor:
            return self.text_editor
        if widget is self.replace_input:
            return self.replace_input
        if widget is self.cfg_value_entry:
            return self.cfg_value_entry
        return self.text_editor

    def undo_action(self):
        widget = self.get_active_undo_widget()
        try:
            widget.edit_undo()
            self.status_var.set("Rückgängig")
        except Exception:
            try:
                if hasattr(self, "_safe_undo_restore") and self._safe_undo_restore():
                    return
            except Exception:
                pass
            self.status_var.set("Nichts rückgängig zu machen")

        self.update_dirty_parts_safe()
        self.update_action_states()

    def redo_action(self):
        widget = self.get_active_undo_widget()
        try:
            widget.edit_redo()
            self.status_var.set("Wiederholen")
        except Exception:
            self.status_var.set("Nichts zu wiederholen")

        self.update_dirty_parts_safe()
        self.update_action_states()

    def update_dirty_parts_safe(self):
        try:
            if self.current_file:
                self.update_dirty_parts()
        except Exception:
            pass

        try:
            self.refresh_project_file_buttons()
        except Exception:
            pass
    # ===== PART: UNDO_REDO END =====

    # ===== PART: SHORTCUTS START =====
    def on_shortcut_paste_editor(self, event):
        try:
            clip_text = self.root.clipboard_get()
        except Exception:
            return "break"

        if self.part_listbox.curselection():
            index = self.part_listbox.curselection()[0]
            if 0 <= index < len(self.parts):
                part = self.parts[index]

                try:
                    name, inner = self.extract_part_name_and_inner_text(clip_text)
                except Exception:
                    name = None
                    inner = clip_text

                if name:
                    if name != part.name:
                        result = messagebox.askyesno(
                            "PART stimmt nicht überein",
                            "Zwischenablage enthält PART:\n\n{0}\n\n"
                            "Ausgewählt ist:\n\n{1}\n\n"
                            "Trotzdem ersetzen?".format(name, part.name)
                        )
                        if not result:
                            return "break"

                    self.replace_part_content(part, inner)
                    self.status_var.set("PART komplett ersetzt per STRG+V")
                    return "break"

                self.replace_part_content(part, clip_text)
                self.status_var.set("PART-Inhalt ersetzt per STRG+V")
                return "break"

        try:
            self.text_editor.insert(tk.INSERT, clip_text)
        except Exception:
            pass

        return "break"

    def on_shortcut_new_file(self, event=None):
        self.new_file()
        return "break"

    def on_shortcut_save_all(self, event=None):
        try:
            self.save_all_changed_files()
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))
        return "break"

    def on_shortcut_load(self, event):
        self.load_file()
        return "break"

    def on_shortcut_save(self, event):
        self.save_file()
        return "break"

    def on_shortcut_save_as(self, event):
        self.save_file_as()
        return "break"

    def on_shortcut_clear_view(self, event):
        self.clear_view()
        return "break"

    def on_shortcut_quit(self, event):
        self.request_close()
        return "break"

    def on_shortcut_replace_part(self, event):
        self.replace_part()
        return "break"

    def on_shortcut_export_part(self, event):
        self.export_selected_part()
        return "break"

    def on_shortcut_import_part(self, event):
        self.import_part_file()
        return "break"

    def on_shortcut_paste_box(self, event):
        self.paste_clipboard_to_replace_box()
        return "break"

    def on_shortcut_clear_box(self, event):
        self.clear_replace_box()
        return "break"

    def on_shortcut_detect_target(self, event):
        self.detect_target_part_from_replace_box()
        return "break"

    def on_shortcut_apply_replace(self, event):
        self.apply_replace_from_box()
        return "break"

    def on_shortcut_replace_from_clipboard(self, event):
        self.replace_from_clipboard()
        return "break"

    def on_shortcut_rescan_cfg(self, event):
        self.scan_config_vars()
        return "break"

    def on_shortcut_add_project_file(self, event):
        self.add_project_file_via_dialog()
        return "break"

    def on_shortcut_close_current_file(self, event):
        self.close_current_project_file()
        return "break"

    def on_shortcut_close_all_files(self, event):
        self.close_all_project_files()
        return "break"

    def on_shortcut_undo(self, event):
        self.undo_action()
        return "break"

    def on_shortcut_redo(self, event):
        self.redo_action()
        return "break"

    def on_shortcut_add_part(self, event):
        self.add_new_part()
        return "break"

    def on_shortcut_remove_part(self, event):
        self.remove_selected_part()
        return "break"

    def on_shortcut_restart_tool(self, event):
        self.restart_application()
        return "break"

    def on_shortcut_abort_assistant(self, event):
        self.request_abort_assistant_run()
        return "break"

    def clear_editor_preview_marks(self, event=None):
        try:
            self.text_editor.tag_remove("replace_preview_target", "1.0", tk.END)
            self.text_editor.tag_remove("part_active", "1.0", tk.END)
        except Exception:
            pass
        return None
    # ===== PART: SHORTCUTS END =====

    # ===== PART: HELPERS START =====
    # ===== PART: HELPERS_UI START =====
    def format_size(self, size):
        try:
            size = float(size)
        except Exception:
            return "?"

        if size < 1024:
            return "{0:.0f} B".format(size)
        if size < 1024 * 1024:
            return "{0:.1f} KB".format(size / 1024.0)
        return "{0:.2f} MB".format(size / (1024.0 * 1024.0))

    def get_current_editor_size(self):
        try:
            text = self.text_editor.get("1.0", "end")
            return len(text.encode("utf-8"))
        except Exception:
            return 0

    def get_disk_file_size(self, path):
        try:
            if path and os.path.exists(path):
                return os.path.getsize(path)
        except Exception:
            pass
        return 0

    def update_window_title(self):
        self.root.title(get_app_title())

        if self.current_file:
            filename = os.path.basename(self.current_file)

            disk_size = self.get_disk_file_size(self.current_file)
            current_size = self.get_current_editor_size()

            text = "{0}  |  Disk: {1}  |  Aktuell: {2}".format(
                filename,
                self.format_size(disk_size),
                self.format_size(current_size)
            )

            self.current_file_display_var.set(text)
        else:
            self.current_file_display_var.set("Keine Datei geladen")

        self.update_project_size_status()

    def update_project_size_status(self):
        total_size = 0
        allowed_ext = (".py", ".cs", ".txt")

        current_normalized = None
        if self.current_file:
            current_normalized = self.normalize_project_path(self.current_file)

        matching_set = set()
        if hasattr(self, "matching_project_files"):
            matching_set = self.matching_project_files

        index = 0
        while index < len(self.project_files):
            path = self.project_files[index]

            try:
                norm = self.normalize_project_path(path)
                ext = os.path.splitext(path)[1].lower()

                if ext not in allowed_ext:
                    index += 1
                    continue

                if norm in matching_set:
                    index += 1
                    continue

                if norm == current_normalized:
                    total_size += self.get_current_editor_size()
                else:
                    total_size += self.get_disk_file_size(path)

            except Exception:
                pass

            index += 1

        if not hasattr(self, "project_size_var"):
            self.project_size_var = tk.StringVar()

        try:
            self.project_size_var.set(
                "Projektgröße: {0}".format(self.format_size(total_size))
            )
        except Exception:
            pass

    def _update_save_button_highlight(self, has_file):
        try:
            has_unsaved = False
            if has_file:
                has_unsaved = self.has_unsaved_changes()

            if hasattr(self, "btn_toolbar_save"):
                if has_file and has_unsaved:
                    self.btn_toolbar_save.config(bg="#ffe08a", activebackground="#ffe08a")
                else:
                    self.btn_toolbar_save.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
        except Exception:
            try:
                if hasattr(self, "btn_toolbar_save"):
                    self.btn_toolbar_save.config(bg="SystemButtonFace")
            except Exception:
                pass
    # ===== PART: HELPERS_UI END =====
    
    # ===== PART: HELPERS_ACTION_STATES START =====
    def update_action_states(self):
        has_file = self.current_file is not None

        try:
            if hasattr(self, "btn_save"):
                if has_file:
                    self.btn_save.config(state="normal")
                else:
                    self.btn_save.config(state="disabled")
        except Exception:
            pass
    # ===== PART: HELPERS_ACTION_STATES END =====
    
    

    # ===== PART: HELPERS_BACKUP START =====
    def _create_full_project_backup_v2(self):
        import shutil
        import time

        try:
            base_dir = os.getcwd()
            backup_root = os.path.join(base_dir, "_backups")

            if not os.path.exists(backup_root):
                os.makedirs(backup_root)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(backup_root, "backup_" + timestamp)

            os.makedirs(backup_dir)

            # Alle relevanten Dateien sichern
            allowed_ext = (".py", ".txt", ".json")

            for root, dirs, files in os.walk(base_dir):
                # Backup-Ordner selbst überspringen
                if "_backups" in root:
                    continue

                for file in files:
                    if file.lower().endswith(allowed_ext):
                        src_path = os.path.join(root, file)

                        rel_path = os.path.relpath(src_path, base_dir)
                        dst_path = os.path.join(backup_dir, rel_path)

                        dst_folder = os.path.dirname(dst_path)
                        if not os.path.exists(dst_folder):
                            os.makedirs(dst_folder)

                        shutil.copy2(src_path, dst_path)

            self.append_assistant_log("Backup erstellt: " + backup_dir)

        except Exception as exc:
            self.append_assistant_log("FEHLER beim Backup: " + str(exc))
    # ===== PART: HELPERS_BACKUP END =====
    # ===== PART: HELPERS END =====
# ===== PART: CLASS_MAIN END =====
