#!/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# low pass filter, give it a list 'data_set' and a 'threshold', and it'll return a list with attenuated pulses
def LP_filter(data_set, threshold):
	result_list = []
	i = 0
	while(i < len(data_set)):
		if(data_set[i] == 0):
			result_list.append(data_set[i])
			i = i + 1
		elif(data_set[i] == 1): #if 1
			one_counter = 0
			while(data_set[i] != 0):
				one_counter = one_counter + 1
				i = i + 1
			if(one_counter >= threshold):
				for a in range(0,one_counter):
					result_list.append(1)
			else:
				for a in range(0,one_counter):
					result_list.append(0)
	return result_list


#decodes data from a manchester encoded signal