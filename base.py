import MySQLdb as mdb
import sys
import logging
import logging.handlers
import traceback


class base:
  #
  #initializer
  #
  def __init__(self, user, password):
    self.user     = user
    self.password = password
    self.host     = '127.0.0.1'
    self.SUCCESS = 0
    self.FAILURE = 1
    LOG_FILENAME = "logs/dbloader.log"
    self.baselogger = logging.getLogger('dbloader')
    self.baselogger.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s %(filename)s %(funcName)s %(lineno)d %(levelname)s %(message)s')
    bhandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=15000000, backupCount=5)
    bhandler.setFormatter(logformat)
    self.baselogger.addHandler(bhandler)
    self.baselogger.handlers[0].doRollover()


  #
  #Initialize database
  #
  def dbinit(self, db):
    try:
      self.connection = mdb.connect(self.host, self.user, self.password, db)
    except mdb.Error as err:
      self.baselogger.error("Error {0} {1}".format(err.args[0], err.args[1]))
    finally:
      if self.connection:
        self.baselogger.info("Connected to database successfully.")
        return self.SUCCESS
      else:
        self.baselogger.error("Unable to connect to database. ")
        self.baselogger.error("Message - {0}".format(sys.exc_info()))
        return self.FAILURE
        sys.exit(1)


  #
  #Closing database connection
  #
  def dbclose(self):
    self.baselogger.info("Running dbclose()...")
    if self.connection:
      try:
        self.connection.close()
        self.baselogger.info("Database connection closed.")
        return self.SUCCESS
      except:
        self.baselogger.error("Operation 'connection close' failed for unknown reasons.")
        self.baselogger.error("Message - {0}".format(sys.exc_info()))
        return self.FAILURE
    else:
      self.baselogger.error("dbclose() failed as no connection object to database found.")
      return self.FAILURE


  #
  #Commit to database
  #
  def dbcommit(self):
    self.baselogger.info("Running dbcommit()...")
    if self.connection:
      try:
        self.connection.commit()
        self.baselogger.info("Database commit successful.")
        return self.SUCCESS
      except:
        self.baselogger.error("Operation 'commit' failed for unknown reasons.")
        self.baselogger.error("Errormessage: {0}".format(sys.exc_info()))
        return self.FAILURE
    else:
      self.baselogger.error("dbcommit() failed as no connection object to database found.")
      return self.FAILURE


  #
  #Rollback database changes
  #
  def dbrollback(self):
    self.baselogger.info("Running dbrollback()...")
    if self.connection:
      try:
        self.connection.rollback()
        self.baselogger.info("Database rollback successful.")
        return self.SUCCESS
      except:
        self.baselogger.error("Operation 'rollback' failed due to unknown reasons.")
        self.baselogger.error("Errormessage: {0}".format(sys.exc_info()))
        return self.FAILURE
    else:
      self.baselogger.error("dbrollback() failed as no connection object to database found.")
      return self.FAILURE


  #
  #SELECT - Prepare query, perform operation and return data
  #
  def dbselect(self, tablename, rowcount, columns, keyvaluepairs):
    self.baselogger.info("Running base.dbselect()...")
    selectclause   = "SELECT "
    fromclause     = "FROM "
    whereclause    = "WHERE "
    andclause      = ""
    limitclause    = "LIMIT "
    andstatement   = "AND "
    space          = " "
    comma          = ","
    equals         = "="
    star           = "*"
    nofilterparams = 0
    nolimitparam   = 0
    if columns:
      for i in range(len(columns)):
        selectclause = selectclause + columns[i]
        if i == (len(columns) - 1):
          selectclause = selectclause + space
        else:
          selectclause = selectclause + comma + space
    else:
      selectclause = selectclause + star + space
    if tablename:
      fromclause = fromclause + tablename + space
    else:
      self.baselogger.error("TABLENAME not provided. ")
      return self.FAILURE
      sys.exit()
    if keyvaluepairs:
      runonce = 0
      for key, value in keyvaluepairs.items():
        if key == "wherestring":
          whereclause = whereclause + value + space
        elif "andstring" in key:
          andclause = andclause + andstatement + value + space
        elif not runonce:
          whereclause = whereclause + key + space + equals + space + '"' + value + '"' + space
          runonce = 1
        else:
          andclause = andclause + andstatement + key + space + equals + space + '"' + value + '"' + space
    else:
      nofilterparams = 1
    if str(rowcount):
      limitclause = limitclause + str(rowcount)
    else:
      nolimitparam = 1
    if nofilterparams and nolimitparam:
      query = selectclause + fromclause
    elif nolimitparam:
      query = selectclause + fromclause + whereclause + andclause
    elif nofilterparams:
      query = selectclause + fromclause + limitclause
    else:
      query = selectclause + fromclause + whereclause + andclause + limitclause
    try:
      with self.connection:
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except:
      self.baselogger.error("The SELECT operaton has failed.")
      self.baselogger.error("querystring : {0}".format(query))
      self.baselogger.error("Message - {0}".format(sys.exc_info()))
      return self.FAILURE


  #
  #INSERT operation
  #
  def dbinsert(self, tablename, colvaldict):
    self.baselogger.info("Running base.dbinsert()...")
    space           = " "
    comma           = ","
    equals          = "="
    andclause       = ""
    insertclause    = "INSERT "
    intoclause      = "INTO "
    columnlist      = ""
    valuesclause    = "VALUES "
    valueslist      = ""
    executionresult = ""
    if tablename:
      intoclause = intoclause + space + tablename + space
    else:
      self.baselogger.error("TABLENAME not provided.")
    if colvaldict:
      keyslist = list(colvaldict.keys())
      columnlist = "("
      valueslist = "("
      for i in range(len(keyslist)):
        if i == (len(keyslist) - 1):
          columnlist = columnlist + str(keyslist[i])
          valueslist = valueslist + '"' + str(colvaldict[keyslist[i]]) + '"'
        else:
          columnlist = columnlist + str(keyslist[i]) + comma + space
          valueslist = valueslist + '"' + str(colvaldict[keyslist[i]]) + '"' + comma + space
      columnlist = columnlist + ")" + space
      valueslist = valueslist + ")" + space
    else:
      self.baselogger.error("Column and values input is not provided.")
    insertquery = insertclause + intoclause + columnlist + valuesclause + valueslist
    try:
      with self.connection:
        cursor = self.connection.cursor()
        cursor.execute(insertquery)
        cursor.close()
        return self.SUCCESS
    except:
      self.baselogger.error("The INSERT operaton has failed.")
      self.baselogger.error("Message - {0}".format(sys.exc_info()))
      return self.FAILURE


  #
  #UPDATE operation
  #
  def dbupdate(self, tablename, colvaldict, keyvaluepairs):
    self.baselogger.info("Running base.dbupdate()...")
    updateclause    = "UPDATE "
    setclause       = "SET "
    whereclause     = "WHERE "
    andclause       = ""
    space           = " "
    comma           = ","
    equals          = "="
    andstatement    = "AND "
    executionresult = ""
    if tablename:
      updateclause = updateclause + tablename + space
    else:
      self.baselogger.error("TABLENAME is not provided. ")
    if colvaldict:
      keyslist = list(colvaldict.keys())
      for i in range(len(keyslist)):
        if i == (len(keyslist) - 1):
          setclause = setclause + keyslist[i] + equals + '"' + colvaldict[keyslist[i]] + '"' + space
        else:
          setclause = setclause + keyslist[i] + equals + '"' + colvaldict[keyslist[i]] + '"' + comma + space
    else:
      self.baselogger.error("SET clause parameters 'colvaldict' is not provided. ")
      return self.FAILURE
      sys.exit()
    if keyvaluepairs:
      runonce = 0
      for key, value in keyvaluepairs.items():
        if not runonce:
          whereclause = whereclause + key + equals + '"' + value + '"' + space
          runonce = 1
        else:
          andclause = andclause + andstatement + key + equals + '"' + value + '"' + space
    else:
      self.baselogger.error("Filter parameters 'keyvaluepairs' is not provided. ")
      return self.FAILURE
      sys.exit()
    updatequery = updateclause + setclause + whereclause + andclause
    try:
      with self.connection:
        cursor = self.connection.cursor()
        executionresult = cursor.execute(updatequery)
        cursor.close()
    except:
      self.baselogger.error("The UPDATE operaton has failed. ")
      self.baselogger.error("Message - {0}".format(traceback.format_exc()))
      return self.FAILURE
    finally:
      if executionresult:
        self.baselogger.info("The UPDATE operation completed successfully.")
        return self.SUCCESS
      else:
        self.baselogger.error("The UPDATE operation failed for unknown reason. ")
        return self.FAILURE


  #
  #DELETE operation
  #
  def dbdelete(self, tablename, keyvaluepairs):
    deleteclause = "DELETE "
    fromclause   = "FROM "
    whereclause  = "WHERE "
    andclause    = ""
    space        = " "
    comma        = ","
    equals       = "="
    andstatement = "AND "
    if tablename:
      fromclause = fromclause + tablename + space
    else:
      self.baselogger.error("TABLENAME is not provided. ")
      return self.FAILURE
      sys.exit()
    if keyvaluepairs:
      runonce = 0
      for key, value in keyvaluepairs.items():
        if not runonce:
          whereclause = whereclause + key + equals + '"' + value + '"' + space
          runonce = 1
        else:
          andclause = andclause + andstatement + key + equals + '"' + value + '"' + space
    else:
      self.baselogger.error("Filter parameters 'keyvaluepairs' is not provided. ")
      return self.FAILURE
      sys.exit()
    deletequery = deleteclause + fromclause + whereclause + andclause
    try:
      with self.connection:
        cursor = self.connection.cursor()
        executionresult = cursor.execute(deletequery)
        cursor.close()
    except MySQLdb.IntegrityError:
      self.baselogger.error("The DELETE operaton has failed. ")
      return self.FAILURE
    finally:
      if executionresult:
        self.baselogger.info("The DELETE operation completed successfully. ")
        return self.SUCCESS
      else:
        self.baselogger.error("The DELETE operation failed for unknown reason. ")
        return self.FAILURE




#testing/debug
#scolumns       = ['chillout', 'party', 'weekendtrip']
#skeyvaluepairs = {'category' : 'active'}
#srowcount      = ""
#keyvaluepairs  = {'wherestring' : '', 'andstring' : ''}
#rowcount       = 3
#colvaldict     = {'entity' : 'flight', 'provider' : 'skyscanner', 'purpose' : 'search_entity_list', 'url' : 'http://partners.api.skyscanner.net/apiservices', 'version' : 'v1.0', 'endPoint' : 'pricing', 'authKeyName1' : 'apiKey', 'authKeyValue1' : 'tr587732112773421189195253963528'}
#dkeyvaluepairs = {'provider' : 'uber'}
#tablename      = "categorydna"
#ukeyvaluepairs = {'provider' : 'skyscanner'}
#ucolvaldict    = {'token' : 'dummytoken1'}

#instance = base('user1', 'test1')
#instance.dbinit("algometadata")
#print ("dbselect running...")
#dbdata = instance.dbselect(tablename, columns, keyvaluepairs, rowcount)
#print(dbdata)
#print ("dbinsert running...")
#instance.dbinsert(tablename, colvaldict)
#print ("dbselect running...")
#dbdata = instance.dbselect(tablename, srowcount, scolumns, skeyvaluepairs)
#print(dbdata)
#print (dbdata)
#instance.dbdummy()
#print ("dbupdate running...")
#instance.dbupdate(tablename, ucolvaldict, ukeyvaluepairs)
#print ("dbdelete running...")
#instance.dbdelete(tablename, dkeyvaluepairs)
#instance.dbclose()
