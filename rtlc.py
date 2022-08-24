#Remote To Local Copy(RTLC)
from datetime import datetime
from time import sleep
import os, shutil

from config import Config

config = Config('config.ini')
config.load()

if not os.path.exists(config.ini):
    print(
        f'[WARNING]: Файл config.ini не найден, отредактируйте созданный конфигурационный файл ("{os.path.abspath(config.ini)}").'
    )
    config.save()
    input()
    exit()

remotePath = config.remotePath
localPath = config.localPath

notPath = False

if not os.path.exists(remotePath):
    print(f'[ERROR]: Удаленный каталог "{remotePath}" не найден.')
    notPath = True

if not os.path.exists(localPath):
    print(f'[ERROR]: Локальный каталог "{localPath}" не найден.')
    notPath = True

if notPath:
    input()
    exit()

refreshTime = config.refreshTime
startDate = config.startDate

print(f'\nRemote Path: "{remotePath}"')
print(f'Local Path: "{localPath}"')
print(f'Refresh Time: {refreshTime}')
print(f'Start Date: {startDate}\n')

try:
    startDate = datetime.strptime(startDate,
                                  "%Y-%m-%d %H:%M:%S.%f").timestamp()
except ValueError:
    print(
        f'[ERROR]: Неверная дата старта: "{startDate}", правильный формат: "{datetime.fromtimestamp(0.0).strftime("%Y-%m-%d %H:%M:%S.%f")}"'
    )
    exit()

remoteSortList = []

while True:
    remoteList = os.listdir(remotePath)
    print(f'*remoteList:')
    for file in remoteList:
        file = os.path.join(remotePath, file)
        if os.path.isdir(file):
            continue
        getctime = os.path.getctime(file)
        if getctime > startDate:
            remoteSortList.append((getctime, file))
    remoteSortList = sorted(remoteSortList)
    if remoteSortList:
        startDate = remoteSortList[-1][0]
        config.startDate = datetime.fromtimestamp(startDate).strftime(
            "%Y-%m-%d %H:%M:%S.%f")
        config.save()
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                print(
                    f'    File "{file[1]} ( {datetime.fromtimestamp(file[0]).strftime("%Y-%m-%d %H:%M:%S.%f")} ) copied to local path.'
                )
                remoteSortList.remove(file)
            except Exception as exp:
                print(exp)
    sleep(refreshTime)
