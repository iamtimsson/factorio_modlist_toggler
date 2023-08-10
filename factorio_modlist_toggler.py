import json
import os
import shutil
import tkinter as tk

class ModToggleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factorio Mod Toggler")

        self.confirm_dict = {
            "backup": False,
            "restore": False,
            "toggle": False,
            "delete": False
        }
        
        self.mods_to_toggle = [
            "factoriohd_base",
            "factoriohd_logistics",
            "factoriohd_military",
            "factoriohd_modpack",
            "factoriohd_production",
            "factoriohd_terrain",
            "alien-biomes",
            "alien-biomes-hr-terrain"
        ]
        
        self.create_ui()

    def create_ui(self):
        self.czech_button = tk.Button(self.root, text="Czech", command=self.check_mods)
        self.backup_button = tk.Button(self.root, text="Backup", command=self.confirm_backup)
        self.restore_button = tk.Button(self.root, text="Restore", command=self.confirm_restore)
        self.toggle_button = tk.Button(self.root, text="Toggle", command=self.confirm_toggle)
        self.delete_backup_button = tk.Button(self.root, text="Delete", command=self.confirm_delete)
        self.alert_button = tk.Button(self.root, text="Alert", command=self.show_alert)
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)

        self.czech_button.pack()
        self.backup_button.pack()
        self.restore_button.pack()
        self.toggle_button.pack()
        self.delete_backup_button.pack()
        self.alert_button.pack()
        self.exit_button.pack()
        
        self.root.bind("<Escape>", self.revert_confirm)

    def confirm_backup(self):
        self.show_confirm("backup", self.backup_mod_list)

    def confirm_restore(self):
        self.show_confirm("restore", self.restore_mod_list)

    def confirm_toggle(self):
        self.show_confirm("toggle", self.toggle_mods)

    def confirm_delete(self):
        self.show_confirm("delete", self.delete_backup)

    def show_confirm(self, action, function):
        if not self.confirm_dict[action]:
            print(action.capitalize() + " Press [ESC] to cancel.")
            self.confirm_dict[action] = True
            self.update_buttons()
        else:
            self.confirm_dict[action] = False
            self.update_buttons()
            function()

    def revert_confirm(self, event):
        for action in self.confirm_dict:
            self.confirm_dict[action] = False
        self.update_buttons()

    def update_buttons(self):
        for action, button in zip(self.confirm_dict.keys(), [self.backup_button, self.restore_button, self.toggle_button, self.delete_backup_button]):
            button.config(text=action.capitalize() if not self.confirm_dict[action] else "[ESC] to Cancel")

    def get_mods_directory(self):
        user_home = os.path.expanduser("~")
        if os.name == "nt":  # Windows
            return os.path.join(user_home, "AppData", "Roaming", "Factorio", "mods")
        else:  # Unix-like (Linux, macOS)
            return os.path.join(user_home, ".factorio", "mods")
            
    def check_mods(self):
        mods_directory = self.get_mods_directory()
        mod_list_path = os.path.join(mods_directory, "mod-list.json")

        with open(mod_list_path, "r") as file:
            data = json.load(file)

        checked_mods = []

        for mod in data["mods"]:
            mod_name = mod["name"]
            if mod_name in self.mods_to_toggle:
                mod_enabled = mod["enabled"]
                checked_mods.append(f"{mod_name} is {'Enabled' if mod_enabled else 'Disabled'}")

        checked_mods_text = "\n".join(checked_mods)
        print("Mods status:\n", checked_mods_text)

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
            
    def toggle_mods(self):
        mods_directory = self.get_mods_directory()
        mod_list_path = os.path.join(mods_directory, "mod-list.json")
    
        with open(mod_list_path, "r") as file:
            data = json.load(file)
    
        toggled_mods = []
    
        for mod in data["mods"]:
            if mod["name"] in self.mods_to_toggle:
                if mod["enabled"]:
                    mod["enabled"] = False
                    toggled_mods.append(f"Disabled: {mod['name']}")
                else:
                    mod["enabled"] = True
                    toggled_mods.append(f"Enabled: {mod['name']}")
    
        with open(mod_list_path, "w") as file:
            json.dump(data, file, indent=4)
    
        if toggled_mods:
            toggled_mods_text = "\n".join(toggled_mods)
            print("Changed mods:\n", toggled_mods_text)
        else:
            print("No mods changed.")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ModToggleApp(root)
    root.mainloop()
