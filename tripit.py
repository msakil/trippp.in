import sys
from sys import argv
import sys, getopt
import http.client
import json
import urllib.parse
import requests
from base import base
from geopy.geocoders import Nominatim
import pprint
import math
from time import sleep
import logging
import logging.handlers
import hmac
import datetime
import traceback
import pprint
from collections import Counter
import configparser


class tripit:
  #
  #initializer, 'argv' parameter is used only for debugrun() function, when calling runfromserver()
  #function a dummy 'argv' parameter is supplied.
  #
  def __init__(self, argv):
    self.argv = argv
    self.baseinstance = base('user1', 'test1')
    self.SUCCESS = 0
    self.FAILURE = 1
    LOG_FILENAME = "logs/tripit.log"
    self.tlogger = logging.getLogger('tripit')
    self.tlogger.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s %(filename)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
    thandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=15000000, backupCount=5)
    thandler.setFormatter(logformat)
    self.tlogger.addHandler(thandler)
    self.tlogger.handlers[0].doRollover()


  #
  #Usage function,called in case of incorrect args to debugrun() or runfromserver()
  #
  def usage(self):
    print (
           'Usage: ' + sys.argv[0] + ' -p <purpose> ' + ' -e <experience> ' + ' -b <budget> ' \
           + ' -o <origin> ' + ' --outbounddate <departure date - yyyy-mm-dd> ' \
           + ' --arrivaldate <arrival date - yyyy-mm-dd>' + ' --adults <no. of passengers> '
          )


  #
  #Get name of nearest city with airport
  #
  def nearestairport(self, cityname):
    searchrad   = 300
    earthrad    = 6371
    minlat      = ""
    maxlat      = ""
    minlong     = ""
    maxlong     = ""
    wherestring = ""
    andstring   = ""
    angrad      = ""
    dboutput    = ""
    geolocator  = Nominatim()
    userlatlong = geolocator.geocode(cityname)
    sleep(1)
    userlat = math.radians(userlatlong.latitude)
    userlong = math.radians(userlatlong.longitude)
    angrad = (searchrad / earthrad)
    deltalong = math.asin(math.sin(angrad)/math.cos(userlat))
    minlat = userlat - angrad
    maxlat = userlat + angrad
    minlong = userlong - deltalong
    maxlong = userlong + deltalong
    wherestring = "(RADIANS(latitude) >= {0} AND RADIANS(latitude) <= {1})".format(minlat, maxlat)
    andstring1 = "(RADIANS(longitude) >= {0} AND RADIANS(longitude) <= {1})".format(minlong, maxlong)
    andstring2 = "acos(sin({0}) * sin(RADIANS(latitude)) + cos({0}) * cos(RADIANS(latitude)) * "\
                 "cos(RADIANS(longitude) - ({1}))) <= {2}".format(userlat, userlong, angrad)
    andstring3 = "airportcity NOT IN ('{0}')".format(cityname)
    tablename = "airportcities"
    reqcolumns = ['airportcity']
    selectparams = {"wherestring" : wherestring, "andstring1" : andstring1, "andstring2" : andstring2,
                    "andstring3" : andstring3}
    try:
      self.baseinstance.dbinit('apimetadata')
      dboutput = self.baseinstance.dbselect(tablename, rowcount="", columns=reqcolumns,
                                            keyvaluepairs=selectparams)
    except:
      self.tlogger.error("Unable to get required info from database due to unknown errors.")
      self.tlogger.error("Message - {0}".format(traceback.format_exc()))
      return self.FAILURE
    finally:
      self.baseinstance.dbclose()
    if dboutput:
      airportcities = dboutput
      return airportcities
    else:
      self.tlogger.error("No database output received.")
      return self.FAILURE


  #
  #Create provider specific url and headers
  #
  def buildurl(self, entity, provider):
    self.tlogger.info("Running tripit.buildurl()...")
    requesturl = ""
    self.baseinstance.dbinit('apimetadata')
    if entity and provider:
      try:
        dbdata = self.baseinstance.dbselect(
                                            'urlpieces',
                                            rowcount="",
                                            columns=['url'],
                                            keyvaluepairs={'entity' : entity, 'provider' : provider}
                                           )
        requesturl = str(dbdata[0][0])
      except:
        self.tlogger.error("Unable to get required info from database due to unknown errors.")
        self.tlogger.error("Message - {0}".format(traceback.format_exc()))
        return self.FAILURE
      finally:
        self.baseinstance.dbclose()
    else:
      self.tlogger.error("Message - Inputs 'provider' and 'entity' not provided.")
      return self.FAILURE
    return requesturl


  #
  #Authentication
  #
  def authenticate():
    self.tlogger.info("Authentication")


  #
  #Request operations
  #
  def request(self, url, operation, headers, parameters):
    self.tlogger.info("Running tripit.request()...")
    post    = "POST"
    get     = "GET"
    put     = "PUT"
    output  = ""
    if url:
      if operation == post:
        try:
          output = requests.post(url, data = parameters, headers=headers)
          if output is not None:
            self.tlogger.info("Requested operation '{0}' successful.".format(operation))
        except:
          self.tlogger.error("Requested Operation '{0}' failed  due to unknown errors.".format(operation))
          return self.FAILURE
      elif operation == get:
         try:
           sleep(1)
           output = requests.get(url, headers=headers)
           if output is not None:
             self.tlogger.info("Requested operation '{0}' successful.".format(operation))
         except:
           self.tlogger.error("Requested Operation '{0}' failed due to unknown errors.".format(operation))
           return self.FAILURE
      elif operation == put:
        self.tlogger.info("PUT operation")
    else:
      self.tlogger.error("Message - Required input 'url' not provided. \n")
    return output


  #
  #Response handling
  #
  def response(self, skypolldata):
    self.tlogger.info("Response")


  #
  #Get list of entities
  #
  def search(self, parameters, entity):
    self.tlogger.info("Running search...")
    dbdata           = ""
    provider         = ""
    searchdata       = ""
    geolocator       = Nominatim()
    skyurl           = ""
    skypollurl       = ""
    userorigin       = ""
    userdest         = ""
    originlatlong    = ""
    destlatlong      = ""
    approxorigin     = ""
    approxdest       = ""
    skysessiondata   = ""
    skypolldata      = ""
    originlists      = ""
    destlists        = ""
    citynotfound     = ""
    listcount        = ""
    yelpurl          = ""
    today            = ""
    tokenstartdate   = ""
    tokenenddate     = ""
    validtoken       = ""
    yelpclientid     = ""
    yelpclientsecret = ""
    yelptokenurl     = ""
    yelptokendata    = ""
    tokenupdate      = ""
    pp               = pprint.PrettyPrinter(indent=2, width=20)
    try:
      self.baseinstance.dbinit('apimetadata')
      dbdata = self.baseinstance.dbselect(
                                          'urlpieces',
                                          rowcount="",
                                          columns=['provider'],
                                          keyvaluepairs={'entity' : entity}
                                          )
      if dbdata:
        provider = str(dbdata[0][0])
    except:
      self.tlogger.error("Unable to get required info from database due to unknown errors.")
      self.tlogger.error("Message - {0}".format(traceback.format_exc()))
      return self.FAILURE
    finally:
      self.baseinstance.dbclose()
    if provider == "skyscanner":
      self.tlogger.info("Getting flight data...")
      skyurl = self.buildurl(entity, provider)
      headers = {'Accept': 'application/json', 'Content-type': 'application/x-www-form-urlencoded'}
      parameters['apiKey'] = "tr587732112773421189195253963528"
      parameters['locale'] = "en-GB"
      if parameters['originplace'] and parameters['destinationplace']:
        userorigin = parameters['originplace']
        userdest = parameters['destinationplace']
        try:
          sleep(1)
          originlatlong = geolocator.geocode(userorigin)
          if originlatlong is not None:
            originlatlong = str(originlatlong.latitude) + "," + str(originlatlong.longitude)
            parameters['originplace'] = originlatlong + "-Latlong"
          else:
            self.tlogger.error("Unable to get lat-long for the location '{0}'. Please recheck location " \
                               "name.".format(userorigin))
            return self.FAILURE
          sleep(1)
          destlatlong = geolocator.geocode(userdest)
          if destlatlong is not None:
            destlatlong = str(destlatlong.latitude) + "," + str(destlatlong.longitude)
            parameters['destinationplace'] = destlatlong + "-Latlong"
          else:
            self.tlogger.error("Unable to get lat-long for the location '{0}'. Please recheck location " \
                               "name.".format(userdest))
            return self.FAILURE
        except:
          if not originlatlong:
            self.tlogger.error("Could not get lat-long for the location '{0}'".format(userorigin))
          elif not destlatlong:
            self.tlogger.error("Could not get lat-long for the location '{0}'".format(userdest))
          self.tlogger.error("Message - {0}".format(traceback.format_exc()))
          return self.FAILURE
      else:
        self.tlogger.error("Required inputs 'originplace' and 'destinationplace' not provided.")
        return self.FAILURE
      skysessiondata = self.request(skyurl, "POST", headers, parameters)
      #skyscanner updated the status_code to '200' but seems like my old api key still has '201' configured
      if str(skysessiondata.status_code) == "201":
        skypollurl = skysessiondata.headers['location']
      elif str(skysessiondata.status_code) == "400":
        listcount = 0
        citynotfound = "Airport not found within 100 miles of this location"
        if skysessiondata.json()["ValidationErrors"][0]["Message"] == citynotfound:
          self.tlogger.info("Status code - 400, incorrect cityname.")
          if skysessiondata.json()["ValidationErrors"][0]["ParameterName"] == "OriginPlace":
            originlists = self.nearestairport(userorigin)
            listcount = len(originlists)
            self.tlogger.info("Incorrect 'Originplace' - {0}".format(userorigin))
          if skysessiondata.json()["ValidationErrors"][0]["ParameterName"] == "DestinationPlace":
            destlists = self.nearestairport(userdest)
            if len(destlists) > listcount:
              listcount = len(destlists)
            self.tlogger.info("Incorrect 'DestinationPlace' - {0}".format(userdest))
          self.tlogger.info("Trying with the nearest city with airport...")
          for i in range(listcount):
            if originlists and i<len(originlists):
              if originlists[i][0]:
                approxorigin = originlists[i][0]
                self.tlogger.info("New OriginPlace - {0}".format(approxorigin))
                try:
                  sleep(1)
                  originlatlong = geolocator.geocode(approxorigin)
                  if originlatlong is not None:
                    originlatlong = str(originlatlong.latitude) + "," + str(originlatlong.longitude)
                    parameters['originplace'] = originlatlong + "-Latlong"
                except:
                  if not originlatlong:
                    self.tlogger.error("Could not get lat-long for the location '{0}'".format(approxorigin))
                  self.tlogger.error("Message - {0}".format(traceback.format_exc()))
                  return self.FAILURE
            if destlists and i<len(destlists):
              if destlists[i][0]:
                approxdest = destlists[i][0]
                self.tlogger.info("New destinationPlace - {0}".format(approxdest))
                try:
                  sleep(1)
                  destlatlong = geolocator.geocode(approxdest)
                  if destlatlong is not None:
                    destlatlong = str(destlatlong.latitude) + "," + str(destlatlong.longitude)
                    parameters['destinationplace'] = destlatlong + "-Latlong"
                except:
                  if not destlatlong:
                    self.tlogger.error("Could not get lat-long for the location '{0}'".format(approxdest))
                  self.tlogger.error("Message - {0}".format(traceback.format_exc()))
                  return self.FAILURE
            skysessiondata = self.request(skyurl, "POST", headers, parameters)
            #skyscanner updated the status_code to '200' but seems like my old api key still has '201'
            #configured
            if str(skysessiondata.status_code) == "201":
              skypollurl = skysessiondata.headers['location']
              break
        else:
          self.tlogger.error("Unable to get 'skypollurl' for unknown reason")
          self.tlogger.error("Skyscanner status_code - {0}".format(skysessiondata.status_code))
          self.tlogger.error("Skyscanner output - {0}".format(skysessiondata.json()))
      else:
        self.tlogger.error("Problems getting polling url for querying flight data from Skyscanner.")
        self.tlogger.error("Message - Complete output JSON...")
        self.tlogger.error("Response status code : {0}".format(skysessiondata.status_code))
        self.tlogger.info(skysessiondata.json())
        return self.FAILURE
      if skypollurl != "":
        skyurl = skypollurl + "?apiKey=" + parameters['apiKey']
        skypolldata = self.request(skyurl, "GET", headers, parameters=[])
      elif str(skysessiondata.status_code) == "400":
        self.tlogger.error("No city with an airport found within 186 miles of given origin place or destination place.")
        return self.FAILURE
      else:
        self.tlogger.error("'skypollurl' empty for unknown reason.")
        return self.FAILURE
      if str(skypolldata.status_code) == "200":
        searchdata = skypolldata.json()
        if approxorigin == "" and approxdest == "":
          self.tlogger.info("Filghts from {0} to {1} - {2}".format(userorigin, userdest, searchdata))
        elif approxorigin != "" and approxdest != "":
          self.tlogger.info("Flights from {0} to {1} - {2}".format(approxorigin, approxdest, searchdata))
        elif approxorigin == "" and approxdest != "":
          self.tlogger.info("Flights from {0} to {1} - {2}".format(userorigin, approxdest, searchdata))
        elif approxorigin != "" and approxdest == "":
          self.tlogger.info("Flights from {0} to {1} - {2}".format(approxorigin, userdest, searchdata))
      else:
        self.tlogger.error("Unable to get flight data.")
        self.tlogger.error("Status code - {0}".format(skypolldata.status_code))
    elif provider == "yelp":
      self.tlogger.info("Getting events data for {0}...".format(parameters['location']))
      yelpurl = self.buildurl(entity, provider)
      if yelpurl != self.FAILURE:
        yelpurl = "{0}/businesses/search?location={1}&limit=50".format(yelpurl, parameters['location'])
      else:
        self.tlogger.error("Unable to get base url for yelp from database.")
        return self.FAILURE
      today = datetime.datetime.date(datetime.datetime.now())
      if today is tokenenddate:
        self.tlogger.info("Getting new access token from yelp...")
        yelpclientid = "swEnRaILTE6jRXaHHoVaPA"
        yelpclientsecret = "dODpZKsiCvydzGSAezbQWRFzklvdr7JeOUTiZ4kXU09o0X4TECph74s37618dsPu"
        yelptokenurl = "https://api.yelp.com/oauth2/token?grant_type=client_credentials&client_id={0}" \
                       "&client_secret={1}".format(yelpclientid, yelpclientsecret)
        yelptokendata = self.request(yelptokenurl, "POST", headers={}, parameters={})
        if str(yelptokendata.status_code) == "200":
          validtoken = yelptokendata.json()['access_token']
          tokenstartdate = today
          tokenenddate = tokenstartdate + datetime.timedelta(seconds=14947200)
          self.tlogger.info("Persisting new access token to the database...")
          try:
            self.baseinstance.dbinit('apimetadata')
            tokenupdate = self.baseinstance.dbupdate(
                                                     'accesstokens',
                                                     colvaldict={'token' : validtoken},
                                                     keyvaluepairs={'provider' : 'yelp'}
                                                    )
          except:
            self.tlogger.error("Unable to update table with new access token.")
            self.tlogger.error("Message - {0}".format(traceback.format_exc()))
            self.baseinstance.dbrollback()
          finally:
            if tokenupdate == self.SUCCESS:
              self.tlogger.info("New access token from yelp updated to database successfully.")
              self.baseinstance.dbcommit()
            else:
              self.tlogger.info("Update of new access token from yelp to database failed.")
            self.baseinstance.dbclose()
        else:
          self.tlogger.error("Unable to get token from yelp.")
          self.tlogger.error("Message - {0}".format(yelptokendata.json()))
          return self.FAILURE
      else:
        try:
          self.baseinstance.dbinit('apimetadata')
          validtoken = self.baseinstance.dbselect(
                                                  'accesstokens',
                                                  rowcount="",
                                                  columns=['token'],
                                                  keyvaluepairs={'provider' : 'yelp'}
                                                 )
          if validtoken is not None:
            validtoken = str(validtoken[0][0])
          self.baseinstance.dbclose()
        except:
          self.tlogger.error("Unable to get token from database.")
          self.tlogger.error("Message - {0}".format(traceback.format_exc()))
          self.baseinstance.dbclose()
          return self.FAILURE
      yelpaccesstoken = "Bearer {0}".format(validtoken)
      yelpheaders = {'Authorization': yelpaccesstoken}
      yelpdata = self.request(yelpurl, "GET", yelpheaders, parameters={})
      if yelpdata != self.FAILURE:
        if str(yelpdata.status_code) == "200":
          searchdata = yelpdata.json()
          self.tlogger.info("Successfuly got events happenning at {0}".format(parameters['location']))
          #self.tlogger.info("Events happenning at {0} : {1}".format(parameters['location'], yelpdata.json()))
        else:
          self.tlogger.error("Unable to get data from yelp.")
          self.tlogger.error("Response status code - {0}".format(yelpdata.status_code))
          self.tlogger.error("Output from yelp - {0}".format(yelpdata))
      else:
        self.tlogger.error("Unable to get data from yelp for unknown reason.")
        self.tlogger.error("yelp output - {0}".format(yelpdata.json()))
        return self.FAILURE
    else:
      self.tlogger.error("Specified provider not found.")
      return self.FAILURE
    if searchdata != "":
      return searchdata
    else:
      return self.FAILURE


  #
  #Recommend destination to user based on purpose, experience and budget
  #
  def recommend(self, purpose, experience, budget):
    self.tlogger.info("Running recommend...")
    flavours         = []
    refreshlocations = "false"
    config           = configparser.ConfigParser()
    searchparams     = {}
    citieslist       = []
    yelpcity         = ""
    titlelist        = []
    categorylist     = []
    categorydata     = ""
    categorycount    = {}
    dbdata           = ""
    flavourpoint     = 0
    flavourscore     = 0
    cityscores       = {}
    recommendedcity  = ""
    if "chillout" in experience.lower():
      flavours.append("chillout")
    if "party" in experience.lower():
      flavours.append("party")
    if "weekendtrip" in experience.lower():
      flavours.append("weekendtrip")
    if "countryexploration" in experience.lower():
      flavours.append("explorecountry")
    if "skiing" in experience.lower():
      flavours.append("skiing")
    if "familyvacation" in experience.lower():
      flavours.append("familyvacation")
    #refreshing locations data to update locationdna.ini file
    refreshlocations = "false"
    if refreshlocations is "true":
      config.read("config/yelpcities.ini")
      citieslist = config.get('yelpcities', 'city').replace('\n', '').split(',')
      #querying each city for businesses
      for yelpcity in citieslist:
        if flavourscore > 0:
          flavourscore = 0
        if len(titlelist) > 0:
          titlelist.clear()
        if len(categorylist) > 0:
          categorylist.clear()
        if len(categorycount) > 0:
          categorycount.clear()
        searchparams['location'] = yelpcity
        self.tlogger.info("Getting top 50 businesses in {0}".format(yelpcity))
        searchdata = self.search(searchparams, "events")
        self.tlogger.debug("Top 50 businesses in {0} - {1}".format(yelpcity, searchdata))
        self.tlogger.info("Extracting titles of each of the 50 businesses")
        if searchdata != self.FAILURE:
          for i in range(len(searchdata['businesses'])):
            if searchdata['businesses'][i]['categories']:
              titlelist.append(searchdata['businesses'][i]['categories'][0]['title'])
          self.tlogger.info("titlelist - {0}".format(titlelist))
        else:
          self.tlogger.error("Unable to get top 50 businesses in {0} for unknown reason".format(yelpcity))
          continue
        self.tlogger.info("Extracting category and category count from titlelist...")
        with open('config/categories.json', 'r') as categoryfile:
          categorydata = json.load(categoryfile)
        for i in range(len(titlelist)):
          for j in range(len(categorydata)):
            if categorydata[j]:
              if categorydata[j]['title'] == titlelist[i]:
                if categorydata[j]['parents']:
                  categorylist.append(categorydata[j]['parents'][0])
        if categorylist:
          categorycount = dict(Counter(categorylist))
          categorylist = list(set(categorylist))
          self.tlogger.info("categorylist - {0}".format(categorylist))
          self.tlogger.info("categorycount - {0}".format(categorycount))
          config.read("config/locationdna.ini")
          config[yelpcity] = categorycount
          with open('config/locationdna.ini', 'w') as configfile:
            config.write(configfile)
        else:
          self.tlogger.error("'categorylist' empty. Unable to extract category and category count")
          return self.FAILURE
    #refresh complete
    self.tlogger.info("Getting flavour scores for induvidual cities")
    #clearing since 'citieslist' is a reused variable
    if citieslist:
      citieslist.clear()
    #clearing since categorycount is a reused variable
    if categorycount:
      categorycount.clear()
    #clearing since categorylist is a reused variable
    if categorylist:
      categorylist.clear()
    config.read("config/yelpcities.ini")
    citieslist = config.get('yelpcities', 'city').replace('\n', '').split(',')
    config.read("config/locationdna.ini")
    for yelpcity in citieslist:
      if flavourscore > 0:
        flavourscore = 0
      categorycount = dict(config.items(yelpcity))
      self.tlogger.info("Yelp city - {0} categorycount - {1}".format(yelpcity, categorycount))
      categorylist = list(categorycount.keys())
      for category in categorylist:
        flavourpoint = 0
        try:
          self.baseinstance.dbinit('algometadata')
          dbdata = self.baseinstance.dbselect(
                                              'categorydna',
                                              rowcount="",
                                              columns=flavours,
                                              keyvaluepairs={'category' : category}
                                              )
        except:
          self.tlogger.error("Unable to get flavourpoint - {0} for category {1} from database " \
                             "table categorydna for unknown reasons.".format(flavours, category))
          self.tlogger.error("Message - {0}".format(traceback.format_exc()))
          continue
        finally:
          self.baseinstance.dbclose()
        if dbdata is not None and dbdata[0] is not None:
          for i in range(len(dbdata[0])):
            flavourpoint = dbdata[0][i]
            flavourscore = flavourscore + (flavourpoint * int(categorycount[category]))
        else:
          self.tlogger.error("Could not get flavourpoint - {0} for category - {1}, output from " \
                             "database table 'categorydna' is empty".format(flavours, category))
          continue
      self.tlogger.info("yelpcity - {0}, flavourscore - {1}".format(yelpcity, flavourscore))
      cityscores[yelpcity] = flavourscore
    self.tlogger.debug("cityscores - {0}".format(cityscores))
    recommendedcity = max(cityscores, key=cityscores.get)
    if recommendedcity != "":
      self.tlogger.info("The best city for purpose - {0} and experience - {1} within the budget of {2} " \
                        "is {3}".format(purpose, experience, budget, recommendedcity))
      return recommendedcity
    else:
      self.tlogger.error("Unable to get a city for the given purpose - {0} and experience - {1} within " \
                         "the budget of {2} for unknown reason".format(purpose, experience, budget))
      return self.FAILURE


  #
  #Get info about chosen entity
  #
  def getInfo(self):
    self.tlogger.info("Get Info")


  #
  #Perform ticket booking
  #
  def reserve(self):
    self.tlogger.info("Reserve")


  #
  #Cancel booking
  #
  def cancel(self):
    self.tlogger.info("Cancel")


  #
  #Sends back data to the calling server
  #
  def sendtoserver(self, outputdata):
    self.tlogger.info("Running sendtoserver...")
    print("Content-Type: text/html\r\n")
    print("")
    print(outputdata)


  #
  #Run function to execute the script from command line, used for debugging only
  #
  def debugrun(self):
    self.tlogger.info("Running 'debugrun' function...")
    purpose        = ""
    experience     = ""
    budget         = ""
    origin         = ""
    outbounddate   = ""
    #temprorary hardcode
    adults         = "2"
    arrivaldate    = ""
    country        = "US"
    currency       = "USD"
    flightparams   = {}
    destination    = ""
    flightdata     = ""
    try:
      opts, args = getopt.getopt(self.argv, "p:e:b:o:",["outbounddate=", "adults=", "arrivaldate="])
      if not opts:
        print("No arguments supplied.")
        self.tlogger.info("No arguments supplied.")
        self.usage()
        return self.FAILURE
    except getopt.GetoptError as err:
      self.tlogger.error(str(err))
      self.usage()
      return self.FAILURE
    for opt, arg in opts:
      if opt == "-p":
        purpose = str(arg)
      elif opt == "-e":
        experience = str(arg)
      elif opt == "-b":
        budget = str(arg)
        self.tlogger.debug("budget - {0}".format(budget))
      elif opt == "-o":
        origin = str(arg)
      elif opt == "--outbounddate":
        outbounddate = str(arg)
      elif opt == "--adults":
        adults = str(arg)
      elif opt == "--arrivaldate":
        arrivaldate = str(arg)
    if not purpose or not experience or not budget or not origin or not outbounddate:
      print("One or more mandatory arguments(-p, -e, -b, -o, --outbounddate) missing. "\
            "Please check inputs again.")
      self.tlogger.info("One or more mandatory arguments(-p, -e, -b, -o, --outbounddate) missing. "\
                        "Please check inputs again.")
      self.usage()
      return self.FAILURE
    flightparams = {
                    'originplace' : origin,
                    'adults' : adults,
                    'country' : country,
                    'currency' : currency,
                    'outbounddate' : outbounddate,
                    'format' : 'json',
                    'source' : origin,
                    'dateofdeparture' : outbounddate,
                    'dateofarrival' : arrivaldate
                   }
    destination = self.recommend(purpose, experience, budget)
    if destination == self.FAILURE:
      self.tlogger.error("Unable to recommend a suitable destination based for input Purpose - {0}," \
                         "Experience - {1}, and Budget - {2}".format(purpose, experience, budget))
      return self.FAILURE
    else:
      self.tlogger.info("Recommended place - {0}".format(destination))
      flightparams['destinationplace'] = destination
      #flightdata = self.search(flightparams, "flight")
      self.tlogger.info("Flight from {0} to {1} - {2}".format(origin, destination, flightdata))
      return flightdata


  #
  #Function called by client to execute script from the server
  #
  def runfromserver(self, argdict):
    self.tlogger.info("Running 'runfromserver' function...")
    #temp hardcode
    adults         = "1"
    arrivaldate    = ""
    country        = "US"
    currency       = "USD"
    flightparams   = {}
    destination    = ""
    flightdata     = ""
    errormsg       = ""
    if (not argdict['purpose'] or not argdict['experience'] or not argdict['budget']
          or not argdict['origin'] or not argdict['outbounddate']):
      self.tlogger.info("One or more mandatory inputs(purpose, experience, budget, origin, outbounddate) missing. "\
                        "Please check inputs again.")
      self.tlogger.info("One or more mandatory inputs(purpose, experience, budget, origin, outbounddate) "\
                        " missing. Please check inputs again.")
      self.usage()
      errormsg = "One or more mandatory inputs(purpose, experience, budget, origin, outbounddate) "\
                 " missing. Please check inputs again."
      self.sendtoserver(errormsg)
    flightparams = {
                    'originplace' : argdict['origin'],
                    'adults' : adults,
                    'country' : country,
                    'currency' : currency,
                    'outbounddate' : argdict['outbounddate'],
                    'format' : 'json',
                    'source' : argdict['origin'],
                    'dateofarrival' : arrivaldate
                   }
    self.tlogger.debug("input parameters - {0}".format(argdict))
    self.tlogger.debug("flightparams - {0}".format(flightparams))
    destination = self.recommend(argdict['purpose'], argdict['experience'], argdict['budget'])
    if destination == self.FAILURE:
      self.tlogger.error("Unable to recommend a suitable destination based on input Purpose - {0}," \
                         "Experience - {1}, and Budget - {2}".format(argdict['purpose'],
                                                                     argdict['experience'],
                                                                     argdict['budget']))
      errormsg = "tripit.py crashed or did not work as expected for unknown reason."
      self.sendtoserver(errormsg)
    else:
      self.tlogger.info("Recommended place - {0}".format(destination))
      flightparams['destinationplace'] = destination
      flightdata = self.search(flightparams, "flight")
      self.tlogger.info("Flight from {0} to {1} - {2}".format(argdict['origin'], destination, flightdata))
      self.sendtoserver(destination)



#testing/debug
#instance = tripit(sys.argv[1:], opts={})
serverargs = {
              'purpose': "solo travel",
              'experience': "chillout, party",
              'budget': "$10,000",
              'origin': "New York",
              'outbounddate': "2016-10-29"
             }
instance = tripit(sys.argv[1:])
print ("Running trip module...")
print ("Calling run function...")
output = instance.debugrun()
#output = instance.runfromserver(serverargs)
#parsedoutput = json.dumps(output, indent=4)
#print (parsedoutput)
#instance.buildurl('flight', 'skyscanner')
#output = instance.nearestairport("mysore")
#print ("output : {0}".format(output))
