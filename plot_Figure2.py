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

slr=pd.read_csv('data/slr_2100_temperature_levels_1p5_1p66_ref1986_2005.csv')


plot_dict={
	'gmt_sat':{'wlvl':1.4622,'name':'1.4468_ref','light_color':'orange','color':'darkorange','longname':'$\mathregular{GMT_{SAT}}$','pos':3,'lsty':'-'},
	'gmt_ar5':{'wlvl':1.5,'name':'1.5_ref','light_color':'lawngreen','color':sns.color_palette()[1],'longname':'$\mathregular{GMT_{AR5}}$','pos':0,'lsty':'--'},
	'gmt_millar':{'wlvl':1.66,'name':'1.66_ref','light_color':'cornflowerblue','color':sns.color_palette()[0],'longname':'$\mathregular{GMT_{M17}}$','pos':1,'lsty':'-'},
	'gmt_bm':{'wlvl':1.7,'name':'1.6584_ref','light_color':'tomato','color':sns.color_palette()[2],'longname':'$\mathregular{GMT_{blend-mask}}$','pos':2,'lsty':'-'},
}

# Figure 2
plt.clf()
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(10,5))
ax=axes.flatten()
for time_slice in ['gmt_ar5','gmt_millar']:
    PDFs=np.zeros([512,len(cmip5_dict.keys())])*np.nan
    for model,mod_index in zip(cmip5_dict.keys(),range(len(cmip5_dict.keys()))):
        try:
            #plt.plot(cmip5_dict[model]['TXx']._distributions['global']['pdf']['xaxis'],cmip5_dict[model]['TXx']._distributions['global']['pdf'][plot_dict[time_slice]['name']],linewidth=0.3,color=plot_dict[time_slice]['light_color'])
            PDFs[:,mod_index]=cmip5_dict[model]['TXx']._distributions['global']['pdf'][plot_dict[time_slice]['name']]
        except:
            pass

    upper=np.nanpercentile(PDFs,100,axis=1)
    lower=np.nanpercentile(PDFs,0,axis=1)
    ax[0].fill_between(cmip5_dict['ACCESS1-0']['TXx']._distributions['global']['pdf']['xaxis'],upper,lower,color=plot_dict[time_slice]['light_color'],alpha=0.25)

for time_slice in ['gmt_ar5','gmt_millar']:
    ax[0].plot(all_cmip5._distributions['global']['pdf']['xaxis'],all_cmip5._distributions['global']['pdf'][plot_dict[time_slice]['name']],linewidth=1.5,color=plot_dict[time_slice]['color'],label=plot_dict[time_slice]['longname'])

ax[0].plot([0,0],[0,1],color='k')
ax[0].set_ylim((0,0.02))
ax[0].set_xlim((-0.8,3))
ax[0].set_yticks(np.arange(0,0.0175,0.0025))
ax[0].text(-0.1, 1.02, 'a', transform=ax[0].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[0].set_ylabel('land fraction')
ax[0].set_xlabel('$\mathregular{TXx}$ $\mathregular{[^\circ C]}$')
ax[0].legend(loc='upper right',fontsize=10)
ax[0].set_title('Hot extremes (Txx)')

for time_slice in ['gmt_ar5','gmt_millar']:
    y=np.array(slr[str(plot_dict[time_slice]['wlvl'])])
    qu=np.nanpercentile(y,[5,1/6.*100,50,5/6.*100,95])
    x=plot_dict[time_slice]['pos']
    #ax[1].plot([x,x],[qu[0],qu[4]],lw=2,color=plot_dict[time_slice]['color'])
    ax[1].fill_between([x-0.03,x+0.03],[qu[1],qu[1]],[qu[3],qu[3]],lw=2,color=plot_dict[time_slice]['color'])
    ax[1].plot([x-0.03,x+0.03],[qu[2],qu[2]],lw=2,color='white')
    #ax[1].scatter([x],[np.nanmean(y)],marker='*',s=40,color='white')

#ax[1].set_ylim((0.25,0.6))
ax[1].set_xlim((-0.5,1.5))
ax[1].set_xticks([plot_dict[time_slice]['pos'] for time_slice in ['gmt_ar5','gmt_millar']])
ax[1].set_xticklabels([plot_dict[time_slice]['longname'] for time_slice in ['gmt_ar5','gmt_millar']])
ax[1].set_ylabel('Sea level rise in 2100 [m]')
ax[1].text(-0.1, 1.02, 'b', transform=ax[1].transAxes,fontsize=18, fontweight='bold', va='top', ha='right')
ax[1].legend(loc='upper right',fontsize=10)
ax[1].set_title('Sea level rise in 2100')

plt.tight_layout()
plt.savefig('plots/Figure2.png',dpi=300)
plt.savefig('plots/Figure2.pdf')

# number
x=all_cmip5._distributions['global']['pdf']['xaxis']
gmt_ar5_txx=all_cmip5._distributions['global']['pdf']['1.5_ref']
gmt_millar_txx=all_cmip5._distributions['global']['pdf']['1.66_ref']

print sum(gmt_ar5_txx[x>1])
print sum(gmt_millar_txx[x>1])
print sum(gmt_ar5_txx[x>1.5])
print sum(gmt_millar_txx[x>1.5])

for time_slice in ['gmt_ar5','gmt_millar']:
    y=np.array(slr[str(plot_dict[time_slice]['wlvl'])])
    qu=np.nanpercentile(y,[5,1/6.*100,50,5/6.*100,95])
    print time_slice,qu

# #SLR check
# plt.clf()
# for time_slice in ['1.46','1.59','1.7']:
#     sns.distplot(slr[time_slice],label=time_slice,bins=np.arange(-0.3,1.2,0.01))
#     #plt.plot(hist[1][1:]-0.005,hist[0],color=plot_dict[time_slice]['color'],label=plot_dict[time_slice]['longname'])
# plt.xlabel('SLR in 2100 [m]')
# #plt.ylabel('count')
# plt.legend(loc='upper right')
# plt.savefig('plots/test.png')


# TXx only
# plt.clf()
# f=plt.figure(figsize=(5,5))
# for time_slice in [1,2,3]:
#     plt.plot(all_cmip5._distributions['global']['pdf']['xaxis'],cmip5_dict['ACCESS1-0']['TXx']._distributions['global']['pdf'][plot_dict[time_slice]['name']],linewidth=1.5,color=plot_dict[time_slice]['color'],label=plot_dict[time_slice]['longname'])
#     print plot_dict[time_slice]['longname']
#
# plt.plot([0,0],[0,1],color='k')
# plt.ylim((0,0.012))
# plt.xlim((-0.8,3))
# plt.ylabel('land fraction')
# plt.xlabel('$\mathregular{TXx}$ $\mathregular{[^\circ C]}$')
# plt.legend(loc='upper right',fontsize=9)
# plt.tight_layout()
# plt.savefig('plots/TXx.png',dpi=300)
# plt.savefig('plots/TXx.pdf')
