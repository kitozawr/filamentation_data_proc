#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:35:53 2019

@author: dmitrii
"""
#lumin_clean.py
"""
luminiscence images cleaning procedure
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import struct
import scipy.ndimage as ndimg

def rotate(data, angle):
	rot_data = ndimg.interpolation.rotate(input=data, angle=angle, order=0, prefilter=False, reshape=False)
	return rot_data

def trunc(data, left, right):
	"""
	Function truncates an array.
	"""
	trunc_data = data[:,left:right]

	return trunc_data

def read_dat(filename):
	"""
	Function opens .dat file.
	"""

	#binary data file reading
	with open(filename, "rb") as binary_file:
		data_bin = binary_file.read()

	zero = struct.unpack('>H', data_bin[0:2])[0]
	height = struct.unpack('>H', data_bin[2:4])[0]
	zero = struct.unpack('>H', data_bin[4:6])[0]
	width = struct.unpack('>H', data_bin[6:8])[0]

	try:
		s = '>H'+'H'*(height*width - 1)
		data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='uint16')
	except struct.error:
		try:
			s = '>B'+'B'*(height*width - 1)
			data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='uint8')
			data = data*8
			print("Warning: 8bit image. Read with adjustment to 12bit format (magnified by 8).")
		except:
			print("ERROR: could not read data file {}".format(filename))
	data = np.reshape(data, (height, width))

	return(data, width, height)

def read_dat_float(filename):
	"""
	Function opens .dat file.
	"""

	#binary data file reading
	with open(filename, "rb") as binary_file:
		data_bin = binary_file.read()

	zero = struct.unpack('>H', data_bin[0:2])[0]
	height = struct.unpack('>H', data_bin[2:4])[0]
	zero = struct.unpack('>H', data_bin[4:6])[0]
	width = struct.unpack('>H', data_bin[6:8])[0]

	try:
		s = '>d'+'d'*(height*width - 1)
		data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='float64')
	except struct.error:
		try:
			s = '>B'+'B'*(height*width - 1)
			data = np.fromiter(struct.unpack(s, data_bin[8:]), dtype='uint8')
			data = data*8
			print("Warning: 8bit image. Read with adjustment to 12bit format (magnified by 8).")
		except:
			print("ERROR: could not read data file {}".format(filename))
	data = np.reshape(data, (height, width))

	return(data, width, height)

def save_dat(filename_to_save, data):
	'''
	Write 2d array to .dat file.
	'''
	fout = open(filename_to_save, 'wb')
	fout.write(struct.pack('>H', 0))
	fout.write(struct.pack('>H', data.shape[0]))
	fout.write(struct.pack('>H', 0))
	fout.write(struct.pack('>H', data.shape[1]))
	s = '>H'+'H'*(data.size - 1)
	data = data.flatten()
	fout.write(struct.pack(s, *data))
	fout.close()

def save_dat_float(filename_to_save, data):
	'''
	Write 2d array to .dat file.
	'''
	fout = open(filename_to_save, 'wb')
	fout.write(struct.pack('>H', 0))
	fout.write(struct.pack('>H', data.shape[0]))
	fout.write(struct.pack('>H', 0))
	fout.write(struct.pack('>H', data.shape[1]))
	s = '>d'+'d'*(data.size - 1)
	data = data.flatten()
	fout.write(struct.pack(s, *data))
	fout.close()

def read_bd_map(bd_map_file):
	"""
	Read breakdown map, as specified in bd_map_file.
	It is assumed that coordinates of breakdowns are sorted by x increasing.
	"""
	#Variables
	bd_mult = [] #Координаты "множественных" пробоев.
	bd_single = [] #Координаты "одиночных" пробоев.

	f=open(bd_map_file)
	lines = f.readlines()
	print("Reading breakdown map...")
	if lines[0] == "Muliple hot spots\n":
		print("File start is OK.")
	single_start_num = lines.index("Separate hot spots\n")
	bd_mult = np.genfromtxt(bd_map_file, skip_header=1, max_rows=single_start_num-1, dtype = 'uint16')
	bd_single = np.genfromtxt(bd_map_file, skip_header=single_start_num+1, dtype = 'uint16')
	print("Bd map has been successfully read.")
	
	return (bd_mult, bd_single)

def apply_bd_map(data, bd_mult, bd_single):
	"""
	Removes breakdowns, which coordinates are listed in bd_mult ("multiple" breakdowns) and bd_single (single separated hot spots).
	It is assumed that coordinates of breakdowns are sorted by x increasing.
	"""
	#Для множественных пробоев - аппроксимируем пробитый участок линейной зависимостью, исходя из ближайших непробитых точек.
	i_old = 0
	if bd_mult.size != 0:
		for k in range(bd_mult.shape[0]):
			j,i = bd_mult[k]
			if i == i_old and j>j_bottum and j<j_top:
				continue
			elif i < i_old:
				print("ERROR: coordinates are not sorted by i increasing!!!")
				return "apply_bd_map_error"
			else:
				i_old = i; k1 = k
				while k1<bd_mult.shape[0] and bd_mult[k1,1] == i: #Используем, что массив отсортирован по i, а где i одинаково - по j.
					k1 += 1
				j_top = int(bd_mult[k1-1,0])+1; k1=k #Ближайшая непробитая точка сверху.
				while k1>=0 and bd_mult[k1,1] == i:
					k1 -= 1
				j_bottum = int(bd_mult[k1+1,0])-1 #Ближайшая непробитая точка снизу.
				# Коэффициенты линейной аппроксимации.
				A = (float(data[j_top,i]) - float(data[j_bottum,i]))/(float(j_top) - float(j_bottum))
				B = float(data[j_bottum,i]) - A*j_bottum
				data[j_bottum+1:j_top,i] = np.around(A*np.arange(j_bottum+1, j_top)+B)

	#Для одиночных пробоев.
	if bd_single.size != 0:
		for k in range(bd_single.shape[0]):
			j,i = bd_single[k]
			vic_sum = np.sum(data[j-1:j+2,i-1:i+2]) - data[j,i]
			data[j,i] = vic_sum/8.0
	return data

def run_av_2d(data, window=11, axis=1):
	'''
	Function performs running average on 2d data array along x axis.
	window should be even.
	'''
	data_1 = np.zeros_like(data[:,window-1:])
	for i in range(0, data.shape[axis]-(window-1)):
		data_1[:,i] = np.mean(data[:,i:i+window], axis = axis)

	return(data_1)

def run_av(data, window=11):
	'''
	Function performs running average on 1d data array.
	window should be even.
	'''
	data_1 = np.zeros_like(data[window-1:])
	for i in range(0, data.shape[0]-(window-1)):
		data_1[i] = np.mean(data[i:i+window])

	return(data_1)

def find_limits(data, method='simple'):
	'''
	Функция находит максимальное и минимальное значение для печати двумерного массива.
	'''
	#Константы
	width = 3
	if method=='simple':
		v_max = np.amax(data)
	elif method=='good':
		#Максимальное среднее по квадрату 3x3.
		y_rest = data.shape[0] % width
		x_rest = data.shape[1] % width
		wv = int(round(width-1)/2)
		wv_1 = wv+1
		ws = width*width
		curr_max = 0.0; new_max = 0.0
		for i in range(wv, data.shape[0]-wv, width):
			for j in range(wv, data.shape[1]-wv, width):
				new_max = np.sum(data[i-wv:i+wv_1,j-wv:j+wv_1])/ws
				if new_max > curr_max:
					curr_max = new_max
		v_max = curr_max	
	else:
		print("ERROR: in find_limits (lumin_proc.py) - unknown keyword for scale maxima search")
		return False		
	v_min = (np.sum(data[:20, :20]) + np.sum(data[-20:, :20]) + np.sum(data[:20,-20:]) + np.sum(data[-20:,-20:]))/1600.0
	return (v_min, v_max)
