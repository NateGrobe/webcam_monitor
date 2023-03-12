import winreg

class WebcamDetect:
    REG_KEY = winreg.HKEY_CURRENT_USER
    # WEBCAM_REG_SUBKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"
    WEBCAM_REG_SUBKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    WEBCAM_TIMESTAMP_VALUE_NAME = "LastUsedTimeStop"

    def __init__(self):
        self._regKey = winreg.OpenKey(WebcamDetect.REG_KEY, WebcamDetect.WEBCAM_REG_SUBKEY)

    def getActiveApps(self):
        activeApps = []
        currentlyActive = []

        subkeyCnt, valueCnt, lastModified = winreg.QueryInfoKey(self._regKey)
        print(subkeyCnt)

        for idx in range(subkeyCnt):
            subkeyName = winreg.EnumKey(self._regKey, idx)
            subkeyFullName = f"{WebcamDetect.WEBCAM_REG_SUBKEY}\\{subkeyName}"

            subkey = winreg.OpenKey(WebcamDetect.REG_KEY, subkeyFullName)
            try:
                ts, _ = winreg.QueryValueEx(subkey, WebcamDetect.WEBCAM_TIMESTAMP_VALUE_NAME)
                activeApps.append(subkeyName)

                if ts == 0:
                    currentlyActive.append(subkeyName)
            except:
                pass

                
        print("Apps with access:")
        for i in activeApps:
            print(i)

        print("\nCurrently active apps:")
        for i in currentlyActive:
            print(i)


        #     name = subkeyName.replace("#", "/")

        #     print(name, ts)

            # if ts == 0:
            #     print(subkeyName)




def main():
    wd = WebcamDetect()
    wd.getActiveApps()


if __name__ == '__main__':
    main()