# ===== PART: IMPORTS START =====
import tkinter as tk
# ===== PART: IMPORTS END =====


# ===== PART: MENU_SETUP START =====
def create_menu_bar(app):
    menubar = tk.Menu(app.root)

    # DATEI
    app.menu_datei = tk.Menu(menubar, tearoff=0)
    app.menu_datei.add_command(label="Neue Datei", command=app.new_file, accelerator="Strg+Shift+N")
    app.menu_datei.add_command(label="Laden", command=app.load_file, accelerator="Strg+O")
    app.menu_datei.add_command(label="Speichern", command=app.save_file, accelerator="Strg+S")
    app.menu_datei.add_command(label="Speichern unter", command=app.save_file_as, accelerator="Strg+U")
    app.menu_datei.add_separator()
    app.menu_datei.add_command(label="Alle geänderten speichern", command=app.save_all_changed_files, accelerator="Strg+Shift+S")
    app.menu_datei.add_separator()
    app.menu_datei.add_command(label="Datei zur Leiste hinzufügen", command=app.add_project_file_via_dialog, accelerator="Strg+Shift+A")
    app.menu_datei.add_command(label="Aktuelle Datei schließen", command=app.close_current_project_file, accelerator="Strg+Shift+W")
    app.menu_datei.add_command(label="Alle Dateien schließen", command=app.close_all_project_files, accelerator="Strg+Shift+X")
    app.menu_datei.add_separator()
    app.menu_datei.add_command(label="Ansicht leeren", command=app.clear_view, accelerator="Strg+L")
    app.menu_datei.add_separator()
    app.menu_datei.add_command(label="Beenden", command=app.request_close, accelerator="Strg+Q")
    menubar.add_cascade(label="Datei", menu=app.menu_datei)

    # PART
    app.menu_part = tk.Menu(menubar, tearoff=0)
    app.menu_part.add_command(label="Neuer PART", command=app.add_new_part, accelerator="Strg+N")
    app.menu_part.add_command(label="PART löschen", command=app.remove_selected_part, accelerator="Entf")
    app.menu_part.add_separator()
    app.menu_part.add_command(label="Teil laden", command=app.replace_part, accelerator="Strg+T")
    app.menu_part.add_command(label="Teil exportieren", command=app.export_selected_part, accelerator="Strg+E")
    app.menu_part.add_command(label="Teil importieren", command=app.import_part_file, accelerator="Strg+I")
    menubar.add_cascade(label="PART", menu=app.menu_part)

    # BEARBEITEN
    app.menu_bearbeiten = tk.Menu(menubar, tearoff=0)
    app.menu_bearbeiten.add_command(label="Rückgängig", command=app.undo_action, accelerator="Strg+Z")
    app.menu_bearbeiten.add_command(label="Wiederholen", command=app.redo_action, accelerator="Strg+Y")
    app.menu_bearbeiten.add_separator()
    app.menu_bearbeiten.add_command(label="Suchen...", command=app.open_search_window, accelerator="Strg+F")
    app.menu_bearbeiten.add_separator()
    app.menu_bearbeiten.add_command(label="Zwischenablage ins Feld", command=app.paste_clipboard_to_replace_box, accelerator="Strg+B")
    app.menu_bearbeiten.add_command(label="Feld leeren", command=app.clear_replace_box, accelerator="Strg+W")
    app.menu_bearbeiten.add_command(label="Ziel erkennen", command=app.detect_target_part_from_replace_box, accelerator="Strg+R")
    app.menu_bearbeiten.add_command(label="Ersetzen", command=app.apply_replace_from_box, accelerator="Strg+Enter")
    menubar.add_cascade(label="Bearbeiten", menu=app.menu_bearbeiten)

    # EXTRAS
    app.menu_extras = tk.Menu(menubar, tearoff=0)
    app.menu_extras.add_command(label="Update laden", command=app.load_update_plugin)
    app.menu_extras.add_command(label="Plugin prüfen", command=app.validate_loaded_update_plugin_plan)
    app.menu_extras.add_command(label="Update starten", command=app.start_loaded_update_plugin_run)
    menubar.add_cascade(label="Extras", menu=app.menu_extras)

    app.root.config(menu=menubar)
# ===== PART: MENU_SETUP END =====


# ===== PART: SHORTCUTS START =====
def bind_shortcuts(app):
    app.root.bind("<Control-f>", lambda e: app.open_search_window())
# ===== PART: SHORTCUTS END =====
