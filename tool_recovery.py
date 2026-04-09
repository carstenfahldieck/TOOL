# ===== PART: IMPORTS START =====
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
# ===== PART: IMPORTS END =====


# ===== PART: CONFIG START =====
BACKUP_FOLDER_NAME = "_backups"
# ===== PART: CONFIG END =====


# ===== PART: MAIN CLASS START =====
class RecoveryTool:

    def __init__(self, root):
        self.root = root
        self.root.title("Recovery Tool")
        self.root.geometry("700x400")

        self.backup_dir = os.path.join(os.getcwd(), BACKUP_FOLDER_NAME)

        self.build_ui()
        self.load_backup_files()

    # ===== UI =====
    def build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_restore = tk.Button(
            btn_frame,
            text="Wiederherstellen",
            command=self.restore_selected
        )
        self.btn_restore.pack(side="left")

        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")

        status_label = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_label.pack(fill="x", padx=10, pady=5)

    # ===== LOAD BACKUPS =====
    def load_backup_files(self):
        self.listbox.delete(0, tk.END)

        if not os.path.exists(self.backup_dir):
            self.status_var.set("Kein Backup-Ordner gefunden")
            return

        files = []

        for root, dirs, filenames in os.walk(self.backup_dir):
            for name in filenames:
                path = os.path.join(root, name)
                try:
                    mtime = os.path.getmtime(path)
                    files.append((path, mtime))
                except Exception:
                    pass

        # neueste zuerst
        files.sort(key=lambda x: x[1], reverse=True)

        self.backup_files = files

        for path, mtime in files:
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            display = f"{dt}  |  {os.path.basename(path)}"
            self.listbox.insert(tk.END, display)

        self.status_var.set(f"{len(files)} Backups gefunden")

    # ===== RESTORE =====
    def restore_selected(self):
        if not self.listbox.curselection():
            messagebox.showwarning("Hinweis", "Bitte Backup auswählen")
            return

        index = self.listbox.curselection()[0]
        backup_path = self.backup_files[index][0]

        filename = os.path.basename(backup_path)
        target_path = os.path.join(os.getcwd(), filename)

        # Sicherheits-Backup der aktuellen Datei
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = filename.replace(".", f"_before_restore_{timestamp}.")
            safe_path = os.path.join(os.getcwd(), safe_name)

            try:
                shutil.copy2(target_path, safe_path)
            except Exception as e:
                messagebox.showerror("Fehler", f"Sicherung fehlgeschlagen:\n{e}")
                return

        # Wiederherstellen (KOPIEREN, nicht verschieben!)
        try:
            shutil.copy2(backup_path, target_path)
        except Exception as e:
            messagebox.showerror("Fehler", f"Wiederherstellung fehlgeschlagen:\n{e}")
            return

        self.status_var.set(f"Wiederhergestellt: {filename}")
        messagebox.showinfo("Fertig", f"{filename} wurde wiederhergestellt")

# ===== PART: MAIN CLASS END =====


# ===== PART: ENTRY POINT START =====
if __name__ == "__main__":
    root = tk.Tk()
    app = RecoveryTool(root)
    root.mainloop()
# ===== PART: ENTRY POINT END =====
