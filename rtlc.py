#Remote To Local Copy(RTLC)
from datetime import datetime
from time import sleep
import os, shutil

from config import Config

config = Config('config.ini')
config.load()

if not os.path.exists('config.ini'):
    print('Файл config.ini не найден, введите данные для создания конфигурационного файла.')
    
    remotePath = input('Введите remotePath(default = "./"): ')
    if remotePath:
        config.remotePath = remotePath
        
    localPath = input('Введите localPath(default = "./local"): ')
    if localPath:
        config.localPath = localPath
        
    startDate = input('Введите дату старта <yyyy-mm-dd>(default = 2000-01-01): ')
    if startDate:
         config.startDate = startDate
         
    config.save()

remotePath = config.remotePath
localPath = config.localPath
startDate = config.startDate

print(f'\nRemote Path: "{remotePath}"')
print(f'Local Path: "{localPath}"')
print(f'Start Date: {startDate}\n')

startDate = datetime.strptime(startDate, "%Y-%m-%d").timestamp()

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
        for file in remoteSortList[:]:  # перебрать копию списка
            try:
                shutil.copy2(file[1], localPath)
                print(
                    f'    File "{file[1]} ( {datetime.fromtimestamp(file[0]).strftime("%Y-%m-%d %H:%M:%S")}, stamp: {file[0]} ) copied to local path.'
                )
                remoteSortList.remove(file)
            except Exception as exp:
                print(exp)
    sleep(5)
