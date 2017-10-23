import os,sys,glob,time,collections,gc,pickle
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib
from scipy import stats
import pandas as pd
import seaborn as sns

#plt.style.use('ggplot')
#plt.rcParams['figure.figsize'] = 8,6
from matplotlib import rc
rc('text', usetex=True)

os.chdir('../pdf_processing/')
import pdf_processing as pdf; reload(pdf)
os.chdir('../gmt/')

# variables
varin_dict={
    'TXx':{'var_name':'tasmax','longname':'Hot extremes (TXx)','unit':'TXx [$^\circ$ C]','cut_interval':[-1.5,3.5]},
    }

with open('data/varoutdict_cmip5_rcp85_TXx.pkl', 'rb') as input:
    cmip5_dict = pickle.load(input)

with open('data/varoutdict_cmip5_rcp85_TXx_models_merged.pkl', 'rb') as input:
    all_cmip5 = pickle.load(input)

N_model=len(cmip5_dict.keys())

current_palette = sns.color_palette()
blue=current_palette[0]
red=current_palette[2]
cyan=current_palette[3]
time_slice_dict={
	1:{'name':'1.587_ref','longname':'HadCRUT4 method\nas in AR5','color':blue,'light_color':'cornflowerblue'},
	2:{'name':'1.695_ref','longname':'HadCRUT4 method\nanomaly to preindustrial','color':red,'light_color':'tomato'},
	3:{'name':'1.5_ref','longname':'TAS as in AR5','color':cyan,'light_color':'plum'},
}

plt.clf()
f=plt.figure(figsize=(5,5))
for time_slice in [1,2,3]:

    plt.plot(all_cmip5._distributions['global']['pdf']['xaxis'],cmip5_dict[model]['TXx']._distributions['global']['pdf'][time_slice_dict[time_slice]['name']],linewidth=1.5,color=time_slice_dict[time_slice]['color'],label=time_slice_dict[time_slice]['longname'])

plt.plot([0,0],[0,1],color='k')
plt.ylim((0,0.012))
plt.xlim((-0.8,3))
plt.ylabel('land fraction')
plt.xlabel(varin_dict['TXx']['unit'])
plt.legend(loc='upper right',fontsize=9)
plt.title('"1.5$^\circ$C"-impacts\nusing different GMT-calculations')
plt.tight_layout()
plt.savefig('plots/TXx.png',dpi=300)
plt.savefig('plots/TXx.pdf')


# cmip5 envelopes overview
plt.clf()
f=plt.figure(figsize=(5,5))
for time_slice in [3,1,2]:
    PDFs=np.zeros([512,N_model])*np.nan
    for model,mod_index in zip(cmip5_dict.keys(),range(N_model)):
        try:
            #plt.plot(cmip5_dict[model]['TXx']._distributions['global']['pdf']['xaxis'],cmip5_dict[model]['TXx']._distributions['global']['pdf'][time_slice_dict[time_slice]['name']],linewidth=0.3,color=time_slice_dict[time_slice]['light_color'])
            PDFs[:,mod_index]=cmip5_dict[model]['TXx']._distributions['global']['pdf'][time_slice_dict[time_slice]['name']]
        except:
            pass

    upper=np.nanpercentile(PDFs,100,axis=1)
    lower=np.nanpercentile(PDFs,0,axis=1)
    plt.fill_between(cmip5_dict['ACCESS1-0']['TXx']._distributions['global']['pdf']['xaxis'],upper,lower,color=time_slice_dict[time_slice]['light_color'],alpha=0.25)

for time_slice in [3,1,2]:
    plt.plot(all_cmip5._distributions['global']['pdf']['xaxis'],cmip5_dict[model]['TXx']._distributions['global']['pdf'][time_slice_dict[time_slice]['name']],linewidth=1.5,color=time_slice_dict[time_slice]['color'],label=time_slice_dict[time_slice]['longname'])

plt.plot([0,0],[0,1],color='k')
plt.ylim((0,0.02))
plt.xlim((-0.8,3))
plt.ylabel('land fraction')
plt.xlabel(varin_dict['TXx']['unit'])
plt.legend(loc='upper right',fontsize=10)
#plt.title('"1.5$^\circ$C"-impacts\nusing different GMT-calculations')
plt.tight_layout()
plt.savefig('plots/TXx_overview.png',dpi=300)
plt.savefig('plots/TXx_overview.pdf')






#jk
