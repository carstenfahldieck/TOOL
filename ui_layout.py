# ===== PART: IMPORTS START =====
import tkinter as tk
# ===== PART: IMPORTS END =====


# ===== PART: MAIN_UI START =====
def build_main_ui(app):
    app.root.grid_rowconfigure(0, weight=0)  # Toolbar
    app.root.grid_rowconfigure(1, weight=0)  # File Header
    app.root.grid_rowconfigure(2, weight=1)  # Main Area
    app.root.grid_rowconfigure(3, weight=0)  # Project Bar
    app.root.grid_rowconfigure(4, weight=0)  # Bottom Bar
    app.root.grid_columnconfigure(0, weight=1)

    build_toolbar(app)
    build_file_header(app)

    app.main_paned = tk.PanedWindow(
        app.root,
        orient=tk.HORIZONTAL,
        sashrelief=tk.RAISED,
        sashwidth=4,
        showhandle=False,
        opaqueresize=True,
        bd=0
    )

    app.main_paned.grid(row=2, column=0, sticky="nsew", padx=8, pady=(2, 2))

    build_left_panel(app)
    build_center_panel(app)
    build_right_panel(app)

    build_project_bar(app)
    build_bottom_bar(app)
    configure_editor_tags(app)
# ===== PART: MAIN_UI END =====


# ===== PART: TOOLBAR START =====
def build_toolbar(app):
    toolbar = tk.Frame(app.root)
    toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(4, 2))

    # Datei-Gruppe
    app.btn_toolbar_load = tk.Button(toolbar, text="Laden", width=10, command=app.load_file)
    app.btn_toolbar_load.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_save = tk.Button(toolbar, text="Speichern", width=10, command=app.save_file)
    app.btn_toolbar_save.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_save_all = tk.Button(toolbar, text="Alle speichern", width=14, command=app.save_all_changed_files)
    app.btn_toolbar_save_all.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_save_as = tk.Button(toolbar, text="Speich. unter", width=14, command=app.save_file_as)
    app.btn_toolbar_save_as.pack(side=tk.LEFT, padx=(0, 10))

    # PART-Gruppe
    app.btn_toolbar_new_part = tk.Button(toolbar, text="Neuer PART", width=12, command=app.add_new_part)
    app.btn_toolbar_new_part.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_replace_part = tk.Button(toolbar, text="Teil laden", width=12, command=app.replace_part)
    app.btn_toolbar_replace_part.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_export_part = tk.Button(toolbar, text="Teil export", width=12, command=app.export_selected_part)
    app.btn_toolbar_export_part.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_import_part = tk.Button(toolbar, text="Teil import", width=12, command=app.import_part_file)
    app.btn_toolbar_import_part.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_remove_part = tk.Button(toolbar, text="Teil löschen", width=12, command=app.remove_selected_part)
    app.btn_toolbar_remove_part.pack(side=tk.LEFT, padx=(0, 10))

    # CFG-Gruppe
    app.btn_toolbar_cfg_rescan = tk.Button(toolbar, text="CFG neu", width=10, command=app.scan_config_vars)
    app.btn_toolbar_cfg_rescan.pack(side=tk.LEFT, padx=(0, 4))

    app.btn_toolbar_cfg_apply = tk.Button(toolbar, text="CFG anw.", width=10, command=app.apply_cfg_value)
    app.btn_toolbar_cfg_apply.pack(side=tk.LEFT, padx=(0, 10))

    # Neustart + TEST
    app.btn_toolbar_restart = tk.Button(toolbar, text="Neustart", width=10, command=app.restart_application)
    app.btn_toolbar_restart.pack(side=tk.RIGHT, padx=(8, 0))

    app.btn_toolbar_test = tk.Button(toolbar, text="TEST", width=10, command=app.test_button_action)
    app.btn_toolbar_test.pack(side=tk.RIGHT, padx=(20, 0))
# ===== PART: TOOLBAR END =====


# ===== PART: FILE_HEADER START =====
def build_file_header(app):
    header = tk.Frame(app.root)
    header.grid(row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=(6, 2))
    header.grid_columnconfigure(0, weight=1)

    app.current_file_display_label = tk.Label(
        header,
        textvariable=app.current_file_display_var,
        anchor="center",
        justify=tk.CENTER
    )
    app.current_file_display_label.grid(row=0, column=0, sticky="ew")
# ===== PART: FILE_HEADER END =====


# ===== PART: LEFT_PANEL START =====
def build_left_panel(app):
    left_panel = tk.Frame(app.main_paned, width=320)
    left_panel.grid_propagate(False)
    left_panel.grid_rowconfigure(1, weight=1)
    left_panel.grid_rowconfigure(3, weight=1)
    left_panel.grid_columnconfigure(0, weight=1)

    tk.Label(left_panel, text="PARTS", anchor="w", padx=8, pady=6).grid(
        row=0, column=0, sticky="ew"
    )

    app.part_listbox = tk.Listbox(left_panel, exportselection=False)
    app.part_listbox.grid(row=1, column=0, sticky="nsew", padx=8)
    app.part_listbox.bind("<<ListboxSelect>>", app.on_part_select)
    app.part_listbox.bind("<Double-Button-1>", app.on_cfg_double_click)

    tk.Label(left_panel, text="CFG VARIABLEN", anchor="w", padx=8, pady=6).grid(
        row=2, column=0, sticky="ew"
    )

    cfg_panel = tk.Frame(left_panel)
    cfg_panel.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
    cfg_panel.grid_rowconfigure(1, weight=1)
    cfg_panel.grid_columnconfigure(0, weight=1)

    cfg_header = tk.Frame(cfg_panel)
    cfg_header.grid(row=0, column=0, sticky="ew")
    cfg_header.grid_columnconfigure(0, weight=1)

    tk.Label(cfg_header, textvariable=app.cfg_count_var, anchor="w").grid(
        row=0, column=0, sticky="w"
    )

    app.cfg_listbox = tk.Listbox(cfg_panel, exportselection=False, height=8)
    app.cfg_listbox.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
    app.cfg_listbox.bind("<<ListboxSelect>>", app.on_cfg_select)
    app.cfg_listbox.bind("<Double-Button-1>", app.on_cfg_double_click)

    app.main_paned.add(left_panel, minsize=220)

    app.left_panel = left_panel
# ===== PART: LEFT_PANEL END =====


# ===== PART: CENTER_PANEL START =====
def build_center_panel(app):
    editor_frame = tk.Frame(app.main_paned)
    editor_frame.grid_rowconfigure(0, weight=1)
    editor_frame.grid_columnconfigure(0, weight=1)

    app.text_editor = tk.Text(editor_frame, wrap=tk.NONE, undo=True)
    app.text_editor.grid(row=0, column=0, sticky="nsew")

    def on_editor_click(event):
        try:
            app.part_listbox.selection_clear(0, tk.END)
        except Exception:
            pass

        try:
            app.clear_editor_preview_marks()
        except Exception:
            pass

    app.text_editor.bind("<Button-1>", on_editor_click, add="+")
    app.text_editor.bind("<Key>", app.clear_editor_preview_marks, add="+")
    app.text_editor.bind("<Control-v>", app.on_shortcut_paste_editor)

    editor_scroll_y = tk.Scrollbar(
        editor_frame, orient=tk.VERTICAL, command=app.text_editor.yview
    )
    editor_scroll_y.grid(row=0, column=1, sticky="ns")
    app.text_editor.config(yscrollcommand=editor_scroll_y.set)

    editor_scroll_x = tk.Scrollbar(
        editor_frame, orient=tk.HORIZONTAL, command=app.text_editor.xview
    )
    editor_scroll_x.grid(row=1, column=0, sticky="ew")
    app.text_editor.config(xscrollcommand=editor_scroll_x.set)

    app.main_paned.add(editor_frame, minsize=320)

    app.center_panel = editor_frame
# ===== PART: CENTER_PANEL END =====


# ===== PART: RIGHT_PANEL START =====
def build_right_panel(app):
    right_panel = tk.Frame(app.main_paned, width=360)
    right_panel.grid_propagate(False)
    right_panel.grid_rowconfigure(1, weight=1)
    right_panel.grid_rowconfigure(4, weight=1)
    right_panel.grid_rowconfigure(7, weight=1)
    right_panel.grid_columnconfigure(0, weight=1)

    # Zielbereich
    target_frame = tk.LabelFrame(right_panel, text="VORSCHAU / ERSETZEN")
    target_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(6, 4))
    target_frame.grid_rowconfigure(2, weight=1)
    target_frame.grid_columnconfigure(0, weight=1)

    app.preview_replace_var = tk.BooleanVar(value=True)
    app.preview_replace_check = tk.Checkbutton(
        target_frame,
        text="Vorschau vor Ersetzen",
        variable=app.preview_replace_var
    )
    app.preview_replace_check.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 4))

    app.detected_target_label = tk.Label(
        target_frame,
        textvariable=app.detected_part_var,
        anchor="w",
        justify=tk.LEFT
    )
    app.detected_target_label.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

    app.replace_input = tk.Text(target_frame, height=10, wrap=tk.NONE, undo=True)
    app.replace_input.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 6))

    replace_scroll_y = tk.Scrollbar(target_frame, orient=tk.VERTICAL, command=app.replace_input.yview)
    replace_scroll_y.grid(row=2, column=1, sticky="ns", pady=(0, 6))
    app.replace_input.config(yscrollcommand=replace_scroll_y.set)

    btn_row = tk.Frame(target_frame)
    btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))
    btn_row.grid_columnconfigure(0, weight=1)
    btn_row.grid_columnconfigure(1, weight=1)
    btn_row.grid_columnconfigure(2, weight=1)
    btn_row.grid_columnconfigure(3, weight=1)

    app.btn_paste_box = tk.Button(btn_row, text="Zwischenablage", command=app.paste_clipboard_to_replace_box)
    app.btn_paste_box.grid(row=0, column=0, sticky="ew", padx=(0, 4))

    app.btn_clear_box = tk.Button(btn_row, text="Feld leeren", command=app.clear_replace_box)
    app.btn_clear_box.grid(row=0, column=1, sticky="ew", padx=4)

    app.btn_detect_target = tk.Button(btn_row, text="Ziel erkennen", command=app.detect_target_part_from_replace_box)
    app.btn_detect_target.grid(row=0, column=2, sticky="ew", padx=4)

    app.btn_apply_replace = tk.Button(btn_row, text="Ersetzen", command=app.apply_replace_from_box)
    app.btn_apply_replace.grid(row=0, column=3, sticky="ew", padx=(4, 0))

    # CFG-Bereich
    cfg_edit_frame = tk.LabelFrame(right_panel, text="CFG BEARBEITEN")
    cfg_edit_frame.grid(row=4, column=0, sticky="nsew", padx=8, pady=4)
    cfg_edit_frame.grid_rowconfigure(4, weight=1)
    cfg_edit_frame.grid_columnconfigure(1, weight=1)

    tk.Label(cfg_edit_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
    tk.Label(cfg_edit_frame, textvariable=app.cfg_name_var, anchor="w").grid(
        row=0, column=1, sticky="ew", padx=8, pady=(6, 2)
    )

    tk.Label(cfg_edit_frame, text="Wert:").grid(row=1, column=0, sticky="nw", padx=8, pady=2)

    app.cfg_value_entry = tk.Text(cfg_edit_frame, height=3, wrap=tk.WORD, undo=True)
    app.cfg_value_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=2)

    tk.Label(cfg_edit_frame, text="Zeile:").grid(row=2, column=0, sticky="w", padx=8, pady=2)
    tk.Label(cfg_edit_frame, textvariable=app.cfg_line_var, anchor="w").grid(
        row=2, column=1, sticky="ew", padx=8, pady=2
    )

    cfg_btn_row = tk.Frame(cfg_edit_frame)
    cfg_btn_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(6, 6))
    cfg_btn_row.grid_columnconfigure(0, weight=1)
    cfg_btn_row.grid_columnconfigure(1, weight=1)

    app.btn_cfg_apply = tk.Button(cfg_btn_row, text="CFG anwenden", command=app.apply_cfg_value)
    app.btn_cfg_apply.grid(row=0, column=0, sticky="ew", padx=(0, 4))

    app.btn_cfg_rescan = tk.Button(cfg_btn_row, text="CFG neu lesen", command=app.scan_config_vars)
    app.btn_cfg_rescan.grid(row=0, column=1, sticky="ew", padx=(4, 0))

    # Assistent
    assistant_frame = tk.LabelFrame(right_panel, text="ASSISTENT / ABLAUF")
    assistant_frame.grid(row=7, column=0, sticky="nsew", padx=8, pady=(4, 8))
    assistant_frame.grid_rowconfigure(0, weight=1)
    assistant_frame.grid_columnconfigure(0, weight=1)

    app.assistant_log_text = tk.Text(assistant_frame, height=10, wrap=tk.WORD, undo=False)
    app.assistant_log_text.grid(row=0, column=0, sticky="nsew", padx=8, pady=(6, 6))

    assistant_btn_row = tk.Frame(assistant_frame)
    assistant_btn_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
    assistant_btn_row.grid_columnconfigure(0, weight=1)
    assistant_btn_row.grid_columnconfigure(1, weight=1)
    assistant_btn_row.grid_columnconfigure(2, weight=1)
    assistant_btn_row.grid_columnconfigure(3, weight=1)

    app.btn_assistant_test = tk.Button(assistant_btn_row, text="Ablauf lesen", command=app.run_test_assistant_flow)
    app.btn_assistant_test.grid(row=0, column=0, sticky="ew", padx=(0, 4))

    app.btn_assistant_abort = tk.Button(assistant_btn_row, text="ESC = Abbruch", command=app.request_abort_assistant_run)
    app.btn_assistant_abort.grid(row=0, column=1, sticky="ew", padx=4)

    app.btn_assistant_load_plugin = tk.Button(assistant_btn_row, text="Plugin laden", command=app.load_update_plugin)
    app.btn_assistant_load_plugin.grid(row=0, column=2, sticky="ew", padx=4)

    app.btn_assistant_validate_plugin = tk.Button(assistant_btn_row, text="Plugin prüfen", command=app.validate_loaded_update_plugin_plan)
    app.btn_assistant_validate_plugin.grid(row=0, column=3, sticky="ew", padx=(4, 0))

    second_btn_row = tk.Frame(assistant_frame)
    second_btn_row.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 6))
    second_btn_row.grid_columnconfigure(0, weight=1)

    app.btn_assistant_start_plugin = tk.Button(second_btn_row, text="Update starten", command=app.start_loaded_update_plugin_run)
    app.btn_assistant_start_plugin.grid(row=0, column=0, sticky="ew")

    app.main_paned.add(right_panel, minsize=260)

    app.right_panel = right_panel
# ===== PART: RIGHT_PANEL END =====


# ===== PART: PROJECT_BAR START =====
def build_project_bar(app):
    project_bar = tk.Frame(app.root)
    project_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=8, pady=(4, 2))
    tk.Label(project_bar, text="Projektdateien:", anchor="w").pack(side=tk.LEFT, padx=(0, 8))

    app.project_files_frame = tk.Frame(project_bar)
    app.project_files_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
# ===== PART: PROJECT_BAR END =====


# ===== PART: BOTTOM_BAR START =====
def build_bottom_bar(app):
    if not hasattr(app, "project_size_var"):
        app.project_size_var = tk.StringVar()
        app.project_size_var.set("Projektgröße: 0 B")

    bottom = tk.Frame(app.root)
    bottom.grid(row=4, column=0, columnspan=3, sticky="ew")

    tk.Label(bottom, textvariable=app.current_file_var, anchor="w").pack(side=tk.LEFT, padx=8)

    tk.Label(bottom, textvariable=app.status_var, anchor="e").pack(side=tk.RIGHT, padx=10)
    tk.Label(bottom, textvariable=app.project_size_var, anchor="e").pack(side=tk.RIGHT, padx=10)
# ===== PART: BOTTOM_BAR END =====


# ===== PART: TAGS START =====
def configure_editor_tags(app):
    app.text_editor.tag_config("part_marker", foreground="#666666")
    app.text_editor.tag_config("part_name", foreground="#003366")
    app.text_editor.tag_config("cfg_line", background="#fff7cc")
    app.text_editor.tag_config("part_active", background="#d9edf7")
    app.text_editor.tag_config("part_changed", background="#ffe0e0")
    app.text_editor.tag_config("replace_preview_target", background="#e6ffe6")

    if hasattr(app, "replace_input"):
        app.replace_input.tag_config("replace_diff_line", background="#fff2a8")
        app.replace_input.tag_config("replace_part_mismatch", background="#ffd6d6")
# ===== PART: TAGS END =====
