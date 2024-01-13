from typing import Optional, Tuple, Union
from tkinter import IntVar
import customtkinter
from win32gui import GetForegroundWindow
import win32process
import psutil

class App(customtkinter.CTk):
    VALID_APPS = ["chrome", "code"]
    APP_TITLE = "Study Doctor"
    APP_SCREEN_SIZE = "400x400"
    
    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.title(self.APP_TITLE)
        self.geometry(self.APP_SCREEN_SIZE)
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
        self.help_button = customtkinter.CTkButton(self, text="Help", command=self.onclick_help)
        self.help_button.pack()
        self.help_window = None
    
    def onchange_timer_slider(self, value):
        self.timer_count = int(value)
        self.timer_count_label.configure(text=f"Timer: {self.timer_count} mins")
    
    def onchange_session_slider(self, value):
        self.session_count = int(value)
        self.session_count_label.configure(text=f"Session Count: {self.session_count}")
    
    def get_current_app(self):
        pid = win32process.GetWindowThreadProcessId(GetForegroundWindow())
        process_name = psutil.Process(pid[-1]).name().split(".")[0].lower()
        print(process_name)
        
        if process_name in self.VALID_APPS:
            self.label.configure(text=process_name)
        else:
            self.label.configure(text="DO YOUR WORK!")        
        self.after(2000, self.get_current_app)
    
    def onclick_start(self):
        print("start button was clicked")

    def onclick_help(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.help_window = Help(self)  # create window if its None or destroyed
            self.help_window.after(10, self.help_window.lift)
        else:
            self.help_window.focus()  # if window exists focus it

class Help(customtkinter.CTkToplevel):
    SCREEN_TITLE = "Help - Study Doctor"
    APP_SCREEN_SIZE = "400x400"
    def __init__(self, *args, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.after(0, self.lift)
        self.title(self.SCREEN_TITLE)
        self.geometry(self.APP_SCREEN_SIZE)
        self.label = customtkinter.CTkLabel(self, text="Help")
        self.label.pack()
        self.close_button = customtkinter.CTkButton(self, text="Close", command=self.onclick_close)
        self.close_button.pack()
    
    def onclick_close(self):
        self.destroy()

app = App()
app.mainloop()