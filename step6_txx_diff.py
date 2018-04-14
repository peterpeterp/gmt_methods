import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import pandas as pd


#plt.style.use('ggplot')
#plt.rcParams['figure.figsize'] = 8,6
from matplotlib import rc
rc('text', usetex=True)

os.chdir('../pdf_processing/')
sys.path.append('/p/projects/tumble/carls/shared_folder/pdf_processing/')
import pdf_processing as pdf; reload(pdf)
os.chdir('../gmt/')

###########
# Settings
###########

# PDF Method (currently defined: hist, python_silverman)
pdf_method='python_silverman'

levels=[1.5,1.66]

# variables
varin_dict={
    'TXx':{'var_name':'tasmax','longname':'Hot extremes (TXx)','unit':'TXx [$^\circ$ C]','cut_interval':[-1.5,3.5],'nc_name':'tasmax'},
    'TNn':{'var_name':'tasmin','longname':'Cold extremes (TNn)','unit':'TNn [$^\circ$ C]','cut_interval':[-3,5],'nc_name':'tasmin'},
    'RX1':{'var_name':'RX1DAY','longname':'Cold extremes (RX1)','unit':'RX1DAY [$^\circ$ C]','cut_interval':[-30,40],'nc_name':'pr'},
    'RX5':{'var_name':'RX5DAY','longname':'Cold extremes (RX5)','unit':'RX5DAY [$^\circ$ C]','cut_interval':[-30,45],'nc_name':'highest_five_day_precipitation_amount_per_time_period'}
    }

gmt_all=da.read_nc('data/gmt_model.nc')['gmt']
models=list(gmt_all.model)
# #models.remove('CESM1-CAM5')
# #models.remove('MIROC5')
# models.remove('BNU-ESM')
# models.remove('bcc-csm1-1-m')
gmt_=gmt_all[gmt_all.style,gmt_all.scenario,models,gmt_all.variable,gmt_all.time]

wlvls=da.read_nc('data/wlvls.nc')['wlvls']

rcp='rcp85'
var='TXx'
cmip5_dict={}

os.chdir('../pdf_processing/')
for model in wlvls.model:
    if model not in cmip5_dict.keys(): cmip5_dict[model]={}

    # time informations and periods
    target_periods=[]
    period_names=[]
    for change in levels:
        period_names.append(str(change))
        mid_year=wlvls['rcp85',model,change]
        target_periods.append([mid_year-10,mid_year+10])

    period_names.append('ref')
    ref_period=[1986,2006]
    target_periods.append(ref_period)

    if True:
        # combine datasets
        var_name=varin_dict[var]['nc_name']

        nc_rcp85=Dataset('/p/projects/ikiimp/tmp/cmip5_Xev_from_Erich_Fischer/tasmax_'+model+'_rcp85_r1i1p1_2006-2100.YEARMAX.nc')
        lat=nc_rcp85.variables['lat'][:]
        lon=nc_rcp85.variables['lon'][:]

        datevar = []
        datevar.append(num2date(nc_rcp85.variables['time'][:],units = nc_rcp85.variables['time'].units,calendar = nc_rcp85.variables['time'].calendar))
        year=np.array([int(str(date).split("-")[0])	for date in datevar[0][:]])
        var_in=nc_rcp85.variables[var_name][:,:,:]
        if var_in.mean()>150:
            var_in-=273.15
        input_rcp85=da.DimArray(var_in[:,:,:].squeeze(), axes=[year, lat, lon],dims=['year', 'lat', 'lon'] )

        nc_hist=Dataset('/p/projects/ikiimp/tmp/cmip5_Xev_from_Erich_Fischer/tasmax_'+model+'_historical_r1i1p1_1901-2005.YEARMAX.nc')
        datevar = []
        datevar.append(num2date(nc_hist.variables['time'][:],units = nc_hist.variables['time'].units,calendar = nc_hist.variables['time'].calendar))
        year=np.array([int(str(date).split("-")[0])	for date in datevar[0][:]])
        var_in=nc_hist.variables[var_name][:,:,:]
        if var_in.mean()>150:
            var_in-=273.15
        input_hist=da.DimArray(var_in[:,:,:].squeeze(), axes=[year, lat, lon],dims=['year', 'lat', 'lon'] )

        input_data=da.concatenate((input_hist, input_rcp85), axis='year')

        print(input_data)

        cmip5_dict[model][var]=pdf.PDF_Processing(var)
        cmip5_dict[model][var].mask_for_ref_period_data_coverage(input_data,ref_period,check_ref_period_only=False,target_periods=target_periods)

        # Derive time slices
        cmip5_dict[model][var].derive_time_slices(ref_period,target_periods,period_names)
        cmip5_dict[model][var].derive_distributions()

        print(cmip5_dict[model][var])
        
        for change in levels:
            cmip5_dict[model][var].derive_pdf_difference('ref',str(change),pdf_method=pdf_method,bin_range=varin_dict[var]['cut_interval'],relative_diff=False)

        for change in levels[-2:]:
            cmip5_dict[model][var].derive_pdf_difference(str(1.5),str(change),pdf_method=pdf_method,bin_range=varin_dict[var]['cut_interval'],relative_diff=False)

    # except Exception as e:
    #     print e
    #     print '-----------'+model


os.chdir('../gmt/')
with open('data/varoutdict_cmip5_'+rcp+'_TXx.pkl', 'wb') as output:
	pickle.dump(cmip5_dict, output, pickle.HIGHEST_PROTOCOL)

# os.chdir('../pdf_processing/')
# import pdf_processing as pdf; reload(pdf)
# os.chdir('../gmt/')
#
# with open('data/varoutdict_cmip5_rcp85_TXx.pkl', 'rb') as input:
#     cmip5_dict = pickle.load(input)

# all models merged pdf
all_cmip5=pdf.PDF_Processing('TXx')
all_cmip5._distributions={'global':{}}
N_model=len(cmip5_dict.keys())

for change in levels+['ref','weight']:
    tmp=np.array([np.nan])
    for model,mod_index in zip(cmip5_dict.keys(),range(N_model)):
        try:
            if np.isfinite(np.nanmean(cmip5_dict[model]['TXx']._distributions['global'][str(change)])):
                tmp=np.concatenate((tmp,cmip5_dict[model]['TXx']._distributions['global'][str(change)]))
        except:
            pass
    all_cmip5._distributions['global'][str(change)]=tmp[1:]

for change in levels:
    all_cmip5.derive_pdf_difference('ref',str(change),pdf_method='python_silverman',bin_range=varin_dict['TXx']['cut_interval'],relative_diff=False)

with open('data/varoutdict_cmip5_'+'rcp85'+'_TXx_models_merged.pkl', 'wb') as output:
	pickle.dump(all_cmip5, output, pickle.HIGHEST_PROTOCOL)


# get ensemble used# cmip5 envelopes overview
ensemble=open('ensemble_TXx.txt','w')
for model,mod_index in zip(cmip5_dict.keys(),range(N_model)):
    try:
        a=cmip5_dict[model]['TXx']._distributions['global']['pdf']['xaxis']
        ensemble.write(model+'\n')
    except:
        pass
ensemble.close()
