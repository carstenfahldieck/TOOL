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

# ===== PART: RANGE_STRUCTURE_VALIDATION START =====
def is_range_fully_inside_existing_part(existing_parts, start_line, end_line):
    """
    Prüft nur die einfache erste Sicherheitsregel:

    True  = der gewählte Bereich liegt vollständig innerhalb eines bestehenden PARTS
    False = der Bereich liegt nicht vollständig innerhalb eines bestehenden PARTS

    Mehr prüfen wir hier bewusst noch nicht.
    """
    if existing_parts is None:
        return False

    try:
        start_line = int(start_line)
        end_line = int(end_line)
    except Exception:
        return False

    if start_line > end_line:
        temp = start_line
        start_line = end_line
        end_line = temp

    index = 0
    while index < len(existing_parts):
        part = existing_parts[index]

        try:
            part_start = int(part.start)
            part_end = int(part.end)
        except Exception:
            index += 1
            continue

        if start_line >= part_start and end_line <= part_end:
            return True

        index += 1

    return False
# ===== PART: RANGE_STRUCTURE_VALIDATION END =====

# ===== PART: CREATE_STRUCTURE_FROM_RANGE START =====
def create_structure_from_range(text, structure_type, start_line, end_line, name, existing_parts=None, marker_prefix="#"):
    """
    Allgemeiner Kern:
    Macht aus einem bestehenden Codebereich ein Struktur-Element
    (erstmal praktisch für PART, später auch für SUB / BAUSTEIN).

    Parameter:
        text:           kompletter Editor-Text
        structure_type: z. B. "PART", "SUB", "BAUSTEIN"
        start_line:     Startzeile (0-basiert)
        end_line:       Endzeile (0-basiert)
        name:           Struktur-Name
        existing_parts: vorhandene PARTS für Minimalprüfung
        marker_prefix:  Standard "#"

    Rückgabe:
        neuer kompletter Text
    """

    if text is None:
        text = ""

    if structure_type is None:
        raise ValueError("structure_type fehlt")

    if name is None:
        raise ValueError("name fehlt")

    structure_type_text = str(structure_type).strip().upper()
    if structure_type_text == "":
        raise ValueError("structure_type ist leer")

    name_text = str(name).strip().upper()
    if name_text == "":
        raise ValueError("name ist leer")

    try:
        start_line = int(start_line)
        end_line = int(end_line)
    except Exception:
        raise ValueError("start_line oder end_line ist ungültig")

    if start_line > end_line:
        temp = start_line
        start_line = end_line
        end_line = temp

    # ===== MINIMALPRÜFUNG =====
    if is_range_fully_inside_existing_part(existing_parts, start_line, end_line):
        raise ValueError("Der gewählte Bereich liegt vollständig in einem bestehenden PART")

    lines = text.splitlines()

    if len(lines) == 0:
        raise ValueError("Der Text enthält keine Zeilen")

    if start_line < 0:
        start_line = 0

    if end_line >= len(lines):
        end_line = len(lines) - 1

    start_marker = (
        str(marker_prefix)
        + " ===== "
        + structure_type_text
        + ": "
        + name_text
        + " START ====="
    )

    end_marker = (
        str(marker_prefix)
        + " ===== "
        + structure_type_text
        + ": "
        + name_text
        + " END ====="
    )

    new_lines = []
    line_index = 0

    while line_index < len(lines):
        if line_index == start_line:
            new_lines.append(start_marker)

        new_lines.append(lines[line_index])

        if line_index == end_line:
            new_lines.append(end_marker)

        line_index += 1

    return "\n".join(new_lines) + "\n"
# ===== PART: CREATE_STRUCTURE_FROM_RANGE END =====