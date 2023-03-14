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
        self.header_font = "helvetica 12 bold"
        self.start = False
        self.startbtn = Button(window, text='Start', height=2, width=10, command=self.handle_start_stop, font=self.header_font)
        self.startbtn.grid(row=4, column=0)

        # self.stopbtn = Button(window, text='Stop', height=2, width=10, command=self.stop_monitor, font=self.header_font)
        # self.stopbtn.grid(row=2, column=1)

        
        self.active_label = Label(window, text="Apps with Access", width=50, font=self.header_font)
        self.active_label.grid(row=0, column=0)
        self.active_list = Text(window, height=20, width= 50, cursor=None, yscrollcommand=True)
        self.active_list.grid(row=1, column=0)

        
       
        self.current_label = Label(window, text="Currently Active", width=50, font=self.header_font)
        self.current_label.grid(row=2, column=0)
        self.current_list = Text(window, height=5, width= 50, cursor=None, yscrollcommand=True)
        self.current_list.grid(row=3, column=0)

        
        self.log_label = Label(window, text="Output Log", width=50, font=self.header_font)
        self.log_label.grid(row=0, column=1)
        self.log_list = Text(window, height=20, width= 50, cursor=None, yscrollcommand=True)
        self.log_list.grid(row=1, column=1)

        self.options_label = Label(window, text="Options", width=50, font=self.header_font)
        self.options_label.grid(row=2, column=1)
        self.options_frame = Frame(window)
        self.options_frame.grid(row=3, column=1)

        self.logging_cb_state = True
        self.logging_cb = Checkbutton(self.options_frame, text='Logging', variable=self.logging_cb_state, onvalue = True, offvalue=False, command=self.toggle_logging)
        self.logging_cb.grid(row=0,column=0)
        self.logging_cb.toggle()

        # self.logging_cb_state = True
        # self.logging_cb = Checkbutton(self.options_frame, text='', variable=self.logging_cb_state, onvalue = True, offvalue=False, command=self.toggle_logging)
        # self.logging_cb.grid(row=0,column=0)


        self.active_tracker = {}

        self.window.mainloop()

   

    def handle_start_stop(self):

        if not self.start:
            self.start = True
            self.startbtn.config(text="Stop")
            self.start_monitor()
        else:
            self.start = True
            self.startbtn.config(text="Start")
            self.stop_monitor()

    def start_monitor(self):
        self.start = True
        self.monitor()

    def stop_monitor(self):
        self.start = False


    def toggle_logging(self):
        self.logging_cb_state = not self.logging_cb_state
        
    def monitor(self):
        if self.start:
            reg_handler = WebcamRegHandler()
            active, c_active = reg_handler.getActiveApps()
            self.active_list.delete('1.0',END)
            self.current_list.delete('1.0',END)
            print("\n\nActive Apps:")
            for p in active:
                if p in self.active_tracker.keys():
                    time_active = time.time() - self.active_tracker[p]
                    log_str = f"{p} stopped after {time_active:.2f}s\n" 
                    write_to_log(log_str)
                    if self.logging_cb_state:
                        self.log_list.insert(END, f"\n{log_str}")
                    self.active_tracker.pop(p)
                    
                print(p)
                self.active_list.insert(END,f"\n{p}")
                self.active_list.see(END)
                

            print("\nCurrently Active App:")
            for p in c_active:
                if p not in self.active_tracker.keys():
                    log_str = f"{p} started at {datetime.now()}\n"
                    write_to_log(log_str)
                    if self.logging_cb_state:
                        self.log_list.insert(END, f"\n{log_str}")
                    self.active_tracker[p] = time.time()
                    chime.success()
                    
                print(p)
                self.current_list.insert(END, f"\n{c_active}")
                self.current_list.see(END)  
                
            
            self.window.after(1000, self.monitor)

if __name__ == '__main__':
    App(Tk())