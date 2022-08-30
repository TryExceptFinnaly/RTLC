import configparser


class Config:

    def __init__(self, ini: str):
        self.ini = ini
        self.config = configparser.ConfigParser()
        self.startDate: str = '2000-01-01 00:00'
        self.timeStamp: float = 0.0
        self.refreshTime: int = 60
        self.extensionFile: str = ''
        self.remotePath: str = './remote'
        self.localPath: str = './local'
        self.logsLevel: str = 'INFO'
        self.logsSize: int = 2
        self.logsBackups: int = 5

    def getstring(self, section, option, fallback):
        string = self.config.get(section, option, fallback=fallback)
        if string:
            return string
        else:
            return fallback

    def getfloat(self, section, option, fallback):
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except ValueError:
            return fallback

    def getint(self, section, option, fallback):
        try:
            return self.config.getint(section, option, fallback=fallback)
        except ValueError:
            return fallback

    def getboolean(self, section, option, fallback):
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except ValueError:
            return fallback

    def load(self):
        self.config.read(self.ini)
        self.startDate = self.getstring('Options',
                                        'start_date',
                                        fallback=self.startDate)
        self.timeStamp = self.getfloat('Options',
                                       'last_file',
                                       fallback=self.timeStamp)
        self.refreshTime = self.getint('Options',
                                       'refresh_time',
                                       fallback=self.refreshTime)
        self.extensionFile = self.getstring('Options',
                                            'extension_file',
                                            fallback=self.extensionFile)
        self.remotePath = self.getstring('Paths',
                                         'remote',
                                         fallback=self.remotePath)
        self.localPath = self.getstring('Paths',
                                        'local',
                                        fallback=self.localPath)
        self.logsLevel = self.getstring('Logs',
                                        'level',
                                        fallback=self.logsLevel)
        self.logsSize = self.getint('Logs', 'size', fallback=self.logsSize)
        self.logsBackups = self.getint('Logs',
                                       'backups',
                                       fallback=self.logsBackups)

    def save(self) -> str:
        self.config['Options'] = {
            'start_date': self.startDate,
            'last_file': self.timeStamp,
            'refresh_time': self.refreshTime,
            'extension_file': self.extensionFile
        }
        self.config['Paths'] = {
            'remote': self.remotePath,
            'local': self.localPath
        }
        self.config['Logs'] = {
            'level': self.logsLevel,
            'size': self.logsSize,
            'backups': self.logsBackups
        }
        try:
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)
                return ('Building configuration file completed successfully.')
        except Exception as exc:
            return (f'Error building configuration file "{exc}": {self.ini}')
