import win32serviceutil  # ServiceFramework and commandline helper
import win32service  # Events
import servicemanager  # Simple setup and logging

from rtlc import CopyUtility, getLenSysArg


class MyService:

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        rtlc = CopyUtility()
        rtlc.log.info('Service started.')
        servicemanager.LogInfoMsg('Service started.')
        while self.running:
            rtlc.copyfiles()
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