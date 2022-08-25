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

logging.info('Запуск программы.')

config = Config('config.ini')
config.load()

if not os.path.exists(config.ini):
    logging.warning(
        f'Файл config.ini не найден, отредактируйте созданный конфигурационный файл ("{os.path.abspath(config.ini)}").'
    )
    config.save()
    exit()

config.save()

remotePath = config.remotePath
localPath = config.localPath

notPath = False

if not os.path.exists(remotePath):
    logging.error(f'Удаленный каталог "{remotePath}" не найден.')
    notPath = True

if not os.path.exists(localPath):
    logging.error(f'Локальный каталог "{localPath}" не найден.')
    notPath = True

if notPath:
    exit()

refreshTime = config.refreshTime
timeStamp = config.timeStamp

print(f'\nRemote Path: "{remotePath}"')
print(f'Local Path: "{localPath}"')
print(f'Refresh Time: {refreshTime}')
print(f'Start Date: {config.startDate}')
print(f'Time Stamp: {timeStamp}\n')

if not timeStamp:
    try:
        timeStamp = mktime(strptime(config.startDate, '%Y-%m-%d %H:%M'))
    except ValueError:
        logging.error(
            f'Неверная дата старта: "{config.startDate}", правильный формат: "2000-01-01 00:00"'
        )
        exit()

remoteSortList = []

logging.info('Программа запущена.')

while True:
    remoteList = os.listdir(remotePath)
    print(f'*Refresh List*')
    for file in remoteList:
        file = os.path.join(remotePath, file)
        if os.path.isdir(file):
            continue
        getctime = os.path.getctime(file)
        if getctime > timeStamp:
            remoteSortList.append((getctime, file))
    remoteSortList = sorted(remoteSortList)
    if remoteSortList:
        timeStamp = remoteSortList[-1][0]
        config.timeStamp = timeStamp
        config.save()
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                logging.info(
                    f'File "{file[1]}" ( {ctime(file[0])} ) {file[0]} copied to local path.'
                )
                remoteSortList.remove(file)
            except Exception as exp:
                print(exp)
    sleep(refreshTime)
