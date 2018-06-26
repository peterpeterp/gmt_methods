import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import seaborn as sns

os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')


# these models start in 1861 GFDL-CM3 GFDL-ESM2G GFDL-ESM2M HadGEM2-AO HadGEM2-CC HadGEM2-ES



for mod_style in ['model','runs']:
	for av_style in ['year','20year']:
		for preind_name,preind_period in zip(['1861-1880','1850-1900'],[[1861,1880],[1850,1900]]):
			gmt=da.read_nc('data/gmt_plot_ready_'+av_style+'_'+mod_style+'_'+preind_name+'.nc')['gmt']

			print '********** '+preind_name+' ***** '+av_style+' ******* '+mod_style
			print '1986-2005'
			for style in ['gmt_sat','gmt_bm']:
				print style,np.nanmean(gmt['rcp85',:,style,1986:2005])

			print '2006-2015'
			for style in ['gmt_sat','gmt_bm']:
				print style,np.nanmean(gmt['rcp85',:,style,2006:2015])

			# print 'diff'
			# for style in ['gmt_sat','gmt_bm']:
			# 	print style,np.nanmean(gmt['rcp85',:,style,2006:2015])-np.nanmean(gmt['rcp85',:,style,1986:2005])
