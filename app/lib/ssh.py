import time
import select
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
        for _ in range(150):
            if self.stdout.channel.eof_received:
                break
            else:
                time.sleep(1)
        else:
            self.stdout.channel.close()
        return self.stdout.read().decode('utf-8')

    def close(self):
        self.pm.close()

    def sendasync(self, cmd):
        self.channel = self.pm.get_transport().open_session()
        self.channel.set_combine_stderr(True)
        self.channel.exec_command(cmd)

    def receiveasync(self):
        if self.channel.exit_status_ready():
            if self.channel.recv_stderr_ready():
                return False, '%s\nERROR: Launching test cases failed !!!' % self.channel.recv_stderr(1024)
            return False, self.channel.recv(1024)
        r, w, x = select.select([self.channel], [], [], 10.0)
        if len(r) > 0:
            return True, self.channel.recv(1024)
        return True, ''


if __name__ == "__main__":
    cmd =  'cat /tmp/hahaha'
    cmd =  '. /etc/profile; /usr/bin/python /root/Automation/Drivers/TestLauncher.py prmb-hwe041 --ATLAS_User chaofengw --ATLAS_Cases Storage::SSD::Functional::SMARTTools Storage::Stress::DeviceStateWithGracefulRemove Storage::Stress::IO_SMART Storage::Stress::SwapToSSD'
    cmd = 'i=0; while [ 1 ];do i=`expr $i + 1`; echo "haha $i"; sleep 1; if [ $i -gt 10 ]; then break; fi done; echo "hahahaha"; cat /tmp/haha; echo "heiheihei"'
    client =Paramiko('hwe-launcher42-vm', 'root', 'ca$hc0w')
    client.sendasync(cmd)
    while True:
        rc, ret = client.receiveasync()
        time.sleep(3)
        print rc, ret
