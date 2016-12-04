#import logging
from lib import db
from flask import Flask, render_template, request, abort, Response, jsonify
import functools32

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
#con.getDB('Archives')
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

@app.route('/')
def index():
    return render_template('index.html', collections = collections)

@app.route('/driver')
def driver():
    drv = request.args.get('driver')
    #print "driver==== %s" % drv
    drv_info = getArchivesData(drv)
    cov_data = getKmbcovData(drv)
    #print cov_data 
    return render_template('driver.html', drv_info=drv_info, drv=drv, cov_data=cov_data, collections=collections)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
