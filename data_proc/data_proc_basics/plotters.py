# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 16:56:08 2018

@author: Дмитрий
"""
import sys, glob, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mplc

mpl.rcParams['agg.path.chunksize'] = 10000 #Enables large file plotting.
mpl.rc('text', usetex=True)
mpl.rcParams.update({'font.size': 20})
#mpl.rc('text.latex',unicode=True)
#mpl.rc('text.latex', preamble=r'\usepackage[utf8]{inputenc}')
#mpl.rc('text.latex', preamble=r'\usepackage[russian]{babel}')
mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['text.latex.preamble'] = [r'\boldmath']

def en_wf_plot(t_array, waveform, filename_to_save, style = 'k', color = 'k', lw='1.5', figsize=(10.5, 9.0), dpi=600, xlabel=r'\textbf{Time, ms}', ylabel=r'\textbf{Amplitude, V}'):
	#Graph plotting
	plt.figure(figsize=figsize, dpi=dpi)
	plt.rcParams['text.latex.preamble'] = [r'\boldmath']
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.plot(t_array, waveform, style, color='k', lw=1.5)
	plt.grid()
	plt.minorticks_on()
	plt.tick_params(axis='x', pad=7)
	plt.tick_params(axis='y', pad=5)
	plt.savefig(filename_to_save, bbox_inches='tight')
	plt.close()

def plot_heat_map(data, filename, v_min, v_max, log=False):
	"""
	Function plots heat maps of data numpy 2d array and save result to filename.png.
	"""
	#%% Constants
	#pair_x = 
	#heat map plotting
	mpl.rcdefaults()
	plt.figure(figsize=(20,10), dpi=300) #fig_size
	mpl.rcParams.update({'font.size': 22}) #fontsize
	#plt.xlabel(r'$x$')
	#plt.ylabel(r'$y$')
	plt.grid(False)
	plt.minorticks_on()
	plt.tick_params(axis='x', pad=7)
	plt.tick_params(axis='y', pad=5)

	if log==True:
		plt.imshow(data, cmap='jet', vmin=v_min, vmax=v_max, norm=mplc.LogNorm())
	else:
		plt.imshow(data, cmap='jet', vmin=v_min, vmax=v_max)

	plt.colorbar()
	plt.savefig(filename, bbox_inches='tight')

	plt.close()

	return True

def plot_heat_map_latex(data, filename, v_min, v_max, log=False, scale=197.9):
	"""
	Function plots heat maps of data numpy 2d array and save result to filename.png.
	"""
	#heat map plotting
	plt.figure(figsize=(20.0*data.shape[1]/1920.0, 10*data.shape[0]/1200.0), dpi=300) #fig_size
	plt.rcParams['text.latex.preamble'] = [r'\boldmath']
	mpl.rcParams.update({'font.size': 22}) #fontsize
	plt.xlabel(r'$x$, \textbf{mm}')
	plt.ylabel(r'$y$, \textbf{mm}')
	plt.grid(False)
	plt.minorticks_on()
	plt.tick_params(axis='x', pad=7)
	plt.tick_params(axis='y', pad=5)

	extent = (0, data.shape[1]/scale, 0, data.shape[0]/scale)

	if log==True:
		plt.imshow(data, cmap='jet', vmin=v_min, vmax=v_max, norm=mplc.LogNorm(), extent=extent)
		#plt.plot((100,297), (100, 100), 'k', color='w')
	else:
		plt.imshow(data, cmap='jet', vmin=v_min, vmax=v_max, extent=extent)
	plt.colorbar()
	plt.savefig(filename, bbox_inches='tight')

	plt.close()

	return True
