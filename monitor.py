import winreg

class WebcamRegHandler:
    # define registry paths
    REG_KEY = winreg.HKEY_CURRENT_USER
    WEBCAM_REG_LIST = [
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam", 
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"
    ]

    def __init__(self):
        self._reg_keys = [winreg.OpenKey(WebcamRegHandler.REG_KEY, reg) for reg in WebcamRegHandler.WEBCAM_REG_LIST]
        self.active_apps = [] # apps with access to webcam
        self.c_active = [] # apps currently using webcam

    def findActiveApps(self):

        for reg_key, reg_path in zip(self._reg_keys, WebcamRegHandler.WEBCAM_REG_LIST):
            subkey_cnt, value_cnt, last_modified = winreg.QueryInfoKey(reg_key)

            for idx in range(subkey_cnt):
                subkey_name = winreg.EnumKey(reg_key, idx)
                subkey_full_name = f"{reg_path}\\{subkey_name}"
                subkey = winreg.OpenKey(WebcamRegHandler.REG_KEY, subkey_full_name)

                try:
                    ts, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStop")

                    if ts == 0:
                        self.c_active.append(subkey_name)
                    else:
                        self.active_apps.append(subkey_name)
                except:
                    pass

    def getActiveApps(self):
        return self.active_apps, self.c_active

# sample of how to use the class
if __name__ == '__main__':
    reg_handler = WebcamRegHandler()
    reg_handler.findActiveApps()
    active, c_active = reg_handler.getActiveApps()

    print("Active Apps:")
    for i in active:
        print(i)

    print("\nCurrently Active App:")
    for i in c_active:
        print(i)