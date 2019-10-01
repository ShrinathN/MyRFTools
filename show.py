#!/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('data_log.csv')
x = list(data['values_raw'])
w = list(data['values_filtered'])
y = np.arange(0,len(x))

plt.plot(y,x)
plt.show()
plt.plot(y,w)
plt.show()
