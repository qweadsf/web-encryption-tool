import customtkinter as ctk
from tkinter import simpledialog
import keyboard
from pynput.mouse import Controller
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw, ImageFont
import threading
import time

class SecureLockerApp:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.root = root
        self.root.geometry("500x400")
        self.root.title("Secure Locker")
        self.mouse_controller = Controller()
        self.is_locked = False

        self.lock_hotkey = 'ctrl+alt+l'
        self.unlock_hotkey = 'ctrl+alt+u'
        self.safe_keys = set(self.unlock_hotkey.split('+'))

        self.create_logo_icon()
        self.setup_gui()
        self.show_typing_animation()
        self.setup_tray()

    def create_logo_icon(self):
        self.logo = Image.new("RGB", (100, 100), (0, 0, 0))
        draw = ImageDraw.Draw(self.logo)
        draw.ellipse((10, 10, 90, 90), fill=(0, 255, 0))
        font = ImageFont.load_default()
        draw.text((35, 35), "S", fill=(0, 0, 0), font=font)
        self.logo.save("logo.ico")

    def setup_gui(self):
        self.title_label = ctk.CTkLabel(self.root, text="Secure Locker", font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.root, text="", font=("Helvetica", 16, "bold"))
        self.status_label.pack(pady=10)

        self.mouse_var = ctk.CTkCheckBox(self.root, text="Enable Mouse Lock", font=("Helvetica", 15))
        self.mouse_var.pack(pady=10)

        self.lock_button = ctk.CTkButton(self.root, text="Lock Keyboard", command=self.lock_keyboard, font=("Helvetica", 16))
        self.lock_button.pack(pady=10)

        self.unlock_button = ctk.CTkButton(self.root, text="Unlock Keyboard", command=self.unlock_keyboard, font=("Helvetica", 16))
        self.unlock_button.pack(pady=10)

        self.shortcut_label = ctk.CTkLabel(self.root, text=f"Lock: {self.lock_hotkey.upper()} | Unlock: {self.unlock_hotkey.upper()}", font=("Helvetica", 14))
        self.shortcut_label.pack(pady=10)

        self.edit_hotkey_button = ctk.CTkButton(self.root, text="Edit Hotkeys", command=self.set_shortcuts, font=("Helvetica", 15))
        self.edit_hotkey_button.pack(pady=10)

    def show_typing_animation(self):
        messages = ["Starting Secure Locker...", "Loading Modules...", "Ready to Lock & Secure!"]
        def animate():
            for msg in messages:
                displayed = ""
                for char in msg:
                    displayed += char
                    self.status_label.configure(text=displayed)
                    self.root.update()
                    time.sleep(0.05)
                time.sleep(0.5)
            self.status_label.configure(text="Status: 🔓 UNLOCKED")
        threading.Thread(target=animate, daemon=True).start()

    def register_hotkeys(self):
        keyboard.add_hotkey(self.lock_hotkey, self.lock_keyboard)
        keyboard.add_hotkey(self.unlock_hotkey, self.unlock_keyboard)

    def lock_keyboard(self):
        if self.is_locked:
            return
        self.is_locked = True
        self.status_label.configure(text="Status: 🔒 LOCKED")
        threading.Thread(target=self.safe_block_loop, daemon=True).start()

    def unlock_keyboard(self):
        self.is_locked = False
        self.status_label.configure(text="Status: 🔓 UNLOCKED")
        keyboard.unhook_all()
        self.register_hotkeys()

    def safe_block_loop(self):
        block_keys = list('abcdefghijklmnopqrstuvwxyz0123456789') + ['space', 'enter', 'tab', 'backspace', 'caps lock']
        while self.is_locked:
            for key in block_keys:
                if not any(k in key for k in self.safe_keys):
                    keyboard.block_key(key)
            if self.mouse_var.get():
                self.mouse_controller.position = (700, 400)
            time.sleep(0.1)

    def set_shortcuts(self):
        new_lock = simpledialog.askstring("Set Lock Hotkey", "Enter Lock Hotkey (Example: ctrl+alt+l):")
        new_unlock = simpledialog.askstring("Set Unlock Hotkey", "Enter Unlock Hotkey (Example: ctrl+alt+u):")
        if new_lock and new_unlock:
            try:
                keyboard.remove_hotkey(self.lock_hotkey)
                keyboard.remove_hotkey(self.unlock_hotkey)
                self.lock_hotkey = new_lock.lower()
                self.unlock_hotkey = new_unlock.lower()
                self.safe_keys = set(self.unlock_hotkey.split('+'))
                self.register_hotkeys()
                self.shortcut_label.configure(text=f"Lock: {self.lock_hotkey.upper()} | Unlock: {self.unlock_hotkey.upper()}")
            except Exception as e:
                print("Error:", e)

    def setup_tray(self):
        menu = (
            item('Lock', self.lock_keyboard),
            item('Unlock', self.unlock_keyboard),
            item('Edit Hotkeys', self.set_shortcuts),
            item('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("SecureLocker", self.logo, "Secure Locker", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def exit_app(self, icon=None, item=None):
        self.icon.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SecureLockerApp(root)
    app.register_hotkeys()
    root.mainloop()
