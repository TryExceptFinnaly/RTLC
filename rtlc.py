#Remote To Local Copy(RTLC)
from time import sleep, ctime, mktime, strptime
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

config.save()

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
        print(
            f'[ERROR]: Неверная дата старта: "{config.startDate}", правильный формат: "2000-01-01 00:00"'
        )
        input()
        exit()

remoteSortList = []

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
                print(
                    f'    {ctime()}: File "{file[1]}" ( {ctime(file[0])} ) {file[0]} copied to local path.'
                )
                remoteSortList.remove(file)
            except Exception as exp:
                print(exp)
    sleep(refreshTime)
