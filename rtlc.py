#Remote To Local Copy(RTLC)
import logging
from time import sleep, ctime, mktime, strptime
import os
import shutil

from config import Config

FORMAT = '[%(levelname)s][%(asctime)s]: %(message)s'
logging.basicConfig(format=FORMAT,
                    level='INFO',
                    filename='log.txt',
                    encoding='utf-8')

logging.info('Starting service...')

config = Config('config.ini')
config.load()

if not os.path.exists(config.ini):
    logging.error(
        f'File "config.ini" not found, modify the generated config file ("{os.path.abspath(config.ini)}").'
    )
    config.save()
    exit()

config.save()

remotePath = config.remotePath
localPath = config.localPath

notPath = False

if not os.path.exists(remotePath):
    logging.error(f'Remote folder "{remotePath}" not found.')
    notPath = True

if not os.path.exists(localPath):
    logging.error(f'Local folder "{localPath}" not found.')
    notPath = True

if notPath:
    exit()

refreshTime = config.refreshTime
timeStamp = config.timeStamp

logging.info(f'Remote folder: "{remotePath}"')
logging.info(f'Local folder: "{localPath}"')
logging.info(f'Refresh time: {refreshTime}')
logging.info(f'Start date: {config.startDate}')
logging.info(f'Last file: {ctime(timeStamp)} (TimeStamp: {timeStamp})')

if not timeStamp:
    try:
        timeStamp = mktime(strptime(config.startDate, '%Y-%m-%d %H:%M'))
    except ValueError:
        logging.error(
            f'Uncorrect start date: "{config.startDate}", correct format: "2000-01-01 00:00"'
        )
        exit()

remoteSortList = []

logging.info('Service started.')

while True:
    remoteList = os.listdir(remotePath)
    logging.info(f'Refresh')
    for file in remoteList:
        file = os.path.join(remotePath, file)
        if os.path.isdir(file):
            continue
        getctime = os.path.getctime(file)
        if getctime > timeStamp:
            remoteSortList.append((getctime, file))
    remoteSortList = sorted(remoteSortList)
    logging.info(f'Found {len(remoteSortList)} new files.')
    if remoteSortList:
        timeStamp = remoteSortList[-1][0]
        config.timeStamp = timeStamp
        config.save()
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                logging.info(
                    f'File "{file[1]}" ( {ctime(file[0])} ) {file[0]} copied to local folder.'
                )
                remoteSortList.remove(file)
            except Exception as exp:
                print(exp)
    sleep(refreshTime)
