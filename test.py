#!/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import low_pass_filter

data = pd.read_csv('/home/shinu/Desktop/data_log.csv')
d = list(data['values_filtered'])

result,timing = low_pass_filter.decode_myprotocol_alternate(d)
r = np.arange(0, len(d))

#sample timing
x = []
y = []
for i in range(0,len(timing)):
	x.append(timing[i][0])
	if(timing[i][1] == 0):
		y.append(0.25)
	else:
		y.append(0.75)

fig = plt.figure(figsize=(60,3))
axes= fig.add_axes([0.1,0.1,0.8,0.8])
axes.plot(r,d)
axes.plot(x,y,"*r")
plt.show()