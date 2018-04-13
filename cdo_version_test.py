import os,glob,sys
from subprocess import Popen
import subprocess
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da
import pandas as pd
import collections

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt/cdo_version_test/')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt/cdo_version_test/')

for cdo in ['cdo/1.6.9','cdo/1.7.0','cdo/1.7.1','cdo/1.8.0']:
	os.system('module load '+cdo)
	print(os.system('cdo -V'))
	os.system('cdo remapdis,../blend-runnable/grid1x1.cdo raw_sftof_ACCESS1-0.nc sftof_'+cdo.replace('/','-')+'_ACCESS1-0.nc')


# for cdo_version in 1.6.9 1.7.0 1.7.1 1.8.0; do module load cdo/$cdo_version; cdo remapdis,../blend-runnable/grid1x1.cdo raw_sftof_ACCESS1-0.nc sftof_cdo-${cdo_version}_ACCESS1-0.nc; done;


#  :history = "Tue Mar 27 11:20:43 2018: cdo remapbil,grid1x1.cdo /data/cmip5/files/historical/fx/sftof/ACCESS1-0/r0i0p0/sftof_fx_ACCESS1-0_historical_r0i0p0.nc sftof.nc\nCMIP5 compliant file produced from raw ACCESS model output using the ACCESS Post-Processor and CMOR2. 2012-01-29T23:55:59Z CMOR rewrote data to comply with CF standards and CMIP5 requirements.";
