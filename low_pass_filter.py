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


#DOESNT WORK, TODO: fix this
#decodes data from my encoding
#expects a filtered signal as input filtered_data_set
#expects the 1T time given, assumes it to be 10 samples instead
def decode_myprotocol(filtered_data_set, one_T_samples=10):
	recovered_data = []
	first_run = True
	i = 0
	length_data = len(filtered_data_set)
	while(i < length_data):
		while(filtered_data_set[i] != 1): #this will find the preamble
			i = i + 1
		print('preamble found')
		#adding 10% of the T time to make detection easier, only does this first time
		if(first_run):
			i = i + int(one_T_samples * 11) #this is for skipping the preamble part, straight to the first part of first bit
			first_run = False
		else:
			i = i + int(one_T_samples * 11)
		bit_shift = 0
		data_byte = 0
		while(filtered_data_set[i] != filtered_data_set[i + one_T_samples]): #while 0s are not found
			if(filtered_data_set[i] == 1 and filtered_data_set[i + one_T_samples] == 0):
				bit_detected = 1
				print('one')
			elif(filtered_data_set[i] == 0 and filtered_data_set[i + one_T_samples] == 1):
				bit_detected = 0
				print('zero')

			data_byte = data_byte | (bit_detected << bit_shift) #setting the data_byte
			bit_shift = bit_shift + 1 #incrementing bit_shift
			if(bit_shift > 7):
				bit_shift = 0
				recovered_data.append(data_byte)
				print(data_byte)
				data_byte = 0
			i = i + 2*one_T_samples
	return recovered_data

def decode_myprotocol_alternate(filtered_data_set, one_T_samples):
	NONE_STAGE = -1
	PREAMBLE_STAGE = 0
	stage = NONE_STAGE
	i = 0
	state_counter = 0
	length_data = len(filtered_data_set)
	while(i < length_data):

		if(stage == NONE_STAGE):
			state_counter = 0
			if(filtered_data_set[i] != 1):
				i = i + 1

		#in this stage, we have to count how long high and low times are
		if(stage == PREAMBLE_STAGE):
