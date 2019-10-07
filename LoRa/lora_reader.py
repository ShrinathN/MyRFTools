#!/bin/python

import serial
import time

prt = serial.Serial('/dev/ttyUSB0', baudrate=115200)


while(True):
	data_read = prt.read(10)
	print(time.ctime())
	print('RegOpMode (0x01)\t->\t' + str(hex(data_read[0])))
	print('RegIrqFlags (0x12)\t->\t' + str(hex(data_read[1])))
	print('Bytes Received\t\t->\t' + str(int(data_read[2])))
	print('RSSI\t\t\t->\t' + str(-137 + data_read[4]) + 'dBm')
	try:
		print('Payload\t\t\t->\t' + str(data_read[5:], 'utf-8') + '\n\n')
	except:
		continue