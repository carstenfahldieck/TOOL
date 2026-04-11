# ===== PART: IMPORTS START =====
# keine externen Imports nötig (reine Logik)
# ===== PART: IMPORTS END =====


# ===== PART: BUILD_PART_BLOCK START =====
def build_part_block(name, marker_prefix="#"):
    """
    Baut den Textblock für einen neuen PART.
    """
    name = name.strip().upper()

    return (
        f"{marker_prefix} ===== PART: {name} START =====\n\n"
        f"{marker_prefix} ===== PART: {name} END =====\n"
    )
# ===== PART: BUILD_PART_BLOCK END =====


# ===== PART: INSERT_IN_EMPTY_FILE START =====
def insert_part_into_empty_text(text, part_block):
    """
    Fügt einen PART in eine komplett leere Datei ein.
    """
    if text.strip() == "":
        return part_block.strip() + "\n"
    return None
# ===== PART: INSERT_IN_EMPTY_FILE END =====


# ===== PART: INSERT_RELATIVE START =====
def insert_part_relative(text, part, part_block, position):
    """
    Fügt einen PART relativ zu einem bestehenden PART ein.

    position:
        "before"
        "after"
    """
    lines = text.splitlines()

    if position == "before":
        insert_index = part.start
    elif position == "after":
        insert_index = part.end + 1
    else:
        raise ValueError("Ungültige Position")

    new_lines = (
        lines[:insert_index]
        + part_block.splitlines()
        + [""]
        + lines[insert_index:]
    )

    return "\n".join(new_lines) + "\n"
# ===== PART: INSERT_RELATIVE END =====


# ===== PART: MAIN_ENTRY START =====
def create_new_part_text(
    text,
    part_name,
    existing_parts,
    target_part=None,
    position=None,
    marker_prefix="#"
):
    """
    Hauptfunktion zum Erstellen eines neuen PART.

    Parameter:
        text: aktueller Editor-Inhalt
        part_name: Name des neuen PART
        existing_parts: Liste der vorhandenen PART-Objekte
        target_part: PART-Objekt (optional)
        position: "before" / "after" (optional)

    Rückgabe:
        neuer Text
    """

    part_block = build_part_block(part_name, marker_prefix)

    # ===== LEERE DATEI =====
    if not existing_parts:
        result = insert_part_into_empty_text(text, part_block)
        if result is not None:
            return result

    # ===== RELATIV ZU PART =====
    if target_part is not None and position is not None:
        return insert_part_relative(text, target_part, part_block, position)

    # ===== FALLBACK =====
    raise ValueError("Ungültiger Zustand für PART-Erstellung")
# ===== PART: MAIN_ENTRY END =====
# ===== PART: CREATE_NEW_PART_TEXT START =====
def create_new_part_text(text, part_name, existing_parts, target_part, position, marker_prefix="#", custom_block=None):
    lines = text.splitlines()

    # ===== BLOCK ERZEUGEN ODER ÜBERNEHMEN =====
    if custom_block is not None:
        # vorhandener Block (z. B. beim Verschieben)
        block_lines = custom_block
    else:
        # neuer PART
        block_lines = [
            f"{marker_prefix} ===== PART: {part_name} START =====",
            "",
            "",
            f"{marker_prefix} ===== PART: {part_name} END ====="
        ]

    # ===== FALL: KEINE PARTS VORHANDEN =====
    if not existing_parts or target_part is None or position is None:
        new_lines = lines + block_lines
        return "\n".join(new_lines) + "\n"

    # ===== POSITION ERMITTELN =====
    insert_index = None

    if position == "before":
        insert_index = target_part.start
    elif position == "after":
        insert_index = target_part.end + 1
    else:
        raise ValueError("Ungültige Position")

    # ===== EINFÜGEN =====
    new_lines = (
        lines[:insert_index]
        + block_lines
        + lines[insert_index:]
    )

    return "\n".join(new_lines) + "\n"
# ===== PART: CREATE_NEW_PART_TEXT END =====
