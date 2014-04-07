#!/usr/bin/python
#db_daily_stats5.py
#this script aggregates energy statistics from the frame hourly table in the mysql db
#it populates the frame2 daily table

import MySQLdb
import gdata.spreadsheet.service
import base64
import ConfigParser
import time


###############################################################
config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
g_user = config.get('section1', 'g_user')
g_passwd = config.get('section1', 'g_passwd')
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
email = g_user.decode('base64','strict')
password = g_passwd.decode('base64','strict')[0:15]
spreadsheet_name = 'home_dials'
###############################################################
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
myq = "select date(ts1) ,sum(watthours) / 1000 as 'net', sum(oldpv)/1000 as oldpv, sum(newpv)/1000 as enphase,sum(totalpv) / 1000 as 'total_pv',sum(hvac) / 1000 as 'total_hvac', avg(outtemp) as meanouttemp from frame group by date(ts1) desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()

#parse results of query
ts = str(myq[0])
net = str(round(myq[1],2))
oldpv = str(round(myq[2],2))
enphase = str(round(myq[3],2))
totalpv = str(round(myq[4],2))
hvac = str(round(myq[5],2))
meanouttemp = str(round(myq[6],2))
#################################
#update frame table
myquery = "insert into frame2 values (DEFAULT, NOW()," + net + "," + oldpv + "," + enphase + "," + totalpv + "," + hvac + "," + meanouttemp + ");"
cursor = db.cursor()
cursor.execute(myquery)
db.commit()
db.close()

###############################################################
#send daily info also to google spreadsheet titled daily_energy_from_pi
spreadsheet_key = '0Aj5_4a6W2d6JdC1sMU9jZjc1bE9ORU8yTWFKdERUSmc'
worksheet_id = 'od6'
myspreadsheetclient = gdata.spreadsheet.service.SpreadsheetsService()
myspreadsheetclient.email = email
myspreadsheetclient.password = password
myspreadsheetclient.source = 'Example Spreadsheet Writing Application'
myspreadsheetclient.ProgrammaticLogin()
###############################################################
# Prepare the dictionary to write
dict = {}
dict['ts1'] = ts
dict['net'] = net
dict['oldpv'] = oldpv
dict['newpv'] = enphase
dict['totalpv'] = totalpv
dict['hvac'] = hvac
dict['meanouttemp'] = meanouttemp
#print dict

#enter the data into the google spreadsheet
try:
    entry = myspreadsheetclient.InsertRow(dict, spreadsheet_key, worksheet_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
        print "Insert row succeeded."
except Exception, msg:
    print "Insert row failed."
    filename = "/home/pi/db_error_log.txt"
    f = open(filename,"r+")
    f.readlines()
    now = time.localtime(time.time())
    curtime = time.asctime(now)
    f.write(curtime + "\n")
    f.write("db_daily_stats5 error is : " + str(msg) + "\n")
    f.write("\n")
    f.close()