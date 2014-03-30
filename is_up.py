#!/usr/bin/python

#is_up.py

#a general test script to see if everything is working with the RasPi energy logging
#Feb 2013
#updated March 2014

import os
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

# first test to see if the connection is good
hostname = "google.com"
response = os.system("ping -c 1 " + hostname)

#and then check the response...
if response == 0:
  #print 'is up!'
  pass
else:
  #print 'is down!'
  os.system("sudo ifup eth0")

#check for errors by running test_last_update.py
cmd = 'python /home/pi/pi_energy/test_last_update.py'
os.system(cmd)

#test to see if err code is 1 *bad* and if so run sendemail
db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
myq = "select ts1, err_code from error order by ts1 desc limit 1;"
cursor = db.cursor()
cursor.execute(myq)
myq = cursor.fetchone()
#parse results of query
errcode = myq[1]
db.commit()
if errcode == 1:
    cmd2 = 'python /home/pi/pi_energy/sendmail.py'
    os.system(cmd2)
    #myq2 = "insert into error values (DEFAULT, NOW(), 0);"
    #cursor.execute(myq2)
    #db.commit()

db.close()