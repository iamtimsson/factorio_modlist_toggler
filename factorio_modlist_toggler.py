import tkinter as tk
import json
import os
import shutil

class ModToggleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factorio Mod Toggler")
        self.confirm_dict = {
            "confirm_backup": False,
            "confirm_restore": False,
            "confirm_toggle": False,
            "confirm_delete": False
        }
        self.mods_info = {}
        self.create_ui()
        self.load_mods()

    def create_ui(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.button_frame.config(borderwidth=2, relief="solid")

        button_width = 10

        buttons = [
            ("Toggle", self.confirm_toggle),
            ("Backup", self.confirm_backup),
            ("Restore", self.confirm_restore),
            ("Delete", self.confirm_delete),
            ("Alert", self.show_alert),
            ("Czech Mods", self.czech_mods),
            ("Exit", self.root.quit)
        ]

        for i, (text, command) in enumerate(buttons):
            button_name = f"{text.lower()}_button"
            setattr(self, button_name, tk.Button(self.button_frame, text=text, command=command, width=button_width))
            button = getattr(self, button_name)
            button.grid(row=i, column=0, sticky="ew")

        self.root.bind("<Escape>", self.revert_confirm)

        self.mod_list_frame = tk.Frame(self.root)
        self.mod_list_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.mod_list_frame.config(borderwidth=2, relief="solid")

        self.mod_listbox = tk.Listbox(self.mod_list_frame, selectmode=tk.MULTIPLE)
        self.mod_listbox.pack(fill=tk.BOTH, expand=True)
        self.mod_listbox.bind("<Double-Button-1>", self.on_mod_listbox_doubleclick)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def load_mods(self):
        self.mods_info = {}

        mods_directory = self.get_mods_directory()
        mod_list_path = os.path.join(mods_directory, "mod-list.json")

        with open(mod_list_path, "r") as file:
            data = json.load(file)

        for mod in data["mods"]:
            mod_name = mod["name"]
            if mod_name != "base":
                self.mods_info[mod_name] = {"selected": False, "enabled": False, "favorite": mod.get("favorite", False)}

        self.populate_mod_listbox()

    def populate_mod_listbox(self):
        self.mod_listbox.delete(0, tk.END)

        for mod_name, info in self.mods_info.items():
            selected = info["selected"]
            enabled = info["enabled"]
            favorite = info["favorite"]
            mod_info = f"[{'*' if favorite else ' '}] [{'x' if enabled else ' '}] {mod_name}"

            self.mod_listbox.insert(tk.END, mod_info)

    def on_mod_listbox_doubleclick(self, event):
        selected_indices = self.mod_listbox.curselection()
        for index in selected_indices:
            self.toggle_enabled(index)

    def toggle_enabled(self, index):
        mod_name = list(self.mods_info.keys())[index]
        self.mods_info[mod_name]["enabled"] = not self.mods_info[mod_name]["enabled"]
        self.populate_mod_listbox()

    def toggle_favorite(self, index):
        mod_name = self.get_mod_name_from_index(index)
        self.mods_info[mod_name]["favorite"] = not self.mods_info[mod_name]["favorite"]
        self.populate_mod_listbox()
    def confirm_toggle(self):
        self.show_confirm("toggle", self.toggle_enabled_mods)
    def confirm_backup(self):
        self.show_confirm("backup", self.backup_mod_list)
    def confirm_restore(self):
        self.show_confirm("restore", self.restore_mod_list)
    def confirm_delete(self):
        self.show_confirm("delete", self.delete_backup)

    def toggle_enabled_mods(self):
        for mod_name, info in self.mods_info.items():
            if info["selected"]:
                info["enabled"] = not info["enabled"]
        self.populate_mod_listbox()
        self.print_enabled_status()

    def print_enabled_status(self):
        print("Enabled Status:")
        for mod_name, info in self.mods_info.items():
            print(f"{mod_name}: {'Enabled' if info['enabled'] else 'Disabled'}")

    def show_confirm(self, action, function):
        if not self.confirm_dict[action]:
            button_name = f"{action.split('_')[1]}_button"
            if action == "confirm_toggle":
                button_name = "toggle_button"
            self.confirm_dict[action] = button_name
            self.update_buttons()
        else:
            self.confirm_dict[action] = False
            self.update_buttons()
            if self.confirm_dict["confirm_toggle"]:
                function()

    def revert_confirm(self, event):
        for action in self.confirm_dict:
            if self.confirm_dict[action]:
                button_name = self.confirm_dict[action]
                button = getattr(self, button_name, None)
                if button is not None:
                    button.config(text=action.split('_')[1].capitalize(), width=10)
                print(f"{button_name} Cancelled")
            self.confirm_dict[action] = False
        self.update_buttons()

    def update_buttons(self):
        button_actions = [
            ("confirm_backup", self.confirm_backup),
            ("confirm_restore", self.confirm_restore),
            ("confirm_toggle", self.confirm_toggle),
            ("confirm_delete", self.confirm_delete)
        ]

        for action, button_func in button_actions:
            button_name = f"{action.split('_')[1]}_button"
            if action == "confirm_toggle":
                button_name = "toggle_button"
            button = getattr(self, button_name, None)
            if button is not None:
                if self.confirm_dict[action]:
                    button.config(text="[ESC]", width=5)
                else:
                    button.config(text=action.split('_')[1].capitalize(), width=10)
                    button.config(state=tk.NORMAL)

    def czech_mods(self):
        mods_directory = self.get_mods_directory()
        mod_list_path = os.path.join(mods_directory, "mod-list.json")

        with open(mod_list_path, "r") as file:
            data = json.load(file)

        mods_data = data["mods"]

        for mod in mods_data:
            mod_name = mod["name"]
            if mod_name != "base":
                mod_enabled = mod["enabled"]
                toggle_status = "enabled" if mod_enabled else "disabled"
                print(f"{mod_name} is {toggle_status}")
    def backup_mod_list(self):
        mods_directory = self.get_mods_directory()
        backup_path = os.path.join(mods_directory, "mod-list_backup.json")
        mod_list_path = os.path.join(mods_directory, "mod-list.json")

        shutil.copyfile(mod_list_path, backup_path)
        print("Mod list backed up successfully!")

    def restore_mod_list(self):
        mods_directory = self.get_mods_directory()
        backup_path = os.path.join(mods_directory, "mod-list_backup.json")
        mod_list_path = os.path.join(mods_directory, "mod-list.json")

        if os.path.exists(backup_path):
            shutil.copyfile(backup_path, mod_list_path)
            print("Mod list restored successfully!")
        else:
            print("Backup file not found. Cannot restore mod list.")

    def delete_backup(self):
        mods_directory = self.get_mods_directory()
        backup_path = os.path.join(mods_directory, "mod-list_backup.json")

        if os.path.exists(backup_path):
            os.remove(backup_path)
            print("Backup file deleted successfully!")
        else:
            print("No backup file found.")


    def show_alert(self):
        print(":)")

    def get_mods_directory(self):
        user_home = os.path.expanduser("~")
        if os.name == "nt":
            return os.path.join(user_home, "AppData", "Roaming", "Factorio", "mods")
        else:
            return os.path.join(user_home, ".factorio", "mods")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = ModToggleApp(root)
    root.mainloop()
