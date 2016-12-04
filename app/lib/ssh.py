import time
import paramiko

class ConnectServError(Exception):
    pass

class Paramiko():
    def __init__(self, host, user, psw):
        self.stdout = None
        try:
            self.pm = paramiko.SSHClient()
            self.pm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.pm.connect(host, username=user, password=psw)
        except NameError:
            raise ConnectServError('paramiko is not installed. Unable to connect using Paramiko')
        # TODO: do we need to handle each case separately?
        except Exception as e:
            raise ConnectServError('Login to host %s failed via ssh, Error: %s' % (host, e))

    def __repr__(self):
        return 'Paramiko'

    def send(self, msg):
        if self.stdout:
            self.stdout.channel.close()
            self.stdout = None
        stdin, self.stdout, stderr = self.pm.exec_command(msg)
        stdin.channel.shutdown_write()

    def receive(self):
        if not self.stdout:
            return ''
        # stdout.read() can wait forever sometime.
        # adding this workaround...
        # still not very happy with the decision
        # of using module paramiko
        for _ in range(7):
            if self.stdout.channel.eof_received:
                break
            else:
                time.sleep(1)
        else:
            self.stdout.channel.close()
        return self.stdout.read().decode('utf-8')

    def close(self):
        self.pm.close()
