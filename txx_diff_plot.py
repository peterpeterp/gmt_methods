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
import pdf_processing as pdf; reload(pdf)
os.chdir('../gmt/')

# variables
varin_dict={
    'TXx':{'var_name':'tasmax','longname':'Hot extremes (TXx)','unit':'TXx [$^\circ$ C]','cut_interval':[-1,1]},
    }

with open('data/varoutdict_cmip5_rcp85_TXx.pkl', 'rb') as input:
    cmip5_dict = pickle.load(input)

N_model=len(cmip5_dict.keys())

time_slice_dict={
	1:{'name':'1.587_ref','longname':'Blended-masked\nas in AR5','color':'darkmagenta'},
	2:{'name':'1.695_ref','longname':'Blended-masked\nanomaly to preindustrial','color':'darkcyan'},
	3:{'name':'1.5_ref','longname':'TAS\nas in AR5','color':'blue'},

}

# cmip5
plt.clf()
f=plt.figure(figsize=(5,5))
ensemble=open('ensemble_TXx.txt','w')
for time_slice in [1,2,3]:
    PDFs=np.zeros([512,N_model])*np.nan
    for model,mod_index in zip(cmip5_dict.keys(),range(N_model)):
        try:
            #plt.plot(cmip5_dict[model][var]._distributions['global']['pdf']['xaxis'],cmip5_dict[model][var]._distributions['global']['pdf'][time_slice_dict[time_slice]['name']],linewidth=0.3,color=time_slice_dict[time_slice]['color'])
            PDFs[:,mod_index]=cmip5_dict[model]['TXx']._distributions['global']['pdf'][time_slice_dict[time_slice]['name']]
            if time_slice==1:   ensemble.write(model+'\n')
        except:
            pass

    upper=np.nanpercentile(PDFs,100,axis=1)
    lower=np.nanpercentile(PDFs,0,axis=1)
    plt.fill_between(cmip5_dict['ACCESS1-0']['TXx']._distributions['global']['pdf']['xaxis'],upper,lower,color=time_slice_dict[time_slice]['color'],alpha=0.25,label=time_slice_dict[time_slice]['longname'])

    #plt.plot([-999,-999],[-999,-999],linewidth=1,color=time_slice_dict[time_slice]['color'],label=time_slice_dict[time_slice]['longname'])

plt.plot([0,0],[0,1],color='k')
plt.ylim((0,0.02))
plt.xlim((-1.5,3))
plt.ylabel('land franction')
plt.xlabel(varin_dict['TXx']['unit'])
plt.legend(loc='upper left',fontsize=8)
plt.title('"1.5$^\circ$C"-impacts\nusing different GMT-calculations')
plt.tight_layout()
plt.savefig('plots/TXx.png',dpi=300)
plt.savefig('plots/TXx.pdf')

ensemble.close()





#jk
