#Remote To Local Copy(RTLC)
import logging
import logging.handlers
import os
import shutil
import sys

from uuid import uuid4
from time import sleep, mktime, strptime, strftime, gmtime

from config import Config


def getModulePath() -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)


def getLenSysArg() -> int:
    return len(sys.argv)


class CopyUtility():

    def __init__(self):
        os.chdir(getModulePath())

        self.config = Config('config.ini')
        self.config.load()

        FORMAT = '[%(asctime)s]: %(levelname)s - %(message)s'
        FOLDER_LOGS = 'Logs'
        NAME_LOG = 'rtlc.log'

        if not os.path.exists(FOLDER_LOGS):
            try:
                os.mkdir(FOLDER_LOGS)
            except Exception as exc:
                print(
                    f'[RTLC ERROR]: Failed to create log directory: "{os.path.abspath(FOLDER_LOGS)}"'
                )
                print(f'{exc}')
                sys.exit()

        logging.basicConfig(handlers='')

        SIZE_LOG = self.config.logsSize * 1024 * 1024

        mainHandler = logging.handlers.RotatingFileHandler(
            f'{FOLDER_LOGS}/{NAME_LOG}',
            maxBytes=SIZE_LOG,
            backupCount=self.config.logsBackups,
            encoding='utf-8')
        mainHandler.setFormatter(logging.Formatter(FORMAT))

        self.log = logging.getLogger('rltc')
        self.log.addHandler(mainHandler)

        self.config.logsLevel = self.config.logsLevel.upper()
        if self.config.logsLevel not in [
                'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ]:
            self.log.error(
                f'Uncorrect logging level: "{self.config.logsLevel}". Available values: "NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL".'
            )
            sys.exit()

        self.log.setLevel(self.config.logsLevel)
        self.log.info('Starting service...')

        if not os.path.exists(self.config.ini):
            self.log.warning(
                f'File "{self.config.ini}" not found, modify the generated config file ("{os.path.abspath(self.config.ini)}").'
            )
            result = self.config.save()
            print(result)
            sys.exit()

        self.config.save()

        self.remotePath = self.config.remotePath
        self.localPath = self.config.localPath

        notPath = False

        if not os.path.exists(self.remotePath):
            self.log.error(f'Remote folder "{self.remotePath}" not found.')
            notPath = True

        if not os.path.exists(self.localPath):
            self.log.error(f'Local folder "{self.localPath}" not found.')
            notPath = True

        if notPath:
            sys.exit()

        self.refreshTime = self.config.refreshTime
        self.timeStamp = self.config.timeStamp
        self.extensionFile = tuple(
            self.config.extensionFile.replace(' ', '').split(','))

        self.log.info(f'Logs level: {self.config.logsLevel}')
        self.log.info(f'Remote folder: "{self.remotePath}"')
        self.log.info(f'Local folder: "{self.localPath}"')
        self.log.info(f'Refresh time: {self.refreshTime}')
        self.log.info(f'Extension file: {self.extensionFile}')
        self.log.info(f'Start date: {self.config.startDate}')
        self.log.info(
            f'Last file: {strftime("%Y-%m-%d %H:%M:%S", gmtime(self.timeStamp))} (timeStamp: {self.timeStamp})'
        )

        if not self.timeStamp:
            try:
                self.timeStamp = mktime(
                    strptime(self.config.startDate, '%Y-%m-%d %H:%M'))
            except ValueError:
                self.log.error(
                    f'Uncorrect start date: "{self.config.startDate}", correct format: "2000-01-01 00:00"'
                )
                sys.exit()

        self.remoteList = []

    def scandir(self, path: str):
        with os.scandir(path) as scanDir:
            for entry in scanDir:
                if entry.is_dir(follow_symlinks=False):
                    self.scandir(entry.path)
                elif entry.is_file(
                        follow_symlinks=False) and entry.name.endswith(
                            self.extensionFile) and (entry.stat().st_ctime >
                                                     self.timeStamp):
                    self.remoteList.append((entry.stat().st_ctime, entry.path))

    def copyfiles(self):
        self.log.info(f'Refresh')
        self.scandir(self.remotePath)
        self.remoteList = sorted(self.remoteList)
        self.log.info(f'Found {len(self.remoteList)} files to copy.')
        if self.remoteList:
            self.timeStamp = self.remoteList[-1][0]
            for file in self.remoteList[:]:  # перебрать копию списка
                try:
                    newName = f'{uuid4()}{os.path.splitext(file[1])[1]}'
                    shutil.copy2(f'{file[1]}', f'{self.localPath}/{newName}')
                    self.log.info(
                        f'File "{newName} << {file[1]}" "{strftime("%Y-%m-%d %H:%M:%S", gmtime(file[0]))} ({file[0]})" copied to local folder.'
                    )
                    self.remoteList.remove(file)
                except Exception as exc:
                    self.log.error(
                        f"File '{file[1]}' not copied to local folder: {exc}")
            self.config.timeStamp = self.timeStamp
            self.config.save()

    def timeout(self):
        sleep(self.refreshTime)


if __name__ == '__main__':
    rtlc = CopyUtility()
    rtlc.log.info('Service started.')
    while True:
        rtlc.copyfiles()
        rtlc.timeout()