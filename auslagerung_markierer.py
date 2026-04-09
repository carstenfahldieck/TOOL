
# ===== PART: START START =====
import tkinter as tk
import difflib


def _is_word_char(ch):
    if ch is None:
        return False
    return ch.isalnum() or ch == "_"


def _expand_diff_to_token_bounds(line, start, end):
    length = len(line)

    while start > 0 and _is_word_char(line[start - 1]):
        start -= 1

    while end < length and _is_word_char(line[end]):
        end += 1

    return start, end


def _configure_preview_tags(text_widget):
    text_widget.tag_configure("line_changed_old", background="#ffe08a")
    text_widget.tag_configure("line_changed_new", background="#c6f7c3")
    text_widget.tag_configure("char_changed_old", background="#ff7f7f")
    text_widget.tag_configure("char_changed_new", background="#6ee56e")


def _fill_text_widget_lines(text_widget, lines):
    text_widget.delete("1.0", "end")

    index = 0
    while index < len(lines):
        text_widget.insert("end", lines[index] + "\n")
        index += 1


def _mark_preview_line_diff(text_widget, tag, lines_a, lines_b):
    text_widget.tag_remove(tag, "1.0", "end")

    max_len = max(len(lines_a), len(lines_b))

    index = 0
    while index < max_len:
        a = lines_a[index] if index < len(lines_a) else ""
        b = lines_b[index] if index < len(lines_b) else ""

        if a != b:
            text_widget.tag_add(tag, "{0}.0".format(index + 1), "{0}.end".format(index + 1))

        index += 1


def _mark_preview_char_diff(text_widget, tag, lines_a, lines_b):
    text_widget.tag_remove(tag, "1.0", "end")

    max_len = max(len(lines_a), len(lines_b))

    line_index = 0
    while line_index < max_len:
        a = lines_a[line_index] if line_index < len(lines_a) else ""
        b = lines_b[line_index] if line_index < len(lines_b) else ""

        if a != b:
            matcher = difflib.SequenceMatcher(None, a, b)

            for op, i1, i2, j1, j2 in matcher.get_opcodes():
                if op != "equal":
                    start, end = _expand_diff_to_token_bounds(b, j1, j2)
                    text_widget.tag_add(
                        tag,
                        "{0}.{1}".format(line_index + 1, start),
                        "{0}.{1}".format(line_index + 1, end)
                    )

        line_index += 1


def _get_first_changed_preview_line(lines_a, lines_b):
    max_len = max(len(lines_a), len(lines_b))

    index = 0
    while index < max_len:
        a = lines_a[index] if index < len(lines_a) else ""
        b = lines_b[index] if index < len(lines_b) else ""

        if a != b:
            return index

        index += 1

    return 0


def _scroll_preview_both_to_line(text_widget, line_index):
    try:
        text_widget.see("{0}.0".format(line_index + 1))
    except Exception:
        pass


def render_preview_engine(parent, old_lines, new_lines, mode):
    wrapper = tk.Frame(parent, bg="white")
    wrapper.pack(fill=tk.BOTH, expand=True)

    if mode == "dual":
        left = tk.Frame(wrapper, bg="white")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(wrapper, bg="white")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_old = tk.Text(left, wrap=tk.NONE, bg="white")
        text_old.pack(fill=tk.BOTH, expand=True)

        text_new = tk.Text(right, wrap=tk.NONE, bg="white")
        text_new.pack(fill=tk.BOTH, expand=True)

        _configure_preview_tags(text_old)
        _configure_preview_tags(text_new)

        _fill_text_widget_lines(text_old, old_lines)
        _fill_text_widget_lines(text_new, new_lines)

        _mark_preview_line_diff(text_old, "line_changed_old", old_lines, new_lines)
        _mark_preview_line_diff(text_new, "line_changed_new", old_lines, new_lines)
        _mark_preview_char_diff(text_old, "char_changed_old", old_lines, new_lines)
        _mark_preview_char_diff(text_new, "char_changed_new", old_lines, new_lines)

        first_changed = _get_first_changed_preview_line(old_lines, new_lines)
        _scroll_preview_both_to_line(text_old, first_changed)
        _scroll_preview_both_to_line(text_new, first_changed)

        return {
            "wrapper": wrapper,
            "old_widget": text_old,
            "new_widget": text_new,
        }

    text_new = tk.Text(wrapper, wrap=tk.NONE, bg="white")
    text_new.pack(fill=tk.BOTH, expand=True)

    _configure_preview_tags(text_new)
    _fill_text_widget_lines(text_new, new_lines)

    _mark_preview_line_diff(text_new, "line_changed_new", old_lines, new_lines)
    _mark_preview_char_diff(text_new, "char_changed_new", old_lines, new_lines)

    first_changed = _get_first_changed_preview_line(old_lines, new_lines)
    _scroll_preview_both_to_line(text_new, first_changed)

    return {
        "wrapper": wrapper,
        "new_widget": text_new,
    }
# ===== PART: START END =====
