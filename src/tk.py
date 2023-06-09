import tkinter
from tkinter import *
from monitor import WebcamRegHandler
import time
from datetime import datetime
import chime
from utils import Logging
import customtkinter
import cv2

# some visual config stuff
customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# popup class logic
class FoundPopUp(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("300x100")

        self.label = customtkinter.CTkLabel(self, text="Unknown application found!")
        self.label.pack(padx=20, pady=20)

# popup class logic
class NotFoundPopUp(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("300x100")

        self.label = customtkinter.CTkLabel(self, text="No unknown applications found!")
        self.label.pack(padx=20, pady=20)

class App(customtkinter.CTk):
    # initialize UI layout
    def __init__(self):
        super().__init__()

        self.start = False
        self.logging_cb_state = True
        self.sound_cb_state = True

        # configure window
        self.title("Webcam Monitor")
        self.geometry(f"{1100}x{725}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets  OPTIONS COL
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Options", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
       
        # START BUTTON
        self.startbtn = customtkinter.CTkButton(self.sidebar_frame, text="Start Monitor", command=self.handle_start_stop)
        self.startbtn.grid(row=1, column=0, padx=20, pady=10)

        self.check_unknownbtn = customtkinter.CTkButton(self.sidebar_frame, text="Scan for\nHidden Programs", command=self.scan_cam)
        self.check_unknownbtn.grid(row=3, column=0, padx=20, pady=10)

        # Logging
        self.logging_cb_var = IntVar()
        self.logging_cb = customtkinter.CTkCheckBox(self.sidebar_frame, text="Logging", variable=self.logging_cb_var, onvalue=1, offvalue=0, command=lambda: self.toggle('logging'))
        self.logging_cb.grid(row=1, column=0, pady=(100, 0), padx=20, sticky="n")
        self.logging_cb.select()

        self.sound_cb_var = IntVar()
        self.sound_cb = customtkinter.CTkCheckBox(self.sidebar_frame, text="Sound", variable=self.sound_cb_var, onvalue=1, command=lambda: self.toggle('sound'))
        self.sound_cb.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        self.sound_cb.select()
       
        # LIGHT AND DARK MODE ETC
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))


        # Widgets
        # Apps with access
        self.active_list_frame = customtkinter.CTkFrame(self, corner_radius=10, width=500, height=250)
        self.active_list_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.active_list_label = customtkinter.CTkLabel(self.active_list_frame, text="Apps with access", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.active_list_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")
       
        self.active_list = customtkinter.CTkTextbox(self.active_list_frame, width=400, height=400, cursor=None, yscrollcommand=True, corner_radius=10)
        self.active_list.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.active_list.configure(state='disabled')
        

        # Output log
        self.log_frame = customtkinter.CTkFrame(self, corner_radius=10, width=250, height=250)
        self.log_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.log_label = customtkinter.CTkLabel(self.log_frame, text="Output Log", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.log_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")
       
        self.log_list = customtkinter.CTkTextbox(self.log_frame, width=400, height=400, cursor=None, yscrollcommand=True, corner_radius=10)
        self.log_list.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.log_list.configure(state='disabled')

        # Currently Active
        self.current_list_frame = customtkinter.CTkFrame(self, corner_radius=10, width=500, height=100)
        self.current_list_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.current_list_label = customtkinter.CTkLabel(self.current_list_frame, text="Currently Active", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.current_list_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")

        self.current_list = customtkinter.CTkTextbox(self.current_list_frame, width=400, height=100, cursor=None, yscrollcommand=True, corner_radius=10)
        self.current_list.grid(row=1, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.current_list.configure(state='disabled')

        
        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.active_tracker = {}
        self.access_counts = {}

        self.toplevel_window = None

        self.populate_log()

        self.mainloop()

    # updates appearance on change
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # writes to log file
    def populate_log(self):
        try:
            with open("logs.txt") as f:
                self.update_log_list(f.read())
        except:
            pass

    # updates log field in UI
    def update_log_list(self, str):
        self.log_list.configure(state='normal')
        self.log_list.insert(END, f"\n{str}")
        self.log_list.configure(state='disabled')


    # toggles alert options
    def toggle(self, cb):
        if cb == 'logging':
            self.logging_cb_state = bool(self.logging_cb_var.get())
        elif cb == 'sound':
            self.sound_cb_state = bool(self.sound_cb_var.get())

    # event handler for start and stop button
    def handle_start_stop(self):
        if not self.start:
            self.start = True
            self.startbtn.configure(text="Stop")
            self.start_monitor()
        else:
            self.start = True
            self.startbtn.configure(text="Start")

            self.stop_monitor()

    # starts the main loop of the monitor
    def start_monitor(self):
        self.start = True
        self.monitor()

    # stops the main loop
    def stop_monitor(self):
        self.start = False


    # toggles loggin on and off
    def toggle_logging(self):
        self.logging_cb_state = not self.logging_cb_state

    # checks if camera is being used as redundancy
    def scan_cam(self):
        _, c_active = WebcamRegHandler().getActiveApps()

        if not len(c_active):
            cap = cv2.VideoCapture(0)
            ret, _ = cap.read()
            cap.release()

            if not ret:
                if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                    self.toplevel_window = FoundPopUp(self)  # create window if its None or destroyed
                else:
                    self.toplevel_window.focus()  # if window exists focus it
            else:
                if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                    self.toplevel_window = NotFoundPopUp(self)  # create window if its None or destroyed
                else:
                    self.toplevel_window.focus()  # if window exists focus it
        else:
            if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
                self.toplevel_window = NotFoundPopUp(self)  # create window if its None or destroyed
            else:
                self.toplevel_window.focus()  # if window exists focus it

        
    # main monitor functoin
    def monitor(self):
        if self.start:
            # query registry
            reg_handler = WebcamRegHandler()
            active, c_active = reg_handler.getActiveApps()

            # clear the active and inactive app lists for new info
            self.active_list.configure(state='normal')
            self.current_list.configure(state='normal')
            self.active_list.delete('1.0',END)
            self.current_list.delete('1.0',END)
            self.active_list.configure(state='disabled')
            self.current_list.configure(state='disabled')

            # inactive application logic
            for p in active:
                if p in self.active_tracker.keys():
                    time_active = time.time() - self.active_tracker[p]
                    log_str = f"{p} stopped after {time_active:.2f}s\n" 
                    Logging.write_to_log(log_str)
                    if bool(self.logging_cb_var.get()):
                        self.update_log_list(log_str)

                    self.active_tracker.pop(p)
                    
                # update active list
                self.active_list.configure(state='normal')
                self.active_list.insert(END,f"\n{p}")
                self.active_list.see(END)
                self.active_list.configure(state='disabled')

            # active app logic
            for p in c_active:
                if p not in self.active_tracker.keys():
                    # build log string
                    log_str = f"{p} started at {datetime.now()}\n"
                    Logging.write_to_log(log_str)

                    if p not in self.access_counts.keys():
                        self.access_counts.update({p : 0})

                    self.access_counts[p] = self.access_counts[p] + 1
                    stats = f"{p} accessed the webcam {self.access_counts[p]} times\n"
                    Logging.write_to_stats(stats)  

                    # checks for logging toggle to be active
                    if bool(self.logging_cb_var.get()):
                        self.update_log_list(f"\n{log_str}")
                        self.update_log_list(f"{p} has accessed the webcam {self.access_counts[p]} times")

                    self.active_tracker[p] = time.time()
                    # checks for sound alert toggle to be active
                    if bool(self.sound_cb_var.get()):
                        chime.success()
                    
                self.current_list.configure(state='normal')
                self.current_list.insert(END, f"\n{c_active[0]}")
                self.current_list.see(END)  
                self.current_list.configure(state='disabled')

            # executes once per second
            self.after(1000, self.monitor)


if __name__ == '__main__':
    app = App()
    app.mainloop()