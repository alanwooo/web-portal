import os
import ssh
import time
import threading
import tempfile
import multiprocessing
from multiprocessing.pool import ThreadPool as Pool
from collections import namedtuple

Auth = namedtuple('Auth','user passwd')
auth = Auth('root', 'ca$hc0w')
DIR='/tmp/'

def writetofile(launchost, cmd, fn):
    client = ssh.Paramiko(launchost, auth.user, auth.passwd)
    client.sendasync(cmd)
    f = os.path.join(DIR, fn)
    fstate = f + '.state'
    with open(fstate, 'w'):
        pass
    flock = f + '.lock'
    with open(f, 'w', 0) as fd:
        msg = ''
        while True:
            rc, ret = client.receiveasync()
            msg += ret
            if not rc:
                os.remove(fstate)
                fd.write(msg)
                return True
            #print msg
            if os.path.exists(flock):
                continue
            fd.write(msg)
            msg = ''

def getcmd(cases, host, user):
    env = '. /etc/profile;'
    python = '/usr/bin/python'
    script = '/root/Automation/Drivers/TestLauncher.py'
    param = '%s --ATLAS_User %s --ATLAS_Cases %s' % (host, user, ' '.join(cases))
    cmd = '%s %s %s %s' % (env, python, script, param)
    #cmd = 'i=0; while [ 1 ];do i=`expr $i + 1`; echo "haha $i"; sleep 1; if [ $i -gt 100 ]; then break; fi done'
    return cmd


def runcase(launchost, cmd):
    fn = str(int(round(time.time() * 1000)))
    #print fn
    pool = Pool()
    result =threading.Thread(target=writetofile, args=(launchost, cmd, fn,))
    result.start()
    return fn 

if __name__ == "__main__":
    cases='aaaa'
    host='pek2-office-04-dhcp74.eng.vmware.com'
    user='chaofengw'
    cmd = getcmd(cases, host, user)
    ret = runcase(host, cmd)
    print ret
    time.sleep(10)
