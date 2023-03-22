import winreg
import time
import os
from datetime import datetime

class WebcamRegHandler:
    # define registry paths
    REG_KEY = winreg.HKEY_CURRENT_USER
    WEBCAM_REG_LIST = [
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam", 
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"
    ]

    def __init__(self):
        self._reg_keys = [winreg.OpenKey(WebcamRegHandler.REG_KEY, reg) for reg in WebcamRegHandler.WEBCAM_REG_LIST]

    def format_program_name(self, p_name):
        if "C:" in p_name:
            return p_name.split("#")[-1].split(".")[0]
        
        if "Python" in p_name:
            return p_name
        return p_name.split(".")[-1].split("_")[0]

    def findActiveApps(self):
        self.active_tmp = []
        self.active_apps = [] # apps with access to webcam
        self.c_active = [] # apps currently using webcam
        for reg_key, reg_path in zip(self._reg_keys, WebcamRegHandler.WEBCAM_REG_LIST):
            subkey_cnt, value_cnt, last_modified = winreg.QueryInfoKey(reg_key)

            for idx in range(subkey_cnt):
                subkey_name = winreg.EnumKey(reg_key, idx)
                subkey_full_name = f"{reg_path}\\{subkey_name}"
                subkey = winreg.OpenKey(WebcamRegHandler.REG_KEY, subkey_full_name)

                try:
                    ts, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStop")
                    formatted_name = self.format_program_name(subkey_name)
                    if ts == 0:
                        self.c_active.append(formatted_name)
                    else:
                        self.active_tmp.append(formatted_name)
                except:
                    pass

        app_count = {}
        for a in self.active_tmp:
            if a not in app_count.keys():
                app_count[a] = 1
            else:
                app_count[a] += 1

        for k in app_count.keys():
            if app_count[k] > 1:
                self.active_apps.append(f"{k} ({app_count[k]})")
            else:
                self.active_apps.append(k)

    def getActiveApps(self):
        self.findActiveApps()
        return self.active_apps, self.c_active

if __name__ == '__main__':
    active_tracker = {}

    while True:
        reg_handler = WebcamRegHandler()
        active, c_active = reg_handler.getActiveApps()

        print("\n\nActive Apps:")
        for p in active:
            if p in active_tracker.keys():
                time_active = time.time() - active_tracker[p]
                log_str = f"{p} stopped after {time_active:.2f}s\n" 
                print(log_str)
                active_tracker.pop(p)
            print(p)

        print("\nCurrently Active App:")
        for i in c_active:
            if p not in active_tracker.keys():
                log_str = f"{p} started at {datetime.now()}\n"
                print(log_str)
                active_tracker[p] = time.time()
            print(p)

        time.sleep(1)