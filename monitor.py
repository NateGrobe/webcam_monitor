import winreg

class WebcamDetect:
    REG_KEY = winreg.HKEY_CURRENT_USER
    WEBCAM_REG_SUBKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"
    WEBCAM_TIMESTAMP_VALUE_NAME = "LastUsedTimeStamp"

    def __init__(self):
        self._regKey = winreg.OpenKey(WebcamDetect.REG_KEY, WebcamDetect.WEBCAM_REG_SUBKEY)

    def getActiveApps(self):
        activeApps = []

        subkeyCtn, valueCnt, lastModified = winreg.QueryInfoKey(self._regKey)

        print(subkeyCtn)
        print(valueCnt)
        print(lastModified)



def main():
    wd = WebcamDetect()
    wd.getActiveApps()


if __name__ == '__main__':
    main()