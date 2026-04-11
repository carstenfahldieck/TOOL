# ===== PART: UI_TEST_BUTTONS START =====
def build_test_buttons(parent, app):
    frame = tk.Frame(parent)
    frame.pack(fill="x", pady=5)

    btn_new = tk.Button(frame, text="TEST: Neuer PART", command=app.add_new_part)
    btn_new.pack(fill="x", pady=2)

    btn_move = tk.Button(frame, text="TEST: PART verschieben", command=app.move_part)
    btn_move.pack(fill="x", pady=2)

    return frame
# ===== PART: UI_TEST_BUTTONS END =====
