from tkinter import *
from monitor import WebcamRegHandler
import time
from datetime import datetime
import chime
from utils import write_to_log

class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam Monitor")

        # create Active Apps label and listbox
        self.active_label = Label(window, text="Active Apps")
        self.active_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.active_list = Listbox(window, width=50)
        self.active_list.grid(row=1, column=0, padx=10, pady=10)

        # create Currently Active App label and listbox
        self.c_active_label = Label(window, text="Currently Active App")
        self.c_active_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.c_active_list = Listbox(window, width=50)
        self.c_active_list.grid(row=1, column=1, padx=10, pady=10)

        # create Start and Stop buttons
        self.startbtn = Button(window, text='Start', height=2, width=10, command=self.start_monitor)
        self.startbtn.grid(row=2, column=0, padx=10, pady=10)

        self.stopbtn = Button(window, text='Stop', height=2, width=10, command=self.stop_monitor)
        self.stopbtn.grid(row=2, column=1, padx=10, pady=10)

        self.active_tracker = {}

        self.window.mainloop()

    def start_monitor(self):
        self.start = True
        self.monitor()

    def stop_monitor(self):
        self.start = False

    def monitor(self):
        if self.start:
            reg_handler = WebcamRegHandler()
            active, c_active = reg_handler.getActiveApps()

            self.active_list.delete(0, END)
            self.c_active_list.delete(0, END)

            for p in active:
                if p in self.active_tracker.keys():
                    time_active = time.time() - self.active_tracker[p]
                    log_str = f"{p} stopped after {time_active:.2f}s\n" 
                    write_to_log(log_str)
                    self.active_tracker.pop(p)
                self.active_list.insert(END, p)

            for p in c_active:
                if p not in self.active_tracker.keys():
                    log_str = f"{p} started at {datetime.now()}\n"
                    write_to_log(log_str)
                    self.active_tracker[p] = time.time()
                    chime.success()
                self.c_active_list.insert(END, p)
            
            self.window.after(1000, self.monitor)

if __name__ == '__main__':
    App(Tk())