#import logging
import os
from lib import db, picker, launcher
from collections import OrderedDict, defaultdict
from flask import Flask, render_template, request, abort, Response, jsonify, redirect, url_for, g, session
import functools32
from werkzeug.local import LocalProxy

Cache = functools32.lru_cache(maxsize=256)

"""
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/hwe-portal.log',
                filemode='w')
"""
app = Flask(__name__)

con = db.mongo('10.117.5.169', 27017)
con.getConnection()
collections = con.getCollectionName('Archives')
collections.remove('system.indexes')

@Cache
def getArchivesData(drv):
    drv_info = con.getDriverCov(drv)
    return drv_info

@Cache
def getKmbcovData(drv):
    cov_data = con.getAllCovData(drv)
    return cov_data

def setlock(fp):
    lock = '%s.lock' % fp
    with open(lock, 'w'):
        pass

def removelock(fp):
    lock = '%s.lock' % fp
    if os.path.exists(lock):
        os.remove(lock)

def getmsg(sid):
    fp = os.path.join('/tmp/', str(sid))
    if not os.path.exists(fp):
            return ''
    setlock(fp)
    with open(fp, 'r') as fd:
        msg = fd.read()
        open(fp, 'w').close()
        removelock(fp)
        return msg

def checkstate(sid):
    path = os.path.join('/tmp/', str(sid))
    fp = path + '.state'
    return '' if os.path.exists(fp) else 'done'
       

@app.route('/getresult/<int:sid>', methods=['GET'])
def getresult(sid):
    msg = getmsg(sid)
    msg = msg.replace('\n', '<br>')
    #print msg
    return  jsonify(msg=msg, stats=checkstate(sid)), 201

@app.route('/output')
def output():
    host = request.args.get('host')
    launchost = request.args.get('launchost')
    cmd = request.args.get('cmd')
    jobid=request.args.get('jobid')
    user = request.args.get('user')
    cases =  request.args.get('cases').split(',')
    return render_template('console.html',
                           jobid=jobid,
                           launchost=launchost,
                           host=host,
                           cmd=cmd,
                           user=user,
                           cases=cases)

@app.route('/runcase', methods=['POST'])
def runcase():
    if request.method == 'POST':
        launchost = request.form.get('launchost')
        host = request.form.get('testbed')
        user = request.form.get('testername')
        #print host, user
        case_list = request.form.getlist('checked_checkbox')
        cases = ','.join(case_list)
        cmd = launcher.getcmd(case_list, host, user)
        jobid = launcher.runcase(launchost, cmd)
        #print jobid
        return redirect(url_for('output',
                                jobid=jobid,
                                launchost=launchost,
                                host=host,
                                cmd=cmd,
                                user=user,
                                cases=cases))

@app.route('/caselist', methods=['GET'])
def caselist():
    if request.method == 'GET':
        chg = request.args.get('change')
        mod = request.args.get('module')
        func_list = picker.getTestCase(con, chg, mod)
        #print func_list
        func_dict = OrderedDict()
        for x in func_list:
            func_dict[x[0]]=x[1]
        #print func_dict
        return jsonify(func_list=func_dict), 201

@app.route('/smartlauncer')
def smartlauncher():
    return render_template('smartlauncher.html',
                           collections = collections)

@app.route('/')
def index():
    return render_template('index.html',
                           collections = collections)

@app.route('/driver')
def driver():
    drv = request.args.get('driver')
    drv_info = getArchivesData(drv)
    cov_data = getKmbcovData(drv)
    return render_template('driver.html',
                           drv_info=drv_info,
                           drv=drv,
                           cov_data=cov_data,
                           collections=collections)

if __name__ == '__main__':
    #app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', port=80, threaded=True, debug=True)
