from smb.SMBConnection import SMBConnection
from nmb.NetBIOS import NetBIOS


class SmbClient():

    def __init__(self, shareIP, userName, userPassword, shareName,
                 clientMachineName, remoteMachineName):
        self.shareIP = shareIP
        self.userName = userName
        self.userPassword = userPassword
        self.shareName = shareName
        self.clienthost = clientMachineName
        self.remotehost = remoteMachineName

    def getBIOSName(self, timeout=5):
        try:
            bios = NetBIOS()
            msg = bios.queryIPForName(self.shareIP, timeout=timeout)[0]
            result = True
        except Exception as exc:
            msg = str(exc)
            result = False
        finally:
            bios.close()
            return result, msg

    @staticmethod
    def create(userName, userPassword, clientMachineName, remoteMachineName):
        return SMBConnection(userName,
                             userPassword,
                             clientMachineName,
                             remoteMachineName,
                             use_ntlm_v2=True)

    def connect(self):
        try:
            if self.server.connect(self.shareIP, 139):
                return True, 'Authentication successfully.'
            else:
                return False, 'Failed authentication.'
        except Exception as exc:
            return False, f'{exc}'

    def close(self):
        try:
            self.server.close()
        except:
            pass

    def echo(self):
        data = 'echo'.encode()
        try:
            if self.server.echo(data) == data:
                return True
            else:
                return False
        except:
            return False

    def copyfile(self, path, filename):
        try:
            with open(filename, 'wb') as file_obj:
                self.server.retrieveFile(self.shareName, path, file_obj)
            return True
        except Exception as exc:
            print(f'[RTLC]: {exc}')
            return False

    def scandir(self, path: str):
        try:
            scanDir = self.server.listPath(self.shareName, path)
        except:
            self.connect()
        for entry in scanDir:
            if entry.isDirectory and (entry.filename !=
                                      '.') and (entry.filename != '..'):
                self.scandir(path + entry.filename + '/')
            elif not entry.isDirectory and (entry.create_time >
                                            self.timeStamp):
                self.remoteList.append(
                    (entry.create_time, path + entry.filename))
