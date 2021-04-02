import csv
import sys, traceback
from base import base
import logging
import logging.handlers


class dataloader:
  #
  #Initializer
  #
  def __init__(self):
    self.baseinstance = base("user1", "test1")
    self.SUCCESS = 0
    self.FAILURE = 1
    LOG_FILENAME = "/home/akhilesh/sandBox/tripIt/logs/dbloader.log"
    self.dblogger = logging.getLogger('tripit.dbloader')
    self.dblogger.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s %(filename)s %(funcName)s %(lineno)d %(levelname)s %(message)s')
    dbhandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=15000000, backupCount=5)
    dbhandler.setFormatter(logformat)
    self.dblogger.addHandler(dbhandler)
    self.dblogger.handlers[0].doRollover()


  #Loads data from a csv file
  def csvloader(self, filename, tablename, dbop):
    #debug
    print ("DEBUG: Running csvloader...")
    self.dblogger.info("Running csvloader()...")
    CSV_FILENAME = filename
    insertcount  = 0
    updatecount  = 0
    if (open(CSV_FILENAME)):
      with open(CSV_FILENAME) as csvfile:
        keyFileReader = csv.DictReader(csvfile, restval="noMetaKey")
        if dbop == "insert":
          if tablename == "airportcities":
            for row in keyFileReader:
              insertdict = {}
              #readline
              if row["airportcity"] and row["country"] and row["latitude"] and row["longitude"]:
                insertdict['airportcity'] = row["airportcity"]
                insertdict['country'] = row["country"]
                insertdict['latitude'] = row["latitude"]
                insertdict['longitude'] = row["longitude"]
              try:
                self.dblogger.debug("insertdict {0}".format(insertdict))
                self.baseinstance.dbinit("apimetadata")
                self.baseinstance.dbinsert(tablename, insertdict)
                self.baseinstance.dbclose()
                self.dblogger.debug("Database insert complete.")
                insertcount += 1
              except:
                self.dblogger.error("Database operation 'INSERT' failed.")
                self.baseinstance.dbinit("apimetadata")
                self.baseinstance.dbrollback()
                self.baseinstance.dbclose()
                return self.FAILURE
                sys.exit(1)
              finally:
                if not row or (insertcount == 1000):
                  if insertcount == 1000:
                    insertcount = 0
                  try:
                    self.baseinstance.dbinit("apimetadata")
                    self.baseinstance.dbcommit()
                    self.baseinstance.dbclose()
                    self.dblogger.debug("Database commit complete.")
                  except:
                    self.dblogger.error("Database commit failed due to unknown reasons.")
                    return self.FAILURE
                    sys.exit(1)
          if tablename == "categorydna":
            for row in keyFileReader:
              insertdict = {}
              #readline
              if row["category"] and row["chillpoint"] and row["partypoint"]:
                insertdict['category'] = row["category"]
                insertdict['chillout'] = row["chillpoint"]
                insertdict['party'] = row["partypoint"]
              try:
                self.dblogger.debug("insertdict {0}".format(insertdict))
                self.baseinstance.dbinit("algometadata")
                self.baseinstance.dbinsert(tablename, insertdict)
                self.baseinstance.dbclose()
                self.dblogger.debug("Database insert complete.")
                insertcount += 1
              except:
                self.dblogger.error("Database operation 'INSERT' failed.")
                self.baseinstance.dbinit("algometadata")
                self.baseinstance.dbrollback()
                self.baseinstance.dbclose()
                return self.FAILURE
                sys.exit(1)
              finally:
                if not row or (insertcount == 1000):
                  if insertcount == 1000:
                    insertcount = 0
                  try:
                    self.baseinstance.dbinit("algometadata")
                    self.baseinstance.dbcommit()
                    self.baseinstance.dbclose()
                    self.dblogger.debug("Database commit complete.")
                  except:
                    self.dblogger.error("Database commit failed due to unknown reasons.")
                    return self.FAILURE
                    sys.exit(1)
        elif dbop == "update":
          for row in keyFileReader:
            updatedict = {}
            if row["weekendtrip"] and row["explorecountry"] and row["skiing"] and row["familyvacation"]:
              updatedict['weekendtrip'] = row["weekendtrip"]
              updatedict['explorecountry'] = row["explorecountry"]
              updatedict['skiing'] = row["skiing"]
              updatedict['familyvacation'] = row["familyvacation"]
            matchrowdict = {}
            if row["category"]:
              matchrowdict['category'] = row["category"]
            try:
              self.dblogger.debug("updatedict {0}".format(updatedict))
              self.dblogger.debug("matchrowdict {0}".format(matchrowdict))
              self.baseinstance.dbinit("algometadata")
              self.baseinstance.dbupdate(tablename, updatedict, matchrowdict)
              self.baseinstance.dbclose()
              self.dblogger.debug("Database update complete.")
              updatecount += 1
            except:
              self.dblogger.error("Database operation 'UPDATE' failed.")
              self.baseinstance.dbinit("algometadata")
              self.baseinstance.dbrollback()
              self.baseinstance.dbclose()
              return self.FAILURE
              sys.exit(1)
            finally:
              if not row or (updatecount == 1000):
                if updatecount == 1000:
                  updatecount = 0
                try:
                  self.baseinstance.dbinit("algometadata")
                  self.baseinstance.dbcommit()
                  self.baseinstance.dbclose()
                  self.dblogger.debug("Database commit complete.")
                except:
                  self.dblogger.error("Database commit failed due to unknown reasons.")
                  return self.FAILURE
                  sys.exit(1)
    else:
      self.dblogger.error("Unable to open data file for processing due to unkown errors.")
      self.dblogger.error("Errormessage - {0}".format(sys.exc_info()))
    self.dblogger.info("Data has been loaded to the database successfully.")
    return self.SUCCESS




#testing/debug
instance = dataloader()
#output = instance.csvloader("/home/akhilesh/TripppIn/data/airports.csv", "airportcities")
output = instance.csvloader("/home/akhilesh/TripppIn/data/categories.csv", "categorydna", "update")
if output is not None and output != 1:
  print ("Data has been loaded to the database successfully.")
else:
  print ("Data loading to database failed.")
