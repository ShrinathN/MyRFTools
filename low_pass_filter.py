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

#this algorithm works on the belief that 20% of one T is a good time to sample the bit
#this algo will absolutely not work if the length of states is different
def decode_myprotocol_alternate(filtered_data_set, one_T_samples=10):
	#constants
	NONE_STAGE = 0 #where nothing is happening and signal is 0 all the time until the next pulse
	NEW_PREAMBLE_STAGE = 1 #
	PREAMBLE_STAGE = 2
	NEW_DATA_STAGE = 3
	DATA_STAGE = 4

	#=====TUNING=====
	SAMPLE_THRESHOLD = 1.4 #this is 100x, so 1.2 is 120%
	FAULT_THRESHOLD = 5 #faults to tolerate before exiting session
	#=====TUNING=====

	stage = NONE_STAGE

	sampled_time_list = []
	final_result = []
	i = 0
	state_counter = 0
	fault_counter = 0
	length_data = len(filtered_data_set)

	while(i < length_data):
		if(stage == NONE_STAGE): #meaning we're trying to find a preamble
			if(filtered_data_set[i] == 1):
				stage = PREAMBLE_STAGE
				state_counter = 0
			else:
				i = i + 1

		if(stage == PREAMBLE_STAGE): #this is while the sample is still high
			if(filtered_data_set[i] == 0): #waiting for the sample to go low so that we can wait for approx 1T and then sample the pin again to know our first bit
				stage = NEW_DATA_STAGE
				state_counter = 0
			else: #if the bit is not yet 0, keep incrementing
				i = i + 1

		if(stage == NEW_DATA_STAGE): #this is when the bit is finally 0 after the preamble.
			if(state_counter >= int(one_T_samples * SAMPLE_THRESHOLD)): #this checks if the data data stage has been present for longer than 120% of a single T
				state_counter = 0
				stage = DATA_STAGE
				bit_shift = 0
				current_byte = 0
				session_bytes = []
			else:
				i = i + 1

		if(stage == DATA_STAGE):
			if(bit_shift > 7):
				bit_shift = 0
				session_bytes.append(current_byte)
				current_byte = 0
			if((filtered_data_set[i] ^ filtered_data_set[i + one_T_samples]) == 1): #if the two transitions are different
				sampled_time_list.append([i,filtered_data_set[i]])
				current_byte |= filtered_data_set[i] << bit_shift
				bit_shift = bit_shift + 1
				fault_counter = 0
			else: #if there is no transition, ie no manchester, increment fault counter
				fault_counter += 1
				if(fault_counter >= FAULT_THRESHOLD): #this means the fault threshold has been exceeded, this usually means the session has ended
					stage = NONE_STAGE
					final_result.append(session_bytes)
					fault_counter = 0

			i = i + (2 * one_T_samples)

		#most important part of the algorithm, this is SysTick basically
		state_counter = state_counter + 1

	return final_result,sampled_time_list