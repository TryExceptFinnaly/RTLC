from smb.SMBConnection import SMBConnection


class SmbClient():

    def __init__(self, ip, username, password, sharename, clienthost,
                 remotehost):
        self.ip = ip
        self.username = username
        self.password = password
        self.sharename = sharename
        self.clienthost = clienthost
        self.remotehost = remotehost

    def connect(self):
        try:
            self.server = SMBConnection(self.username,
                                        self.password,
                                        self.clienthost,
                                        self.remotehost,
                                        use_ntlm_v2=True)
            if self.server.connect(self.ip, 139):
                return 'Authentication successfully.'
            else:
                return 'Failed authentication.'
        except Exception as exc:
            return f'{exc}'

    def copyfile(self, path, filename):
        try:
            with open(filename, 'wb') as file_obj:
                self.server.retrieveFile(self.sharename, path, file_obj)
            return True
        except Exception as exc:
            print(f'[RTLC]: {exc}')
            return False

    def scandir(self, path: str, ts: float, rl: list):
        scanDir = self.server.listPath(self.sharename, path)
        for entry in scanDir:
            if entry.isDirectory and (entry.filename !=
                                      '.') and (entry.filename != '..'):
                self.scandir(path + entry.filename + '/', ts, rl)
            elif not entry.isDirectory and (entry.create_time > ts):
                rl.append((entry.create_time, path + entry.filename))
