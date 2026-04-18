"""Mindful Work — Smart Stress Relief Pod Companion App.

Entry point for the FutureForward Wellness desktop application.
Run with: python main.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk

# Let CustomTkinter use whatever the system theme is (light or dark)
ctk.set_default_color_theme("blue")

from controllers.app_controller import AppController
from views.theme import Theme
from views.login_screen import LoginScreen
from views.home_screen import HomeScreen
from views.stress_check_screen import StressCheckScreen
from views.pod_customization_screen import PodCustomizationScreen
from views.active_session_screen import ActiveSessionScreen
from views.feedback_screen import FeedbackScreen


class MindfulWorkApp(ctk.CTk):
    """Main application window managing all screens and navigation."""

    APP_TITLE = "Mindful Work — Smart Stress Relief Pod"
    MIN_WIDTH = 480
    MIN_HEIGHT = 720

    def __init__(self) -> None:
        super().__init__()

        self.title(self.APP_TITLE)
        self.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.minsize(self.MIN_WIDTH, 600)
        self.configure(fg_color=Theme.BACKGROUND)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.MIN_WIDTH) // 2
        y = (self.winfo_screenheight() - self.MIN_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.controller = AppController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.screens: dict[str, ctk.CTkFrame] = {}
        self._current_screen: str = ""

        screen_classes = {
            "login": LoginScreen,
            "home": HomeScreen,
            "stress_check": StressCheckScreen,
            "pod_customization": PodCustomizationScreen,
            "active_session": ActiveSessionScreen,
            "feedback": FeedbackScreen,
        }

        for name, ScreenClass in screen_classes.items():
            screen = ScreenClass(self, self.controller)
            screen.parent_app = self
            self.screens[name] = screen

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_screen("login")

    def show_screen(self, name: str) -> None:
        if name not in self.screens:
            return
        if self._current_screen and self._current_screen in self.screens:
            current = self.screens[self._current_screen]
            if hasattr(current, "on_hide"):
                current.on_hide()
            current.grid_forget()

        target = self.screens[name]
        target.grid(row=0, column=0, sticky="nsew")
        if hasattr(target, "on_show"):
            target.on_show()
        self._current_screen = name

    def _on_close(self) -> None:
        if self.controller.is_session_running:
            confirm = messagebox.askyesno(
                "Session Active",
                "A session is still running. Ending now will save your "
                "partial progress.\n\nAre you sure you want to exit?",
                icon="warning",
            )
            if not confirm:
                return
        self.controller.cleanup()
        self.destroy()


def main() -> None:
    app = MindfulWorkApp()
    app.mainloop()


if __name__ == "__main__":
    main()
