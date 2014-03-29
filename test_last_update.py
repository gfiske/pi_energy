#!/usr/bin/python

#test_last_update.py
#this script tests the last update to the energy db
#if it is too long, there's a problem, populate error table

#written on 3/26/14

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
myq = "select timestampdiff(minute, now(), ts1) from trend order by ts1 desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()
diff = myq[0]
db.commit()

# if the time delay is greater than 2 minutes, populate error table
if int(diff) > -4 & int(diff) < -2:
    offtime = 1
    myq2 = "insert into error values (DEFAULT, NOW(), 1);"
    cursor.execute(myq2)
    db.commit()
else:
    myq2 = "insert into error values (DEFAULT, NOW(), 0);"
    cursor.execute(myq2)
    db.commit()
    offtime = 0
db.close()


