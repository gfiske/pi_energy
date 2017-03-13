#test script to read 1 wire temperature sensor in the kitchen

import time
import os
import forecastio

file_name = os.path.join("/","mnt","1wire","28.ED548F050000","temperature")
file_name2 = os.path.join("/","mnt","1wire","28.2B9F8F050000","temperature")
file_name3 = os.path.join("/","mnt","1wire","28.FFD646451603","temperature")

file_object = open(file_name, 'r')
line = file_object.read()
line2 = (float(line)*1.8)+32.0
print
print "kitchen temperature: " + str(line2)
file_object.close()

file_object = open(file_name2, 'r')
line = file_object.read()
line2 = (float(line)*1.8)+32.0
print "solar tank temperature: " + str(line2)
file_object.close()

#file_object = open(file_name3, 'r')
#line = file_object.read()
#line3 = (float(line)*1.8)+32.0
#print "basement temperature is: " + str(line3)
#print
#file_object.close()

#get outdoor temp using gpio
# code modified from the samples on this page: https://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')

temp_sensor = "/sys/bus/w1/devices/28-03164546d6ff/w1_slave"

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = temp_raw()
    temp_output = lines[1].find('t=')
    temp_string = lines[1].strip()[temp_output+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return str(temp_f)    

print("outdoor temperature from local sensor: " + read_temp())
print
print

#get outdoor temp from darksky
forecast = forecastio.load_forecast('72348bae4adf606ce385c7782fc681b4', 41.5982, -70.5927)
current = forecast.currently()
darkSkyF = current.temperature

print
print "And outdoor temperature from DarkSky: " + str(darkSkyF)
print
