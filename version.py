from distutils.command.config import config
import pyinstaller_versionfile

name = 'RTLC'
ver = '1.0.0.2'
encoding = 'UTF-8'

history = '''
    History changed:
        1.0.0:
            1.0.0.2: Добавлена многопоточность.
            Для активации дополнительного потока необходимо добавить еще один конфиг(Формат: '*rtlc.ini')
            1.0.0.1: Исправлена проблема с завершением работы службы после 1000 попыток переподключения к сетевой шаре
'''

installation = '''
    1. Install Windows(x64):
        a. Скачать 'dist/rtlc.exe'.
        b. Закинуть бинарь в рабочую директорию (Например: 'C:/rtlc/').
        c. Открыть командную строку от имени администратора и запустить бинарь с параметром install (Пример: 'C:/rtlc/rtlc.exe install')
        e. При первом запуске утилиты (Через 'Службы' или комнадную строку (Пример: 'C:/rtlc/rtlc.exe start')) она сгенерирует конфигурационный файл в директорию с бинарем (Пример: 'C:/rtlc/config.ini'). 
    2. Install RedOS:
        a. Скачать файлы: 'rtlc.py, config.py, install_rtlc.sh'.
        b. Закинуть файлы в домашнюю директорию (Например: '/home/lins/').
        c. Выдать права: 'chmod 755 /home/lins/install_rtlc.sh', запустить его и следовать инструкции установочного скрипта.
'''

config = '''
    Config.ini:
        [Options]
        1. start_date - дата и время создания файлов от которых начинать сканирование (игнорируется при заданном параметре last_file).
        2. last_file - timestamp от которого начинать сканирование файлов, подставляется автоматически.
        3. refresh_time - интервал между сканированием файлов (в секундах)
        4. extenstion_file - фильтр по расширениям файлов (Пример: '.dcm, .png'), если не нужен фильтр оставляем пустым
        [Paths]
        1. remote - путь до удалённой папки
        2. local - путь до локальной папки
        [NetShare] - Only Windows!!!
        1. use_network_share - подключение к сетевой шаре с помощью службы (True или False)
        2. share_ip - IP или DOMAIN сетевой папки
        3. share_name - Имя сетевой папки
        4. user_name - Логин
        5. user_password - Пароль
        6. client_machine_name - Хостнейм локальной машины (cmd: hostname)
        7. remote_machine_name - Хостнейм удалённой машины (Если не заполнять - программа узнает автоматически)
        [Logs]
        1. level - уровень логирования
        2. size - максимальный размер файла логов (в мегабайтах)
        3. backups - количество бекапов логов (создаются в случае достижения максимального размера основного файла логирования)
'''

pyinstaller_versionfile.create_versionfile(
    output_file="version.txt",
    version=ver,
    company_name="GNU General Public License",
    file_description=name,
    internal_name=name,
    legal_copyright="© GNU General Public License. All rights reserved.",
    original_filename="RTLC.exe",
    product_name=name)

with open('README.md', mode='w', encoding=encoding) as readme:
    readme.write(f'# {name} {ver} \n')
    readme.write(history)
    readme.write(f'# Installation:\n')
    readme.write(installation)
    readme.write(f'# Config:\n')
    readme.write(config)
    # with open('history.txt', mode='r', encoding=encoding) as history:
    #     readme.write(history.read())
