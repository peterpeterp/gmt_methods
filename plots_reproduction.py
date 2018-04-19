import os,sys,glob,time,collections,gc
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import matplotlib.pylab as plt
import dimarray as da
import itertools
import matplotlib


def running_mean_func(xx,N):
	if N==1:
		return xx
	if N!=1:
	    x=np.ma.masked_invalid(xx.copy())
	    ru_mean=x.copy()*np.nan
	    for t in range(int(N/2),len(x)-int(N/2)):
	        ru_mean[t]=np.nanmean(x[t-int(N/2):t+int(N/2)])
	    return ru_mean

def yearly_anomaly(gmt_in,ref_period=[1861,1880]):
	gmt_anom=gmt_in
	# anomaly to preindustrial
	gmt_anom.values-=np.expand_dims(np.nanmean(gmt_anom[:,:,:,:,ref_period[0]:ref_period[1]].values,axis=4),axis=4)

	# yearly values
	gmt_year=da.DimArray(axes=[gmt_in.style,gmt_in.scenario,gmt_in.model_run,gmt_in.variable,np.arange(1850,2100,1)],dims=['style','scenario','model_run','variable','time'])
	for model in gmt_year.model_run:
		for style in gmt_year.style:
			for var in gmt_year.variable:
				for year in gmt_year.time:
					gmt_year[style,'rcp85',model,var,year]=np.nanmean(gmt_anom[style,'rcp85',model,var,year:year+1])

	return gmt_year

gmt_year=da.read_nc('data/gmt_year_runs.nc')['gmt']
gmt_model=da.read_nc('data/gmt_year_model.nc')['gmt']

gmt_year.values-=np.expand_dims(np.nanmean(gmt_year[:,:,:,:,1861:1880].values,axis=4),axis=4)
gmt_model.values-=np.expand_dims(np.nanmean(gmt_model[:,:,:,:,1861:1880].values,axis=4),axis=4)

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
read='yes'
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4=np.array(had4[11*12:-12])

gmt_richardson=da.read_nc('data/gmt_all_richardson.nc')['gmt']
gmt_richardson.values-=np.expand_dims(np.nanmean(gmt_richardson[:,:,:,:,1861:1880].values,axis=4),axis=4)

gmt_cowtan=da.read_nc('data/gmt_all_cowtan.nc')['gmt']
gmt_cowtan_year=yearly_anomaly(gmt_cowtan[:,:,gmt_richardson.model_run,:,:])

plot_dict={'Peter model average':{'data':gmt_model,'colors':['yellow','pink','cyan']},
			'Peter':{'data':gmt_year,'colors':['orange','plum','lightblue']},
			'Cowtan':{'data':gmt_cowtan_year,'colors':['darkred','darkviolet','darkblue']},
			'Richardson':{'data':gmt_richardson,'colors':['red','magenta','blue']}}

names=['Richardson','Cowtan','Peter','Peter model average']


print('1986-2005')
for name in names[::-1]:
	print(name,np.nanpercentile(plot_dict[name]['data']['xax','rcp85',:,'air',1986:2005],50))

print('2021-2040')
for name in names[::-1]:
	print(name,np.nanpercentile(plot_dict[name]['data']['xax','rcp85',:,'air',2021:2040],50))


# richardson 1b
plt.close()
fig = plt.figure(figsize=(8,4))
ax1 = fig.add_subplot(1,2,1,ylim=[-0.4,1.2],xlim=[1861,2016])
ax2 = fig.add_subplot(1,2,2,ylim=[-0.25,0.05],xlim=[1861,2016])
#ax3 = fig.add_subplot(1,3,3,ylim=[-9999,-999],xlim=[99,999])

# set xlabels and xticks
for ax in [ax1,ax2]:
	ax.set_xticks(np.arange(1880,2021,40))
	ax.set_xlabel('Year',fontsize=16)

ax1.set_ylabel('$\Delta$T ($^\circ$C)',fontsize=16,labelpad=-5)
ax2.set_ylabel('$\Delta$T - $\Delta$T$_{tas}$ ($^\circ$C)',fontsize=16,
			   labelpad=0)

for name in names[::-1]:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax1.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'air',:],50,axis=0),colors[0])
	ax1.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'gmt',:],50,axis=0),colors[1])
	ax2.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],50,axis=0),colors[1])
	ax1.plot(data.time,np.nanpercentile(data['had4','rcp85',:,'gmt',:],50,axis=0),colors[2])
	ax2.plot(data.time,np.nanpercentile(data['had4','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],50,axis=0),colors[2])
	#ax2.plot(data.time,np.nanmean(data['had4','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],axis=0),colors[2],linewidth=0.2)

ax1.plot([0],[0],'white',label='tas-only')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax1.plot([0],[0],colors[0],label=name)

ax2.plot([0],[0],'white',label='blended')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax2.plot([0],[0],colors[1],label=name)
ax2.plot([0],[0],'white',label=' ')
ax2.plot([0],[0],'white',label='blended-masked')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax2.plot([0],[0],colors[2],label=name)

leg = ax1.legend(loc='upper center',frameon=False,handletextpad=0,fontsize=8)
leg = ax2.legend(loc='lower left',frameon=False,handletextpad=0,fontsize=8)

for ax in fig.get_axes():
	for ylab in ax.get_yticklabels():
		ylab.set_fontsize(11)
	for xlab in ax.get_xticklabels():
		xlab.set_fontsize(11)

# labelling of subplots
ax1.text(1865,1.07,'(a)',fontsize=20)
ax2.text(1990,0.025,'(b)',fontsize=20)
fig.subplots_adjust(0.08,0.12,0.98,0.97,wspace=0.26)
plt.savefig('plots/reproduction/richardson_fig1b.png',dpi=300)





# comparing ensembles
missing_runs=sorted([run for run in gmt_richardson.model_run if run not in gmt_year.model])
missing_models=sorted(set([run.split('_')[0] for run in gmt_richardson.model_run if run.split('_')[0] not in gmt_model.model]))


# richardson 1b but long
plt.close()
fig = plt.figure(figsize=(8,4))
ax1 = fig.add_subplot(1,2,1,ylim=[-0.4,4],xlim=[1850,2100])
ax2 = fig.add_subplot(1,2,2,ylim=[-0.5,0.05],xlim=[1850,2100])
#ax3 = fig.add_subplot(1,3,3,ylim=[-9999,-999],xlim=[99,999])

# set xlabels and xticks
for ax in [ax1,ax2]:
	ax.set_xticks(np.arange(1850,2100,40))
	ax.set_xlabel('Year',fontsize=16)

ax1.set_ylabel('$\Delta$T ($^\circ$C)',fontsize=16,labelpad=-5)
ax2.set_ylabel('$\Delta$T - $\Delta$T$_{tas}$ ($^\circ$C)',fontsize=16,
			   labelpad=0)

for name in names[::-1]:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax1.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'air',:],50,axis=0),colors[0])
	ax1.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'gmt',:],50,axis=0),colors[1])
	ax2.plot(data.time,np.nanpercentile(data['xax','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],50,axis=0),colors[1])
	ax1.plot(data.time,np.nanpercentile(data['had4','rcp85',:,'gmt',:],50,axis=0),colors[2])
	ax2.plot(data.time,np.nanpercentile(data['had4','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],50,axis=0),colors[2])
	#ax2.plot(data.time,np.nanmean(data['had4','rcp85',:,'gmt',:]-data['xax','rcp85',:,'air',:],axis=0),colors[2],linewidth=0.2)

ax1.plot([0],[0],'white',label='tas-only')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax1.plot([0],[0],colors[0],label=name)

ax2.plot([0],[0],'white',label='blended')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax2.plot([0],[0],colors[1],label=name)
ax2.plot([0],[0],'white',label=' ')
ax2.plot([0],[0],'white',label='blended-masked')
for name in names:
	data,colors=plot_dict[name]['data'],plot_dict[name]['colors']
	ax2.plot([0],[0],colors[2],label=name)

leg = ax1.legend(loc='upper center',frameon=False,handletextpad=0,fontsize=8)
leg = ax2.legend(loc='lower left',frameon=False,handletextpad=0,fontsize=8)

for ax in fig.get_axes():
	for ylab in ax.get_yticklabels():
		ylab.set_fontsize(11)
	for xlab in ax.get_xticklabels():
		xlab.set_fontsize(11)

# labelling of subplots
ax1.text(1865,1.07,'(a)',fontsize=20)
ax2.text(1990,0.025,'(b)',fontsize=20)
fig.subplots_adjust(0.08,0.12,0.98,0.97,wspace=0.26)
plt.savefig('plots/reproduction/richardson_fig1b_long.png',dpi=300)
