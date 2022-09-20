import pyinstaller_versionfile

name = 'RTLC'
ver = '1.0.0.1'
encoding = 'UTF-8'

history = '''
    History changed:
        1.0.0:
            1.0.0.1: Исправлена проблема с завершением работы службы после 1000 попыток переподключения к сетевой шаре
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
    # with open('history.txt', mode='r', encoding=encoding) as history:
    #     readme.write(history.read())
