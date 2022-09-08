import win32serviceutil  # ServiceFramework and commandline helper
import win32service  # Events
import servicemanager  # Simple setup and logging

from rtlc import CopyUtility, getLenSysArg
from smbclient import SmbClient


class CopyUtilityNetShare(CopyUtility):

    def __init__(self):
        super().__init__()
        self.conn = SmbClient(self.config.shareIP, self.config.userName,
                              self.config.userPassword, self.config.shareName,
                              self.config.clientMachineName,
                              self.config.remoteMachineName)
        self.log.info(self.conn.connect())

    def copyfile(self, path, filename):
        return self.conn.copyfile(path, filename)

    def scandir(self, path: str):
        self.conn.scandir(path, self.timeStamp, self.remoteList)


class MyService:

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        servicemanager.LogInfoMsg('Service started.')

        if 1 == 1:  #rtlc.config.useNetShare:
            rtlc = CopyUtilityNetShare()
        else:
            rtlc = CopyUtility()

        while self.running:
            rtlc.walker()
            rtlc.timeout()


class MyServiceFramework(win32serviceutil.ServiceFramework):

    _svc_name_ = 'RTLC'
    _svc_display_name_ = 'Remote To Local Copy'

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = MyService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.service_impl.run()


if __name__ == '__main__':
    if getLenSysArg() == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyServiceFramework)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyServiceFramework)