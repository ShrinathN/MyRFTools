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
			try:
				while(data_set[i] != 0):
					one_counter = one_counter + 1
					i = i + 1
			except:
				break
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
	data_length = len(filtered_data_set)
	i = 0
	state_counter = 0
	bit_shift = 0
	current_byte = 0

	while(i < data_length):
		while(filtered_data_set[i] != 1): #till a 1 is not found, proceed
			i += 1

		state_counter = 0

		while(filtered_data_set[i] != 0):
			state_counter += 1
			i += 1

		if(state_counter >= (one_T_samples * 1.5)): #if the low T state was longer than 150% of the normal T state, this means the first bit is a zero
			current_byte |= (0 << bit_shift)


def decode_myprotocol_sync(filtered_data_set, one_T_samples=10):
	i = 0
	l = len(filtered_data_set)
	state_counter = 0
	fault_found = False
	curstate = 0

	#=====TUNING=====
	SAMPLE_THRESHOLD = 1.2
	#=====TUNING=====

	bit_shift = -1
	current_byte = 0
	local_data = []
	final_data = []
	sample_times = []

	while(i < l):
		try: #here we find the preamble
			while(filtered_data_set[i] == 0):
				i += 1

			while(filtered_data_set[i] == 1):
				i += 1
		except IndexError:
			fault_found = True
			break

		i += int(one_T_samples * SAMPLE_THRESHOLD) #skipping to first bit

		bit_shift = -1
		local_data = []
		current_byte = 0

		while(not fault_found):
			curstate = filtered_data_set[i]

			bit_shift += 1
			if(bit_shift > 7):
				bit_shift = 0
				local_data.append(current_byte)
				current_byte = 0

			current_byte |= (curstate << bit_shift)
			sample_times.append([i, curstate])
			try:
				while(filtered_data_set[i] == curstate):
					i += 1
			except:
				local_data.append(current_byte)
				fault_found = True
				break

			state_counter = 0
			while(filtered_data_set[i] == (curstate ^ 1)):
				i += 1
				state_counter += 1
				if(state_counter > (3 * one_T_samples)):
					fault_found = True
					state_counter = 0
					break

			#this is for when the state is a fused state to the next bit
			if(state_counter >= int(one_T_samples * SAMPLE_THRESHOLD)): #if the state is longer than SAMPLE_THRESHOLD*100 % of a normal state
				i -= int((2 - SAMPLE_THRESHOLD) * one_T_samples) #decrementing i
			else: #if the state is less than one_T_samples * SAMPLE_THRESHOLD
				i += int((SAMPLE_THRESHOLD - 1) * one_T_samples)

		local_data.append(current_byte)
		final_data.append(local_data.copy())
		local_data = []
		fault_found = False
	return (final_data, sample_times)

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
	SAMPLE_THRESHOLD = 1.5 #this is 100x, so 1.2 is 120%
	FAULT_THRESHOLD = 1 #faults to tolerate before exiting session
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