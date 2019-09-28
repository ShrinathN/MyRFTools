#!/bin/python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import low_pass_filter

data = pd.read_csv('/home/shinu/Desktop/data_log.csv')
d = list(data['values_filtered'])

result = low_pass_filter.decode_myprotocol(d)

print(result)