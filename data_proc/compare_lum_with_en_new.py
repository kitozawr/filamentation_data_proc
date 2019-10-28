#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 16:57:52 2019

@author: dmitrii
"""

import os
import numpy as np
import shutil as sh

#%% Constants
empty_threshold = 350.0
n_ac_try_range = 10

def read_en(filename_en, line_length, col_times, col_en, col_fon, col_trig):
	#%% Чтение данных из файла с энергиями.
	#Читаем файл с энергиями в массив "слов".
	with open(filename_en,'r') as f:
		file_data_words = f.read().split()

	#Подсчёт количества строк в файле (нужно в случае, если все данные записаны в одну строку).
	lc = int(round(len(file_data_words)/line_length))
	#print(lc)

	if lc == 0:
		print("\nFile with energies is empty.\n")
		return(1)
	elif lc <= 2:
		print("\nEnergy file contains less than 3 entries.\n")
		return(2)

	# Инициализация массивов с времена
	time_en = np.zeros(lc) # Массив времён [c]
	energies = np.zeros(lc) # Массив энергий [попугаи]
	strob = np.zeros(lc) #Массив значений строба

	#Заполняем массивы значениями из файла с энергиями.
	for i in range(0, lc):
		time_en_list = (file_data_words[i*line_length+col_times]).split("-")
		time_en[i] = float(time_en_list[-1])+ float(time_en_list[-2]) + 60.0*float(time_en_list[-3]) + 3600.0*float(time_en_list[-4])
		energies[i] = int(round(float(file_data_words[i*line_length+col_en]) - float(file_data_words[i*line_length+col_fon])))
		strob[i] = int(round(float(file_data_words[i*line_length+col_trig])))
	#-----------
	#Конец чтения файла с энергиями.

	#%% Поиск момента включения строба.
	# Инициализация переменных
	strob_diff = 0; i_start = 0 # Скачок строба; номер строки, когда включился строб.
	for i in range(1, lc):
		strob_diff_new = strob[i] - strob[i-1] #Текущее значение скачка строба.
		# Если текущее значение больше предыдущего, то текущее присваивается предыдущему.
		if strob_diff_new > strob_diff:
			strob_diff = strob_diff_new
			i_start = i # В i_start записывается текущий номер.

	return(time_en, energies, i_start, lc)

#%%
def read_lum(foldername_ac, ext):
	#Формирование несортированного списка файлов с акустикой.
	filenames_ac = [f for f in os.listdir(foldername_ac) if f.endswith(ext)]
	filenames_ac_info = [f.split(ext)[0].split("__") for f in filenames_ac]
	filenames_ac_info_ext = []
	for f in filenames_ac_info:
		time = calc_lum_time(f[-1])
		filenames_ac_info_ext.append([time, f])
	filenames_ac_info_ext = sorted(filenames_ac_info_ext, key = lambda x: float(x[0])) #Cортированный по первому элементу названия (времени в мс) список файлов с акустикой.
	filenames_ac_times = np.array([int(f[0]*1000) for f in filenames_ac_info_ext])
	filenames_ac_info = [f[1] for f in filenames_ac_info_ext]
	return(filenames_ac_times, filenames_ac_info)

#%%
def calc_lum_time(string):
	'''
	Calculate time from a time string in format h_m_s,ms.
	'''
	string_splitted, ms = string.split(",")
	ms = float(ms)
	h, m, s = [float(f) for f in string_splitted.split("_")]
	time = h*3600.0 + m*60.0 + s + ms*0.001
	return(time)

def compare_lum_with_en_new(filename_en, foldername_ac, folder_to_write, ext='.dat', col_en=9, col_fon=8, col_trig=6, col_times=1, line_length=17, dt=0.1, shift=-2, EPS_TIME_EN=0.14, EPS_TIME_AC=120, EPS_TIME_AC_1=25, N_try=5, EPS_TIME_EN_1=0.025):

	'''
	This function matches energies from a file with energies with other data obtained in single-shot regime (acoustics, or modes, or luminescence, or interferograms) in "parrots".

	Parameters:
	filename_en - energy file,
	foldername_ac - folder with files to be compared with the energies from the energy file,
	folder_to_write - path for the files to be written,
	ext='.bin' - extension for data filenames ('.bin' is default),
	col_en=9 - number of column that contain energy values from photodiode (in the energy files),
	col_fon=8 - number of column that contain background values from photodiode (in the energy files),
	col_trig=6 - number of column that contain strobe values (the data when the trigger is turned on),
	col_times=1 - column with times, when the energies have been written into the file,
	line_length=17 - number of columns in energy file,
	dt=0.1 - laser (and sinchropulse) repetition rate,
	shift=-2 - strange shift between the energies and data. In the program the shift is added by +1.

	Program constants:
	EPS_TIME_EN=0.14
	EPS_TIME_AC=120
	N_try=5 - number of pulses after which the function checks if the steps in energy file restored after a strob has been missed,
	EPS_TIME_EN_1=0.025 - if the difference between the calculated and real times within N_try shots is less than this value, shots are considered to be haven't been missed

	WARNING: program parameters are fitted for the nice program work. It is NOT recommended to change them.
	'''

	###

	'''
	#%% Инициализация параметров
	EPS_TIME_EN = 0.14
	EPS_TIME_AC = 120
	dt = 0.1
	N_try = 5 # Число выстрелов, после которых проверяется, восстановились ли шаги по энергии
	EPS_TIME_EN_1 = 0.025 # Если разница между рассчётными реальным временем в N_try выстрелов меньше этой величины, то считается, что выстрелы пропущены не были

	#Номера столбцов, по которым определяются значения энергии и момент включения строба. 8 канал АЦП (при нумерации с 1) - 9 столбец.
	col_en = 9 # cигнал с диода
	col_fon = 8 # фон с диода
	col_trig = 6 # включение/выключение строба
	col_times = 1 # столбец времён записи энергии в файл
	line_length = 17 # количество слов в строке файла с энергиями
	dt = 0.1 # интервал между выстрелами в секундах [c]
	'''

	#%% Инициализация переменных
	count_en_skipped = 0
	count_en_corrected = 0
	#delta_j = 0

	'''
	#Путь к папке для копирования сопоставленных мод.
	folder_to_write = os.path.abspath(os.path.join(foldername_ac, os.pardir))+"/"+foldername_ac.split("/")[-2] + "_matched" + os.sep

	#Удаление папки, если она существует, и создание её заново.
	if os.path.exists(folder_to_write):
		sh.rmtree(folder_to_write)
	os.makedirs(folder_to_write)

	#Название файла с энергиями (без расширения и пути).
	filename_en_splitted = filename_en.split("/")[-1]
	filename_en_splitted = filename_en_splitted.split(ext_en)[0]
	#print(filename_en_splitted)
	folder_ac_to_write = folder_to_write + filename_en_splitted + os.sep
	#print(folder_ac_to_write)
	os.makedirs(folder_ac_to_write)

	#Для каждого файла с энергиями цикл перебирает все папки с акустикой.
	foldername_ac_splitted = foldername_ac.split(os.sep)[-1]
	foldername_ac = os.path.join(folder_to_write, foldername_ac)
	'''

	#%% Read list of filenames with luminescence.
	filenames_ac_times, filenames_ac_info = read_lum(foldername_ac, ext)
	#%% Read parameters from the energy file.
	time_en, energies, i_start, lc = read_en(filename_en, line_length, col_times, col_en, col_fon, col_trig)
	#%% Цикл, сопоставляющий акустику и энергию.
	i, j = i_start+shift, 0 # Счётчики для энергии и акустики, соответственно.
	#delta_j = 0
	#variable = "OK"
	while (i < lc - 1) and (j < len(filenames_ac_info)):
		if i > 0 and j > 0:
			delta_time_en = time_en[i+1] - time_en[i]
			delta_time_ac = filenames_ac_times[j] - filenames_ac_times[j-1]
		else:
			delta_time_en = 0
			delta_time_ac = 0

		#Проверка на пропущенные стробы в энергиях и акустике.
		if delta_time_en < EPS_TIME_EN and delta_time_ac < EPS_TIME_AC:
			filename_ac_new = folder_to_write + str(energies[i+1]) + "_" + str(i+1) + "_" + filenames_ac_info[j][0] + "_" + filenames_ac_info[j][1] + "_" + filenames_ac_info[j][2] + ext
			filename_ac = os.path.join(foldername_ac, "__".join(filenames_ac_info[j])+ext)
			sh.copyfile(filename_ac, filename_ac_new)
			i += 1; j += 1
		elif delta_time_ac >= EPS_TIME_AC and delta_time_en < EPS_TIME_EN:
			#print("WARNING: acoustics was skipped.")
			#delta_t_ac = int(round(delta_time_ac/100.0))
			print("WARNING: acoustics was skipped")
			#time_ac_j_minus_2 = np.mean(time_en[i-:i]) + dt
			N_ac_try = 2; success = False
			if j < 2:
				j_new = 2
			else:
				j_new = j
			while (j + N_ac_try < len(filenames_ac_info)):
				n_ac_try = N_ac_try
				while (n_ac_try < N_ac_try + n_ac_try_range) and (j_new + n_ac_try < len(filenames_ac_info)):
					if abs(filenames_ac_times[j_new+N_ac_try-2] - filenames_ac_times[j_new-2] - dt*n_ac_try*1000) < EPS_TIME_AC_1:
						if abs(time_en[i+(j_new-j)+n_ac_try] - time_en[i+(j_new-j)] - dt*n_ac_try) < EPS_TIME_EN_1:
							i = i+(j_new-j)+n_ac_try; j = j_new + N_ac_try
							print("Luminescence has been successfully corrected. {} luminescence files has been skipped".format(N_ac_try-2))
							success = True
							break
						else:
							print("WARNING: energy has been skipped.")
							n_en_try = 1 #n_en_try должно быть больше 0, иначе цикл будет завершаться после 1-й итерации.
							while (n_en_try < 2*n_ac_try) and (i + (j_new-j) + n_en_try < len(time_en)):
								if abs(time_en[i+(j_new-j)+n_en_try] - time_en[i+(j_new-j)] - dt*n_ac_try) < EPS_TIME_EN_1:
									i = i+(j_new-j)+n_en_try; j = j_new + N_ac_try
									print("Luminescence has been successfully corrected. {} luminescence files has been skipped".format(N_ac_try-2))
									print("Energy has been successfully corrected.")
									success = True
									break
								n_en_try += 1
							if not success: #Если произошёл выход из цикла, значит хотя бы одно из условий выхода было выполнено. При этом успех не был достигнут.
								print("WARNING: luminescence and energy was NOT corrected.")
							break
					else:
						n_ac_try += 1
					print(filenames_ac_times[j_new+N_ac_try-2])
					print(filenames_ac_times[j_new-2])
					print(j)
					print(abs(filenames_ac_times[j_new+N_ac_try-2] - filenames_ac_times[j_new-2] - dt*n_ac_try*1000))
					print("n_ac_try = {}".format(n_ac_try))
					#print(N_ac_try)
				if success:
					break
				else:
					N_ac_try += 1
			if not success:
				print("WARNING: energy has NOT been successfully corrected!")
				break
			#print(delta_t_ac, delta_time_ac, time_en[i:i+delta_t_ac+2], filenames_ac_times[j], filenames_ac_times[j-1], filenames_ac[j], filenames_ac[j-1])
			'''
			if time_en[i + delta_t_ac] < time_en[i-1] + delta_t_ac*0.1 + EPS_TIME_EN:
				filename_ac_new = folder_to_write + str(energies[i + delta_t_ac]) + "_" + str(i + delta_t_ac) + "_" + filenames_ac_info[j][0] + "_" + filenames_ac_info[j][1] + "_" + filenames_ac_info[j][2] + ext
				print("First frame after the skip: {}\n".format(filename_ac_new.split("/")[-1]))
				filename_ac = os.path.join(foldername_ac, "__".join(filenames_ac_info[j])+ext)
				sh.copyfile(filename_ac, filename_ac_new)
				i = i + delta_t_ac + 1; j += 1
			'''
		else:
			print("WARNING: suspicious energy time behavior.")
			#delta_j = 1
			time_en_i_minus_1 = np.mean(time_en[i-3:i]) + dt
			if (i+N_try < lc) and (j < len(filenames_ac_info)):
				if abs(time_en[i+N_try-1] - time_en_i_minus_1 - dt*N_try) < EPS_TIME_EN_1:
					print("Energy was not skipped.")
					# i_1, j_1 - cчётчики кадров для энергии и акустики для внутреннего цикла
					for i_1 in range(i,i+N_try-1):
						filename_ac_new = folder_to_write + str(energies[i+1]) + "_" + str(i+1) + "_" + filenames_ac_info[j][0] + "_" + filenames_ac_info[j][1] + "_" + filenames_ac_info[j][2] +ext
						filename_ac = os.path.join(foldername_ac, "__".join(filenames_ac_info[j]) + ext)
						sh.copyfile(filename_ac, filename_ac_new)
						i += 1
						j += 1
				else:
					count_en_skipped += 1
					n_try = N_try+1
					while (n_try <= 2*N_try) and abs(time_en[i+N_try-1] - time_en_i_minus_1 - dt*n_try) >= EPS_TIME_EN_1:
						n_try += 1
					if abs(time_en[i+N_try-1] - time_en_i_minus_1 - dt*n_try) < EPS_TIME_EN_1:
						print("Energy was skipped {} times".format(n_try-N_try))
						print("Acoustics will be skipped {} times".format(n_try))
						i += N_try - 1
						j += n_try - 1
						count_en_corrected += 1
						print("Energy has been successfully corrected.")
					else:
						print("WARNING: energy was NOT successfully corrected!")
						break

	print("Energy was skipped {0} times, {1} times successfully corrected.".format(count_en_skipped, count_en_corrected))
	if count_en_skipped - count_en_corrected > 0:
		print("WARNING: energy was not corrected {0} times.".format(count_en_skipped - count_en_corrected))
	print("See it, say it, sorted!")
	return("OK")

#############