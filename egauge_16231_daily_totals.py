#!/usr/bin/env python
###############################################################################
# egauge_daily_totals.py 2015-12-10
#
# Project:  egauge
# Purpose:  The purpose of this script is to query the daily total energy data from the egauge device
#           and send it to both a local MySQL db and a Google Spreadsheet
#
# Author:   Greg Fiske, gfiske@whrc.org
#
###############################################################################
import MySQLdb
import xml.etree.ElementTree as ET # for XML parsing
import urllib, time
import json
import gspread
import base64
import ConfigParser
from oauth2client.client import SignedJwtAssertionCredentials
import os,sys,time
import string
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
spreadsheet_name = 'home_egauge16231'
###############################################################

# Enter eGauge name
eGauge = "egauge16231"
# Get XML from eGauge device
url = "http://" + eGauge + ".egaug.es/cgi-bin/egauge-show?m&n=2&s=1439&C"

#########################################
#          PULL FROM EGAUGE       #
#########################################
def pullFromDevice():
    # Parse the results
    tree = ET.parse(urllib.urlopen(url)).getroot()
    net = ((int(tree[0][7][0].text)) * -1) * 0.00000027778
    oldpv = abs(int(tree[0][7][1].text)) * 0.00000027778
    hvac = int(tree[0][7][3].text) * 0.00000027778
    enphase = abs(int(tree[0][7][4].text)) * 0.00000027778
    totalpv = oldpv + enphase
    return net,oldpv,enphase,totalpv,hvac

try:
    data = pullFromDevice()
except:
    print "device pull failed"

#########################################
#        Get Temperature Data           #
#########################################

db = MySQLdb.connect("127.0.0.1", db_user, db_passwd, "energy")
try:
    myq2 = "select avg(kitchTemp), min(outTemp), max(outTemp), avg(outTemp), avg(tankTemp), ((max(tankTemp)-min(tankTemp))*5421) from temperature where date(ts1) = date(now());"
    cursor = db.cursor()
    cursor.execute(myq2)
    myq2 = cursor.fetchone()
    meankitchtemp = round(myq2[0],2)
    minouttemp = round(myq2[1],2)
    maxouttemp = round(myq2[2],2)
    meanouttemp = round(myq2[3],2)
    meantanktemp = round(myq2[4],2)
    tankbtus = round(myq2[5],2)
except:
    print "temperature query failed"



#########################################
#        Update Google Spreadsheet      #
#########################################
json_key = json.load(open('/home/pi/pi_energy/raspPi-e0a08639ebab.json'))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
g = gspread.authorize(credentials)
    
# first the daily energy spreadsheet
try:
    rowToAdd = (time.strftime('%m/%d/%Y'),str(round(data[0],2)),str(round(data[1],2)),str(round(data[2],2)),str(round(data[3],2)), str(round(data[4],2)), str(meanouttemp)) #date, net,oldpv,enphase,totalpv,hvac,meanouttemp                
    worksheet = g.open('daily_energy_from_pi').get_worksheet(0)
    worksheet.append_row(rowToAdd)
    print "...energy row add success"
except:
    print "...energy row add fail"

# second update the daily tempearture spreadsheet
try:
    rowToAdd = (time.strftime('%m/%d/%Y'),str(meankitchtemp), str(minouttemp), str(maxouttemp), str(meanouttemp), str(meantanktemp), str(tankbtus))
    worksheet = g.open('daily_temperature_from_pi').get_worksheet(0)
    worksheet.append_row(rowToAdd)
    print "...temperature row add success"
except:
    print "...tempearture row add fail"
