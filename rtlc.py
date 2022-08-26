#Remote To Local Copy(RTLC)
import logging
import logging.handlers
from time import sleep, mktime, strptime, strftime, gmtime
import os
import shutil

from config import Config

FORMAT = '[%(asctime)s]: %(levelname)s - %(message)s'
LEVEL_LOGS = 'INFO'
FOLDER_LOGS = 'Logs'
NAME_LOG = 'rtlc.log'
SIZE_LOG = 1024 * 1024
COUNT_BACKUPS_LOGS = 5

config = Config('config.ini')
config.load()

if not os.path.exists(FOLDER_LOGS):
    os.mkdir(FOLDER_LOGS)

logging.basicConfig(level=LEVEL_LOGS, handlers='')

mainLog = logging.getLogger('main')

mainHandler = logging.handlers.RotatingFileHandler(
    f'{FOLDER_LOGS}/{NAME_LOG}',
    maxBytes=SIZE_LOG,
    backupCount=COUNT_BACKUPS_LOGS,
    encoding='utf-8')
mainHandler.setFormatter(logging.Formatter(FORMAT))

mainLog.addHandler(mainHandler)
mainLog.info('Starting service...')

if not os.path.exists(config.ini):
    mainLog.warning(
        f'File "config.ini" not found, modify the generated config file ("{os.path.abspath(config.ini)}").'
    )
    config.save()
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

mainLog.info(f'Remote folder: "{remotePath}"')
mainLog.info(f'Local folder: "{localPath}"')
mainLog.info(f'Refresh time: {refreshTime}')
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
    remoteList = os.listdir(remotePath)
    mainLog.info(f'Refresh')
    for file in remoteList:
        file = os.path.join(remotePath, file)
        if os.path.isdir(file):
            continue
        getctime = os.path.getctime(file)
        if getctime > timeStamp:
            remoteSortList.append((getctime, file))
    remoteSortList = sorted(remoteSortList)
    mainLog.info(f'Found {len(remoteSortList)} new files.')
    if remoteSortList:
        timeStamp = remoteSortList[-1][0]
        config.timeStamp = timeStamp
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                mainLog.info(
                    f'File "{file[1]}" "{strftime("%Y-%m-%d %H:%M:%S", gmtime(file[0]))} ({file[0]})" copied to local folder.'
                )
                remoteSortList.remove(file)
            except Exception as exc: 
                mainLog.error(exc)
        config.save()
    sleep(refreshTime)
