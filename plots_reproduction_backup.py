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

gmt_raw=da.read_nc('data/gmt_all_remapdis.nc')['gmt']
model_runs=sorted(gmt_raw.model_run)
for model_run in gmt_raw.model_run:
	if model_run.split('_')[0] in ['CESM1-CAM5','BNU-ESM','bcc-csm1-1-m','CESM1-WACCM']:
		model_runs.remove(model_run)
	elif np.isnan(np.nanmean(gmt_raw['xax','rcp85',model_run,'gmt',:].values)):
		model_runs.remove(model_run)

model_runs.remove('EC-EARTH_r7i1p1')
model_runs.remove('EC-EARTH_r11i1p1')
model_runs.remove('EC-EARTH_r12i1p1')
model_runs.remove('EC-EARTH_r13i1p1')
model_runs.remove('EC-EARTH_r14i1p1')

gmt_all_clean=gmt_raw[gmt_raw.style,gmt_raw.scenario,model_runs,gmt_raw.variable,gmt_raw.time]
gmt_year=yearly_anomaly(gmt_all_clean)

models=sorted(set([model_run.split('_')[0] for model_run in model_runs]))
gmt_model=da.DimArray(axes=[gmt_raw.style,gmt_raw.scenario,models,gmt_raw.variable,np.arange(1850,2100,1)],dims=['style','scenario','model','variable','time'])
for model in models:
	ensemble=[model_run for model_run in model_runs if model_run.split('_')[0]==model]
	print model, ensemble
	gmt_model[:,:,model,:,:]=np.nanmean(gmt_year[:,:,ensemble,:,:],axis=2)

dat=open('data/Had4_gmt.txt','r').read()
had4=[]
read='yes'
for line in dat.split('\n')[::2]:
	for anom in line.split(' ')[2:-1]:
		if anom!='':
			had4.append(float(anom))

had4=np.array(had4[11*12:-12])

gmt_richardson=da.read_nc('data/gmt_all_richardson.nc')['gmt']
gmt_richardson.values-=np.expand_dims(np.nanmean(gmt_richardson[:,:,:,:,1860:1880].values,axis=4),axis=4)

gmt_cowtan=da.read_nc('data/gmt_all_cowtan.nc')['gmt']
gmt_cowtan_year=yearly_anomaly(gmt_cowtan[:,:,gmt_richardson.model_run,:,:])

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

plot_dict={'Peter model average':{'data':gmt_model,'colors':['yellow','pink','cyan']},
			'Peter':{'data':gmt_year,'colors':['orange','plum','lightblue']},
			'Cowtan':{'data':gmt_cowtan_year,'colors':['darkred','darkviolet','darkblue']},
			'Richardson':{'data':gmt_richardson,'colors':['red','magenta','blue']}}

names=['Richardson','Cowtan','Peter','Peter model average']

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
missing_runs=sorted([run for run in gmt_richardson.model_run if run not in gmt_year.model_run])
missing_models=sorted(set([run.split('_')[0] for run in gmt_richardson.model_run if run.split('_')[0] not in gmt_model.model]))

#CESM1-CAM5_r1i1p1	CESM1-CAM5_r2i1p1	CESM1-CAM5_r3i1p1	EC-EARTH_r12i1p1	FIO-ESM_r1i1p1	FIO-ESM_r2i1p1	FIO-ESM_r3i1p1	GISS-E2-H-CC_r1i1p1	GISS-E2-H_r2i1p1	GISS-E2-H_r2i1p3	GISS-E2-R-CC_r1i1p1	GISS-E2-R_r2i1p1	GISS-E2-R_r2i1p3	MRI-ESM1_r1i1p1	bcc-csm1-1_r1i1p1	inmcm4_r1i1p1

#CESM1-CAM5	FIO-ESM	GISS-E2-H-CC	GISS-E2-R-CC	MRI-ESM1	bcc-csm1-1	inmcm4

#ACCESS1-0	ACCESS1-3	CCSM4	CESM1-BGC	CMCC-CM	CMCC-CMS	CNRM-CM5	CSIRO-Mk3-6-0	CanESM2	EC-EARTH	GFDL-CM3	GFDL-ESM2G	GFDL-ESM2M	GISS-E2-H	GISS-E2-R	HadGEM2-AO	HadGEM2-CC	HadGEM2-ES	IPSL-CM5A-LR	IPSL-CM5A-MR	IPSL-CM5B-LR	MIROC-ESM	MIROC-ESM-CHEM	MIROC5	MPI-ESM-LR	MPI-ESM-MR	MRI-CGCM3	NorESM1-M	NorESM1-ME
