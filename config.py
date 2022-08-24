import configparser


class Config:

    def __init__(self, ini: str):
        self.ini = ini
        self.config = configparser.ConfigParser()
        self.startDate: str = '2000-01-01'
        self.remotePath: str = './'
        self.localPath: str = './local'

    def getstring(self, section, option, fallback):
        string = self.config.get(section, option, fallback=fallback)
        if string:
            return string
        else:
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
        self.remotePath = self.getstring('Paths',
                                         'remote',
                                         fallback=self.remotePath)
        self.localPath = self.getstring('Paths',
                                        'local',
                                        fallback=self.localPath)
        
    def save(self):
        self.config['Options'] = {
            'start_date': self.startDate
        }
        self.config['Paths'] = {
            'remote': self.remotePath,
            'local': self.localPath
        }
        with open(self.ini, 'w') as configfile:
            try:
                self.config.write(configfile)
            except OSError:
                print(f'[CONFIG]: Error save file: {self.ini}')