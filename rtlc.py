#Remote To Local Copy(RTLC)
import logging
import logging.handlers
from time import sleep, mktime, strptime, strftime, gmtime
import os
import shutil

from config import Config

config = Config('config.ini')
config.load()

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
        exit()

logging.basicConfig(handlers='')

SIZE_LOG = config.logsSize * 1024 * 1024

mainHandler = logging.handlers.RotatingFileHandler(
    f'{FOLDER_LOGS}/{NAME_LOG}',
    maxBytes=SIZE_LOG,
    backupCount=config.logsBackups,
    encoding='utf-8')
mainHandler.setFormatter(logging.Formatter(FORMAT))

mainLog = logging.getLogger('rltc')
mainLog.addHandler(mainHandler)

config.logsLevel = config.logsLevel.upper()
if config.logsLevel not in [
        'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
]:
    mainLog.error(
        f'Uncorrect logging level: "{config.logsLevel}". Available values: "NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL".'
    )
    exit()

mainLog.setLevel(config.logsLevel)
mainLog.info('Starting service...')

if not os.path.exists(config.ini):
    mainLog.warning(
        f'File "{config.ini}" not found, modify the generated config file ("{os.path.abspath(config.ini)}").'
    )
    result = config.save()
    print(result)
    exit()

config.save()

remotePath = config.remotePath
localPath = config.localPath

notPath = False

if not os.path.exists(remotePath):
    mainLog.error(f'Remote folder "{remotePath}" not found.')
    notPath = True

if not os.path.exists(localPath):
    mainLog.error(f'Local folder "{localPath}" not found.')
    notPath = True

if notPath:
    exit()

refreshTime = config.refreshTime
timeStamp = config.timeStamp
extensionFile = tuple(config.extensionFile.replace(' ', '').split(','))

mainLog.info(f'Logs level: {config.logsLevel}')
mainLog.info(f'Remote folder: "{remotePath}"')
mainLog.info(f'Local folder: "{localPath}"')
mainLog.info(f'Refresh time: {refreshTime}')
mainLog.info(f'Extension file: {extensionFile}')
mainLog.info(f'Start date: {config.startDate}')
mainLog.info(
    f'Last file: {strftime("%Y-%m-%d %H:%M:%S", gmtime(timeStamp))} (TimeStamp: {timeStamp})'
)

if not timeStamp:
    try:
        timeStamp = mktime(strptime(config.startDate, '%Y-%m-%d %H:%M'))
    except ValueError:
        mainLog.error(
            f'Uncorrect start date: "{config.startDate}", correct format: "2000-01-01 00:00"'
        )
        exit()

remoteSortList = []
mainLog.info('Service started.')

while True:
    mainLog.info(f'Refresh')
    with os.scandir(remotePath) as scanDir:
        for entry in scanDir:
            if entry.is_file(follow_symlinks=False) and entry.name.endswith(
                    extensionFile) and (entry.stat().st_ctime > timeStamp):
                remoteSortList.append((entry.stat().st_ctime, entry.path))
        remoteSortList = sorted(remoteSortList)
    mainLog.info(f'Found {len(remoteSortList)} new files.')
    if remoteSortList:
        timeStamp = remoteSortList[-1][0]
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                mainLog.info(
                    f'File "{file[1]}" "{strftime("%Y-%m-%d %H:%M:%S", gmtime(file[0]))} ({file[0]})" copied to local folder.'
                )
                remoteSortList.remove(file)
            except Exception as exc:
                mainLog.error(
                    f"File '{file[1]}' not copied to local folder: {exc}")
        config.timeStamp = timeStamp
        config.save()
    sleep(refreshTime)
