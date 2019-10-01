#!/bin/python
import serial
import time
import threading
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import low_pass_filter

# try:
prt = serial.Serial('/dev/ttyUSB0', baudrate=2000000)
# except:
	# prt = serial.Serial('/dev/ttyUSB1', baudrate=2000000)

y = []
y_raw = []

canrun = True

def displayer():
	while(canrun):
		print('     ' + '\r' + str(len(y_raw)) + '\r')
		time.sleep(0.5)


threading.Thread(target=displayer, args=()).start()

try:
	print('Running')
	while(True):
		data = prt.read(102400)
		y_raw.extend(str(data,'utf-8'))
except KeyboardInterrupt:
	canrun = False
	for i in y_raw:
		y.append(int(i))
	print(len(y))
	x = list(np.arange(0, len(y)))
	n = np.array(x) / 100000
	z = low_pass_filter.LP_filter(y,10)

	fig = plt.figure(figsize=(60,3))
	axes= fig.add_axes([0.1,0.1,0.8,0.8])
	axes.plot(n,y)
	axes.plot(n,z)

	result,timing = low_pass_filter.decode_myprotocol_sync(y, 11)
	final_result = []
	for i in result:
		if(sum(i) != 0):
			final_result.append(i)

	print(final_result)

	plt.show()

	print('Save [y]: ', end='')
	if(input() == 'y'):
		df = pd.DataFrame({'values_raw' : y, 'values_filtered' : z})
		print(type(df))
		df.to_csv('data_log.csv')
