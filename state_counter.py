#!/bin/python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv('data_log.csv')
lstates = []
hstates = []

temp = 0
i = 0
d = list(data['values_filtered'])
l = len(d)
print(l)
try:
	while(i < l):

		while(d[i] == 0):
			i += 1
			temp += 1
		lstates.append(temp)

		temp = 0
		while(d[i] == 1):
			i += 1
			temp += 1
		hstates.append(temp)
except:
	print("LMin -> " + str(min(lstates)))
	print("LMax -> " + str(max(lstates)))

	print("HMin -> " + str(min(hstates)))
	print("HMax -> " + str(max(hstates)))

	print(lstates)
	print(hstates)