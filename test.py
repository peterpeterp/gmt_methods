import os,glob,sys
from subprocess import Popen
import subprocess
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import dimarray as da
import pandas as pd
import collections

try:
	os.chdir('/p/projects/tumble/carls/shared_folder/gmt')
except:
	os.chdir('/Users/peterpfleiderer/Documents/Projects/gmt')

cdoinfo=Popen('cdo info data_models/rcp85-xxx_rcp85_EC-EARTH_r1i1p1/tos.nc',shell=True, stdout=subprocess.PIPE).stdout.read()
cdoinfo.split('\n')[1]


cdoinfo=Popen('cdo info data_models/EC-EARTH_r1i1p1/tos.nc',shell=True, stdout=subprocess.PIPE).stdout.read()
