from typing import Any, Callable, Optional, Tuple, Union
from tkinter import IntVar
import customtkinter
from win32gui import GetForegroundWindow
import win32process
import psutil
from facereader import FaceReader
import threading


class App(customtkinter.CTk):
    VALID_APPS = ["chrome", "code"]
    APP_TITLE = "Study Doctor"
    APP_SCREEN_SIZE = "400x400"

    def __init__(
        self, fg_color: str | Tuple[str, str] | None = None, **kwargs
    ):
        super().__init__(fg_color, **kwargs)
        self.title(self.APP_TITLE)
        self.geometry(self.APP_SCREEN_SIZE)
        self.tabview = Tabs(master=self)
        self.tabview.pack()

class Help(customtkinter.CTkToplevel):
    SCREEN_TITLE = "Help - Study Doctor"
    APP_SCREEN_SIZE = "400x400"

    def __init__(
        self, *args, fg_color: str | Tuple[str, str] | None = None, **kwargs
    ):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.after(0, self.lift)
        self.title(self.SCREEN_TITLE)
        self.geometry(self.APP_SCREEN_SIZE)
        self.label = customtkinter.CTkLabel(self, text="Help")
        self.label.pack()
        self.close_button = customtkinter.CTkButton(
            self, text="Close", command=self.onclick_close
        )
        self.close_button.pack()

    def onclick_close(self):
        self.destroy()

class Tabs(customtkinter.CTkTabview):
    def __init__(self, master: Any, width: int = 300, height: int = 250, corner_radius: int | None = None, border_width: int | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, segmented_button_fg_color: str | Tuple[str, str] | None = None, segmented_button_selected_color: str | Tuple[str, str] | None = None, segmented_button_selected_hover_color: str | Tuple[str, str] | None = None, segmented_button_unselected_color: str | Tuple[str, str] | None = None, segmented_button_unselected_hover_color: str | Tuple[str, str] | None = None, text_color: str | Tuple[str, str] | None = None, text_color_disabled: str | Tuple[str, str] | None = None, command: Callable[..., Any] | Any = None, anchor: str = "center", state: str = "normal", **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, segmented_button_fg_color, segmented_button_selected_color, segmented_button_selected_hover_color, segmented_button_unselected_color, segmented_button_unselected_hover_color, text_color, text_color_disabled, command, anchor, state, **kwargs)
        
        self.add("Main")
        self.add("Timer")
        self.main_screen = MainScreen(master=self.tab("Main"))
        self.main_screen.pack()
        self.timer_screen = TimerScreen(master=self.tab("Timer"))
        self.timer_screen.pack()

class MainScreen(customtkinter.CTkFrame):
    VALID_APPS = ["chrome", "code"]
    
    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.label = customtkinter.CTkLabel(self, text="")
        self.label.pack()
        self.get_current_app()
        self.session_count = IntVar(value=1)
        self.timer_count = IntVar(value=20)
        self.timer_count_label = customtkinter.CTkLabel(self, text=f"Timer: {self.timer_count.get()} mins")
        self.timer_count_label.pack()
        self.timer_slider = customtkinter.CTkSlider(self, from_=15, to=35, variable=self.timer_count, number_of_steps=20, command=self.onchange_timer_slider)
        self.timer_slider.pack()
        self.session_count_label = customtkinter.CTkLabel(self, text=f"Session Count: {self.session_count.get()}")
        self.session_count_label.pack()
        self.session_slider = customtkinter.CTkSlider(self, from_=1, to=10, variable=self.session_count, number_of_steps=9, command=self.onchange_session_slider)
        self.session_slider.pack()
        self.start_button = customtkinter.CTkButton(self, text="Start", command=self.onclick_start)
        self.start_button.pack()
        self.help_button = customtkinter.CTkButton(
            self, text="Help", command=self.onclick_help
        )
        self.help_button.pack()
        self.help_window = None
        self.face_reader = FaceReader()
    
    def onchange_timer_slider(self, value):
        self.timer_count = int(value)
        self.timer_count_label.configure(text=f"Timer: {self.timer_count} mins")
    
    def onchange_session_slider(self, value):
        self.session_count = int(value)
        self.session_count_label.configure(text=f"Session Count: {self.session_count}")
    
    def get_current_app(self):
        pid = win32process.GetWindowThreadProcessId(GetForegroundWindow())
        process_name = psutil.Process(pid[-1]).name().split(".")[0].lower()
        # print(process_name)

        if process_name in self.VALID_APPS:
            self.label.configure(text=process_name)
        else:
            self.label.configure(text="DO YOUR WORK!")
        self.after(2000, self.get_current_app)

    def onclick_start(self):
        # t = threading.Thread(target=self.face_reader.data_collection)
        # t.start()
        
        app.tabview.set("Timer")

    def onclick_help(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = Help(
                self
            )  # create window if its None or destroyed
            self.help_window.after(10, self.help_window.lift)
        else:
            self.help_window.focus()  # if window exists focus it

class TimerScreen(customtkinter.CTkFrame):
    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.label = customtkinter.CTkLabel(self, text="Timer Screen")
        self.label.pack()

app = App()
app.mainloop()
