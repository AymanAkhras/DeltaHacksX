import customtkinter
from win32gui import GetForegroundWindow
import win32process
import psutil

VALID_APPS = ["chrome", "code"]
APP_TITLE = "Study Doctor"
APP_SCREEN_SIZE = "1280x720"
app = customtkinter.CTk()
app.title(APP_TITLE)
app.geometry(APP_SCREEN_SIZE)

def get_current_app():
    pid = win32process.GetWindowThreadProcessId(GetForegroundWindow())
    process_name = psutil.Process(pid[-1]).name().split(".")[0].lower()
    print(process_name)
    
    if process_name in VALID_APPS:
        label.configure(text=process_name)
    else:
        label.configure(text="DO YOUR WORK!")
    app.after(2000, get_current_app)

label = customtkinter.CTkLabel(app, text="")
label.pack()
get_current_app()

app.mainloop()