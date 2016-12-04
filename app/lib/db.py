import logging
import pymongo

try:
    import pymongo
except ImportError:
    pass

class mongo():
    def __init__(self, hostname, port):
        """
        Initiate parameters
        """
        self.hostname = hostname
        self.port = int(port)
        self.conn = None
        self.db = None
        self.coll = None
        #self._getConn()

    def getConnection(self):
        """
        Initiate Mongo DB connection
        @return: True Connect to DB server succeed
                 False Connect to DB server failed
        """
        try:
            self.conn = pymongo.MongoClient(self.hostname, self.port)
        except pymongo.errors.ConnectionFailure as e:
            log.warning('Could not connect to the DB server : \n %s' % e)
            return False
        except NameError:
            log.warning('pymongo library is missing... Unable to use mongo database.')
            return False

        if not self.conn:
            log.warning('Could not connect to the DB server.')
            return False
        return True

    def closeConnection(self):
        """
        Close the connection to DB
        """
        if self.conn:
            self.conn.close()

    def getDB(self, dbname='Archives'):
        """
        Initiate DB instance
        @param dbname: A string with Database's name
        """
        self.db = self.conn[dbname]

    def getCollection(self, collname):
        """
        Initiate collection instance
        @param collname: A string with test category
        """
        self.coll = self.db[collname]

    def getCollectionName(self, dbname):
        return self.conn[dbname].collection_names()

    def insertOneRecord(self, repo):
        """
        This function is to insert one record into Mongo DB
        @param repo: A dict including test and code coverage info
        """
        try:
            self.coll.insert(repo, continue_on_error=True)
        except pymongo.errors.DuplicateKeyError as e:
            log.warning('Insert the record to Mongo DB fail with : %s' % e)

    def insertMultiRecords(self, repos):
        """
        This function is to insert multiple records into Mongo DB
        """
        for repo in repos:
            self.insertOneRecord(repo)

    def getDriverCov(self, driver, dbname='Archives'):
        """
        Get target driver code coverage date for each esxi build.
        @return 
        """
        # [[esxi build number], [function percent], [branch percent]]
        ret = [[],[],[]]
        coll = self.conn[dbname][driver]
        for rd in coll.find().sort("esx_buildnum", pymongo.DESCENDING):
            if len(ret[0]) > 10:
                break
            ret[0].append(rd['esx_buildnum'])
            ret[1].append(str(round(rd['function_percent'] * 100, 2)))
            ret[2].append(str(round(rd['branch_percent'] * 100, 2)))
        map(lambda x: x.reverse(), ret)
        return ret

    def getAllCovData(self, driver, dbname='KMBCOV'):
        """
        Get target driver all the coverage data.
        @return
        """
        ret=[]
        coll = self.conn[dbname][driver]
        for rd in coll.find().sort('esx_buildnum', pymongo.DESCENDING):
            if len(ret) > 100:
                break
            ret.append([rd['esx_buildnum'],
                        str(round(rd['cov_data']['functionPer'] * 100, 2)),
                        str(round(rd['cov_data']['branchPer'] * 100, 2)),
                        rd['esx_version'],
                        rd['esx_buildtype'],
                        rd['testid'],
                        rd['vmnum'],
                       ])
        return ret
