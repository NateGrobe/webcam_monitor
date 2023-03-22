import tkinter
from tkinter import *
from monitor import WebcamRegHandler
import time
from datetime import datetime
import chime
from utils import write_to_log
from utils import write_to_stats
import customtkinter
import cv2

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PopUp(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(self, text="LABEL")
        self.label.pack(padx=20, pady=20)

class App(customtkinter.CTk):
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

        self.check_unknownbtn = customtkinter.CTkButton(self.sidebar_frame, text="Scan for Hidden Programs", command=self.scan_cam)
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
        

        # Output log
        self.log_frame = customtkinter.CTkFrame(self, corner_radius=10, width=250, height=250)
        self.log_frame.grid(row=0, column=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.log_label = customtkinter.CTkLabel(self.log_frame, text="Output Log", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.log_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")
       
        self.log_list = customtkinter.CTkTextbox(self.log_frame, width=400, height=400, cursor=None, yscrollcommand=True, corner_radius=10)
        self.log_list.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")


        # Currently Active
        self.current_list_frame = customtkinter.CTkFrame(self, corner_radius=10, width=500, height=100)
        self.current_list_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.current_list_label = customtkinter.CTkLabel(self.current_list_frame, text="Currently Active", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.current_list_label.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="")

        self.current_list = customtkinter.CTkTextbox(self.current_list_frame, width=400, height=100, cursor=None, yscrollcommand=True, corner_radius=10)
        self.current_list.grid(row=1, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")

        
        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.active_tracker = {}
        self.access_counts = {}

        self.toplevel_window = None

        self.mainloop()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


    def toggle(self, cb):
        if cb == 'logging':
            self.logging_cb_state = bool(self.logging_cb_var.get())
        elif cb == 'sound':
            self.sound_cb_state = bool(self.sound_cb_var.get())

    def handle_start_stop(self):
        if not self.start:
            self.start = True
            self.startbtn.configure(text="Stop")
            self.start_monitor()
        else:
            self.start = True
            self.startbtn.configure(text="Start")

            self.stop_monitor()

    def start_monitor(self):
        self.start = True
        self.monitor()

    def stop_monitor(self):
        self.start = False


    def toggle_logging(self):
        self.logging_cb_state = not self.logging_cb_state

    def scan_cam(self):
        # _, c_active = WebcamRegHandler().getActiveApps()

        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = PopUp(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

        # if not len(c_active):
        #     cap = cv2.VideoCapture(0)
        #     ret, _ = cap.read()
        #     cap.release()

        #     if not ret:
        #         print("Unknown application found")
        #     else:
        #         print("No unknown applications found")

        # else:
        #     print("No unknown applications found")

        
    def monitor(self):
        if self.start:
            reg_handler = WebcamRegHandler()
            active, c_active = reg_handler.getActiveApps()
            self.active_list.delete('1.0',END)
            self.current_list.delete('1.0',END)
            # print("\n\nActive Apps:")
            for p in active:
                if p in self.active_tracker.keys():
                    time_active = time.time() - self.active_tracker[p]
                    log_str = f"{p} stopped after {time_active:.2f}s\n" 
                    write_to_log(log_str)
                    if bool(self.logging_cb_var.get()):

                        self.log_list.insert(END, f"\n{log_str}")
                    self.active_tracker.pop(p)
                    
                # print(p)
                self.active_list.insert(END,f"\n{p}")
                self.active_list.see(END)

            # print("\nCurrently Active App:")
            for p in c_active:
                if p not in self.active_tracker.keys():
                    # build log string
                    log_str = f"{p} started at {datetime.now()}\n"
                    write_to_log(log_str)

                    if p not in self.access_counts.keys():
                        self.access_counts.update({p : 0})
                    self.access_counts[p] = self.access_counts[p] + 1
                    stats = f"{p} accessed the webcam {self.access_counts[p]} times\n"
                    write_to_stats(stats)  
                    if bool(self.logging_cb_var.get()):
                        self.log_list.insert(END, f"\n{log_str}")
                        self.log_list.insert(END, f"{p} has accessed the webcam {self.access_counts[p]} times")
                    self.active_tracker[p] = time.time()
                    if bool(self.sound_cb_var.get()):
                        chime.success()
                    
                # print(p)
                self.current_list.insert(END, f"\n{c_active[0]}")
                self.current_list.see(END)  

            self.after(1000, self.monitor)


if __name__ == '__main__':
    # App(Tk())
    app = App()
    app.mainloop()