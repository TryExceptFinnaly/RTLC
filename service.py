import win32serviceutil  # ServiceFramework and commandline helper
import win32service  # Events
import servicemanager  # Simple setup and logging

from rtlc import CopyUtility, getLenSysArg
from smbclient import SmbClient


class CopyUtilityNetShare(CopyUtility):

    def __init__(self):
        super().__init__()
        self.shareIP = self.config.shareIP
        self.shareName = self.config.shareName

        if not self.config.remoteMachineName:
            result, msg = SmbClient.getBIOSName(self)
            if result:
                self.config.remoteMachineName = msg
                self.log.info(
                    f"Getting hostname by IP '{self.shareIP}' successfully: '{msg}'"
                )
                self.config.save()
            else:
                self.log.error(
                    f"Error getting hostname by IP '{self.shareIP}': {msg}")
                self.exit()

    def connect(self):
        self.server = SmbClient.create(self.config.userName,
                                       self.config.userPassword,
                                       self.config.clientMachineName,
                                       self.config.remoteMachineName)
        connect, msg = SmbClient.connect(self)
        if connect:
            self.log.info(msg)
        else:
            self.log.error(msg)
            self.close()
            self.timeout()
            self.connect()

    def close(self):
        SmbClient.close(self)

    def echo(self):
        return SmbClient.echo(self)

    def copyfile(self, path, filename):
        return SmbClient.copyfile(self, path, filename)

    def scandir(self, path):
        if not self.echo():
            self.log.error('Echo request failed, reconnect...')
            self.close()
            self.timeout()
            self.connect()
        SmbClient.scandir(self, path)


class MyService:

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        useNetShare = CopyUtility.getUseNetShare()

        if useNetShare:
            rtlc = CopyUtilityNetShare()
            rtlc.connect()
        else:
            rtlc = CopyUtility()

        servicemanager.LogInfoMsg('Service started successfully.')

        while self.running:
            rtlc.walker()
            rtlc.timeout()


class MyServiceFramework(win32serviceutil.ServiceFramework):

    _svc_name_ = 'RTLC'
    _svc_display_name_ = 'Remote To Local Copy'
    _svc_description_ = 'Remote To Local Copy files utility'

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
    # if getLenSysArg() == 1:
    #     servicemanager.Initialize()
    #     servicemanager.PrepareToHostSingle(MyServiceFramework)
    #     servicemanager.StartServiceCtrlDispatcher()
    # else:
    #     win32serviceutil.HandleCommandLine(MyServiceFramework)
    rtlc = MyService()
    rtlc.run()