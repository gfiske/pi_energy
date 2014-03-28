#updates database trend1 table with data from Gregs CurrentCost meter
#Greg Fiske Feb 2013

#edited on 9/27/13 to include HVAC data
#edited on 9/29/13 to run continuously for more accurate db logging results
#edited on 11/2/13 to include try, except statements
#edited on 1/20/14 to include the live dial updates and gspread
#edited on 3/26/14 to include a better temperature default value and base64

import serial,sys,MySQLdb
import xml.etree.ElementTree as ET # for XML parsing
import json
import urllib2
import time
import gspread
import base64
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
g_user = config.get('section1', 'g_user')
g_passwd = config.get('section1', 'g_passwd')

###############################################################
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
email = g_user.decode('base64','strict')
password = g_passwd.decode('base64','strict')[0:15]
spreadsheet_name = 'home_dials'
###############################################################

ser = serial.Serial(port='/dev/ttyUSB0',baudrate=57600)
line = ser.readline()
#print line
#set up blank variables
totalwatts = 0
temp = 40
pv = 0
hvac = 0
enphasedata = 0

#########################################
#          PULL FROM CURRENT COST       #
#########################################

def pullFromCurrentCost():
    # Read XML from Current Cost.  Try again if nothing is returned.
    watts1  = None
    watts2 = None
    sensor = None
    while watts1 == None:
        line2 = ser.readline()
        try:
            tree  = ET.XML(line2)
            watts1  = tree.findtext("ch1/watts")
            watts2  = tree.findtext("ch2/watts")
            temp = tree.findtext("tmprF")
            sensor = tree.findtext("sensor")
        except Exception, inst: # Catch XML errors (occasionally the current cost outputs malformed XML)
            sys.stderr.write("XML error: " + str(inst) + "\n")
            line2 = None

    ser.flushInput()
    return temp, watts1, watts2, sensor

## Continuously call energy data from the current cost meter
while True:
    try:

        #########################################
        #          Organize sensor data         #
        #########################################
        totalwatts = totalwatts
        temp = temp
        pv = pv
        hvac = hvac
        enphasedata = enphasedata
        # run for first sensor
        data = pullFromCurrentCost()
        if int(data[3]) == 0:
            #then sensor 0
            totalwatts = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 1:
            #then sensor 1
            pv = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 2:
            #then sensor 2
            hvac = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        # run again for second sensor
        data = pullFromCurrentCost()
        if int(data[3]) == 0:
            #then sensor 0
            totalwatts = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 1:
            #then sensor 1
            pv = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 2:
            #then sensor 2
            hvac = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        # run again for third sensor
        data = pullFromCurrentCost()
        if int(data[3]) == 0:
            #then sensor 0
            totalwatts = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 1:
            #then sensor 1
            pv = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0
        if int(data[3]) == 2:
            #then sensor 2
            hvac = int(data[1]) + int(data[2])
            temp = float(data[0]) - 5.0

        #################################
        #get enphase system values
        #url to fiske enphase system
        url = "https://api.enphaseenergy.com/api/systems/62345/summary?&key=1dad77b9676fa86345f48482179e5835"
        try:
            #create a dictionary out of the enphase json return
            enphase = json.load(urllib2.urlopen(url))
            enphasedata = enphase["current_power"]
        except:
            enphasedata = enphasedata
        #################################
        # calc energy flow values

        #add in enphase data
        pvtotal = pv + enphasedata
        #correct pv data
        if pvtotal <= 15:
            pvtotal = 0

        #check for flow direction to get net
        if pvtotal > totalwatts:
            net = totalwatts * -1
        else:
            net = (totalwatts - pvtotal) - pvtotal


        #update db
        db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
        myquery2 = "insert into trend values (DEFAULT, NOW()," + str(temp) + "," + str(net) + "," + str(pv) + "," + str(enphasedata) + "," + str(pvtotal) + "," + str(hvac) + ");"
        mycleanupquery = "delete from trend order by id limit 1;"
        cursor = db.cursor()
        cursor.execute(myquery2)
        cursor.execute(mycleanupquery)
        db.commit()
        db.close()

        g = gspread.login(email, password)
        worksheet = g.open('home_dials').get_worksheet(0)
        worksheet.update_cell(2,1,str(net))
        worksheet.update_cell(2,2,str(pvtotal))
        worksheet.update_cell(2,3,str(hvac))

        #set in a rest period
        time.sleep(5)
    except Exception,msg:
        filename = "/home/pi/db_error_log.txt"
        f = open(filename,"w")
        f.write(msg)
        f.write('/n')
        f.close()