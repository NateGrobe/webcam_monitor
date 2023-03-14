from tkinter import *
from monitor import WebcamRegHandler
import time
from datetime import datetime
import chime

def write_to_log(log):
    with open("logs.txt", "a") as f:
        f.write(log)

class App:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam Monitor")

        self.start = False
        self.startbtn = Button(window, text='Start', height=2, width=10, command=self.start_monitor)
        self.startbtn.pack()

        self.stopbtn = Button(window, text='Stop', height=2, width=10, command=self.stop_monitor)
        self.stopbtn.pack()

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

            print("\n\nActive Apps:")
            for p in active:
                if p in self.active_tracker.keys():
                    time_active = time.time() - self.active_tracker[p]
                    log_str = f"{p} stopped after {time_active:.2f}s\n" 
                    write_to_log(log_str)
                    self.active_tracker.pop(p)
                print(p)

            print("\nCurrently Active App:")
            for p in c_active:
                if p not in self.active_tracker.keys():
                    log_str = f"{p} started at {datetime.now()}\n"
                    write_to_log(log_str)
                    self.active_tracker[p] = time.time()
                    chime.success()
                print(p)
            
            self.window.after(1000, self.monitor)




if __name__ == '__main__':
    App(Tk())