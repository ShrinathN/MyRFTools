#!/bin/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import low_pass_filter
import sys


def manchester():
	data = []
	outdata = []
	bit_shift = 0

	for i in range(1, len(sys.argv)):
		data.append(int(sys.argv[i]))

	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)

	#high for 10T and low for 1T
	for _ in range(0,10):
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
		outdata.append(1)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)
	outdata.append(0)

	i = 0
	while(i < len(data)):
		if(data[i] & (1 << bit_shift)): #if 1
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
		else:
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(0)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)
			outdata.append(1)

		bit_shift += 1
		if(bit_shift > 7):
			bit_shift = 0
			i += 1
	return outdata


def display_data(y):
	x = np.arange(0, len(y))
	plt.plot(x,y)
	plt.show()
	print(low_pass_filter.decode_myprotocol_alternate(y))

display_data(manchester())