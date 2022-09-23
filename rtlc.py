# Remote To Local Copy(RTLC)
import logging
import logging.handlers
import os
import shutil
import sys
import atexit
import threading

from uuid import uuid4
from time import sleep, mktime, strptime, strftime, gmtime

from config import Config

FORMAT = '[%(asctime)s]: %(levelname)s - %(message)s'


def getModulePath() -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)


def getLenSysArg() -> int:
    return len(sys.argv)


class CopyUtility():

    def __init__(self, name):
        os.chdir(getModulePath())

        FOLDER_LOGS = 'Logs'
        CONFIG_NAME = f'{name}.ini'
        NAME_LOG = f'{name}.log'
        NAME_QUEUE = f'{name}.queue'

        if not os.path.exists(FOLDER_LOGS):
            try:
                os.mkdir(FOLDER_LOGS)
            except Exception as exc:
                print(
                    f'[RTLC ERROR]: Failed to create log directory: "{os.path.abspath(FOLDER_LOGS)}"'
                )
                print(f'{exc}')
                self.exit()

        self.config = Config(CONFIG_NAME)
        self.config.load()

        SIZE_LOG = self.config.logsSize * 1024 * 1024

        logging.basicConfig(handlers='')

        self.mainHandler = logging.handlers.RotatingFileHandler(
            f'{FOLDER_LOGS}/{NAME_LOG}',
            maxBytes=SIZE_LOG,
            backupCount=self.config.logsBackups,
            encoding='utf-8')
        self.mainHandler.setFormatter(logging.Formatter(FORMAT))

        self.log = logging.getLogger(name)
        self.log.addHandler(self.mainHandler)

        self.config.logsLevel = self.config.logsLevel.upper()
        if self.config.logsLevel not in [
                'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ]:
            self.log.error(
                f'Uncorrect logging level: "{self.config.logsLevel}". Available values: "NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL".'
            )
            self.exit()

        self.log.setLevel(self.config.logsLevel)
        self.log.info('Starting service...')

        if not os.path.exists(self.config.ini):
            self.log.warning(
                f'File "{self.config.ini}" not found, modify the generated config file ("{os.path.abspath(self.config.ini)}").'
            )
            result = self.config.save()
            print(result)
            self.exit()

        self.remotePath = self.config.remotePath
        self.localPath = self.config.localPath

        if not self.config.useNetShare:
            notPath = False
            if not os.path.exists(self.remotePath):
                self.log.error(
                    f'Remote folder: "{self.remotePath}" not found.')
                notPath = True
            if not os.path.exists(self.localPath):
                self.log.error(f'Local folder: "{self.localPath}" not found.')
                notPath = True
            if notPath:
                self.exit()

        self.timeStamp = self.config.timeStamp

        if not self.timeStamp:
            try:
                self.timeStamp = mktime(
                    strptime(self.config.startDate, '%Y-%m-%d %H:%M'))
            except ValueError:
                self.log.error(
                    f'Uncorrect start date: "{self.config.startDate}", correct format: "2000-01-01 00:00"'
                )
                self.exit()

        self.refreshTime = self.config.refreshTime
        self.extensionFile = tuple(
            self.config.extensionFile.replace(' ', '').split(','))

        self.log.info(f'    Logs level: {self.config.logsLevel}')
        self.log.info(f'    Remote folder: "{self.remotePath}"')
        self.log.info(f'    Local folder: "{self.localPath}"')
        self.log.info(f'    Refresh time: {self.refreshTime}')
        self.log.info(f'    Extension file: {self.extensionFile}')
        self.log.info(f'    Start date: {self.config.startDate}')
        self.log.info(
            f'    Last file: {strftime("%Y-%m-%d %H:%M:%S", gmtime(self.timeStamp))} (timeStamp: {self.timeStamp})'
        )

        self.nameQueue = NAME_QUEUE
        self.remoteList = []
        self.loadQueue()
        atexit.register(self.end)
        self.log.info('Service started.')

    # @staticmethod
    # def getUseNetShare():
    #     config = Config(os.path.join(getModulePath(), CONFIG_NAME))
    #     config.load()
    #     return config.useNetShare

    def loadQueue(self):
        if os.path.exists(self.nameQueue):
            with open(self.nameQueue, 'r', encoding='utf-8') as queue:
                files = queue.readlines()
                for file in files:
                    self.remoteList.append((self.timeStamp, file.strip()))
            try:
                os.remove(self.nameQueue)
            except Exception as exc:
                self.log.error(f'REMOVE {exc}')

    def saveQueue(self):
        if self.remoteList:
            try:
                with open(self.nameQueue, 'w', encoding='utf-8') as queue:
                    for file in self.remoteList:
                        queue.write(f'{file[1]}\n')
            except Exception as exc:
                self.log.error(f'WRITE {exc}')
        else:
            if os.path.exists(self.nameQueue):
                try:
                    os.remove(self.nameQueue)
                except Exception as exc:
                    self.log.error(f'REMOVE {exc}')

    def walker(self):
        self.log.info('Scanning directory...')
        self.scandir(self.remotePath)
        self.remoteList = sorted(self.remoteList)
        self.log.info(f'Found {len(self.remoteList)} files to copy.')
        if self.remoteList:
            self.timeStamp = self.remoteList[-1][0]
            for file in self.remoteList[:]:
                newName = f'{uuid4()}{os.path.splitext(file[1])[1]}'
                if self.copyfile(f'{file[1]}', f'{self.localPath}/{newName}'):
                    self.log.info(
                        f'File "{newName} << {file[1]}" "{strftime("%Y-%m-%d %H:%M:%S", gmtime(file[0]))} ({file[0]})" copied to local folder.'
                    )
                    self.remoteList.remove(file)
                else:
                    self.log.error(
                        f"File '{file[1]}' not copied to local folder.")
            self.config.timeStamp = self.timeStamp
            self.config.save()
            self.saveQueue()

    def scandir(self, path: str):
        try:
            with os.scandir(path) as scanDir:
                for entry in scanDir:
                    if entry.is_dir(follow_symlinks=False) and (
                            entry.stat().st_mtime > self.timeStamp):
                        self.scandir(entry.path)
                    elif entry.is_file(
                            follow_symlinks=False) and entry.name.endswith(
                                self.extensionFile) and (entry.stat().st_ctime
                                                         > self.timeStamp):
                        self.remoteList.append(
                            (entry.stat().st_ctime, entry.path))
        except Exception as exc:
            self.log.error(f"Directory '{path}' scan error: {exc}")

    def copyfile(self, path, filename):
        try:
            shutil.copy2(path, filename)
            return True
        except Exception as exc:
            print(f'[RTLC]: {exc}')
            return False

    def timeout(self):
        sleep(self.refreshTime)

    def run(self):
        while True:
            self.walker()
            self.timeout()

    def exit(self):
        sys.exit()

    def end(self):
        # self.running = False
        self.log.info('Service stopped.')


if __name__ == '__main__':
    rtlc = []
    with os.scandir(os.path.join(getModulePath())) as scanDir:
        for entry in scanDir:
            if entry.is_file(
                    follow_symlinks=False) and entry.name.endswith('rtlc.ini'):
                rtlc.append(entry.name.rpartition('.')[0])
    if not rtlc:
        rtlc.append('rtlc')
    for rtlc in rtlc[:]:
        rtlc = CopyUtility(rtlc)
        rtlc.thread = threading.Thread(target=rtlc.run, daemon=True)
        rtlc.thread.start()

    while True:
        pass
