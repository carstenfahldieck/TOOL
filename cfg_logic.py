# ===== PART: IMPORTS START =====
import re
import tkinter as tk
from tkinter import messagebox
from helpers import find_cfg_index_by_name
# ===== PART: IMPORTS END =====


# ===== PART: DATA_STRUCTURES START =====
class ConfigVar:
    def __init__(self, name, value, line_index, raw_line):
        self.name = name
        self.value = value
        self.line_index = line_index
        self.raw_line = raw_line
# ===== PART: DATA_STRUCTURES END =====


# ===== PART: CLASS_MAIN START =====
class CfgLogicMixin:
    # ===== PART: PARSER_LOGIC START =====
    def scan_config_vars(self):
        self.config_vars = []
        self.cfg_listbox.delete(0, tk.END)
        self.cfg_name_var.set("")
        self.cfg_value_var.set("")
        self.cfg_line_var.set("")
        self.cfg_value_entry.delete("1.0", tk.END)

        lines = self.text_editor.get("1.0", tk.END).splitlines()
        cfg_re = re.compile(r"^\s*(cfg_[A-Za-z0-9_]+)\s*=\s*(.+?)\s*$")

        index = 0
        while index < len(lines):
            line = lines[index]
            stripped = line.strip()

            if stripped and (not stripped.startswith("#")) and (not stripped.startswith("//")):
                match = cfg_re.match(line)
                if match:
                    name = match.group(1).strip()
                    value = match.group(2).strip()
                    self.config_vars.append(ConfigVar(name, value, index, line))
                    self.cfg_listbox.insert(tk.END, "{0} = {1}".format(name, value))

            index += 1

        self.reset_cfg_list_visuals()
        self.cfg_count_var.set("{0} gefunden".format(len(self.config_vars)))
        self.update_action_states()
    # ===== PART: PARSER_LOGIC END =====

    # ===== PART: CFG_VISUALS START =====
    def reset_cfg_list_visuals(self):
        index = 0
        while index < len(self.config_vars):
            try:
                self.cfg_listbox.itemconfig(index, background="white", foreground="black")
            except Exception:
                pass
            index += 1

    def highlight_cfgs_for_part(self, part):
        self.reset_cfg_list_visuals()
        self.cfg_listbox.selection_clear(0, tk.END)

        matching_indices = []
        index = 0
        while index < len(self.config_vars):
            cfg_var = self.config_vars[index]
            if cfg_var.line_index >= part.start and cfg_var.line_index <= part.end:
                matching_indices.append(index)
                try:
                    self.cfg_listbox.itemconfig(index, background="#fff2a8", foreground="black")
                except Exception:
                    pass
            index += 1

        if len(matching_indices) > 0:
            first_index = matching_indices[0]
            self.cfg_listbox.selection_set(first_index)
            self.cfg_listbox.activate(first_index)
            self.cfg_listbox.see(first_index)
            self.on_cfg_select(None)
        else:
            self.cfg_name_var.set("")
            self.cfg_value_var.set("")
            self.cfg_line_var.set("")
            self.cfg_value_entry.delete("1.0", tk.END)

        self.update_action_states()
    # ===== PART: CFG_VISUALS END =====

    # ===== PART: UI_LOGIC START =====
    def on_cfg_select(self, event):
        if not self.cfg_listbox.curselection():
            self.update_action_states()
            return

        index = self.cfg_listbox.curselection()[0]
        cfg_var = self.config_vars[index]

        self.cfg_name_var.set(cfg_var.name)
        self.cfg_value_var.set(cfg_var.value)
        self.cfg_line_var.set(str(cfg_var.line_index + 1))

        self.cfg_value_entry.delete("1.0", tk.END)
        self.cfg_value_entry.insert("1.0", cfg_var.value)

        active_part_name = None
        if self.part_listbox.curselection():
            part_index = self.part_listbox.curselection()[0]
            active_part_name = self.parts[part_index].name

        start_index = "{0}.0".format(cfg_var.line_index + 1)
        end_index = "{0}.0 lineend".format(cfg_var.line_index + 1)

        self.apply_editor_marks(active_part_name=active_part_name)
        self.text_editor.mark_set(tk.INSERT, start_index)
        self.text_editor.see(start_index)
        self.text_editor.tag_add("cfg_highlight", start_index, end_index)

        self.status_var.set("CFG gewählt: " + cfg_var.name)
        self.update_action_states()

    def on_cfg_double_click(self, event):
        self.apply_cfg_value()
    # ===== PART: UI_LOGIC END =====

    # ===== PART: REPLACE_LOGIC START =====
    def apply_cfg_value(self):
        if not self.cfg_listbox.curselection():
            messagebox.showwarning("Hinweis", "Keine cfg_ Variable ausgewählt")
            return

        index = self.cfg_listbox.curselection()[0]
        cfg_var = self.config_vars[index]
        new_value = self.cfg_value_entry.get("1.0", tk.END).strip()

        all_lines = self.text_editor.get("1.0", tk.END).splitlines()
        target_line = all_lines[cfg_var.line_index]

        pattern = re.compile(r'^(\s*' + re.escape(cfg_var.name) + r'\s*=\s*)(.+?)(\s*)$')
        match = pattern.match(target_line)

        if not match:
            messagebox.showerror(
                "Aktualisierungsfehler",
                "Ausgewählte cfg_ Zeile konnte nicht geändert werden"
            )
            return

        all_lines[cfg_var.line_index] = match.group(1) + new_value

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", "\n".join(all_lines).rstrip("\n") + "\n")

        self.last_changed_part_names = set()
        self.scan_config_vars()
        self.update_dirty_parts()
        self.apply_editor_marks()

        reselection_index = find_cfg_index_by_name(self, cfg_var.name)
        if reselection_index is not None:
            self.cfg_listbox.selection_clear(0, tk.END)
            self.cfg_listbox.selection_set(reselection_index)
            self.cfg_listbox.activate(reselection_index)
            self.cfg_listbox.see(reselection_index)
            self.on_cfg_select(None)

        self.status_var.set("CFG aktualisiert: " + cfg_var.name)
    # ===== PART: REPLACE_LOGIC END =====
# ===== PART: CLASS_MAIN END =====