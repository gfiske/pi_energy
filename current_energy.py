#!/usr/bin/python
#current_energy.py

import MySQLdb
import ConfigParser

###############################################################
config = ConfigParser.RawConfigParser()
config.read('/home/pi/gfiske.cfg')
db_user = config.get('section1', 'db_user')
db_passwd = config.get('section1', 'db_passwd')
db_user = db_user.decode('base64','strict')
db_passwd = db_passwd.decode('base64','strict')
###############################################################

#connect to db
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
#do query on trend table
myq = "select * from trend order by ts1 desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()
timestamp = str(myq[1])
temp = float(myq[2]) - 5.0
netwatts = myq[3]
oldpv = myq[4]
newpv = myq[5]
totalpv = myq[6]
hvac = myq[7]
db.commit()
db.close()

#report to user
print
print "Current timestamp: " + timestamp
print "Basement temperature is: " + str(round(temp,2))
print "Current netwatts is: " + str(round(netwatts,2))
print "Old PV system is producing: " + str(round(oldpv,2))
print "New PV system is producing: " + str(round(newpv,2))
print "Total PV production is: " + str(round(totalpv,2))
print "HVAC is using: " + str(round(hvac,2))
print