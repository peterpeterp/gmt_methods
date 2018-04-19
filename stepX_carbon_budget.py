
# get conversion factor based on November submit
x=np.array([1.57,1.35,1.77,1.34,1.16,1.40,1.30,1.17,1.59])
y=np.array([156.,-333,600,-356,-756,-222,-444,-733,200])
x-=1.5

m=[(y[i+1]-y[i+0])/(x[i+1]-x[i+0]) for i in range(len(x)-1)]
factor=np.mean(m)

# compute new budgets
x=np.array([1.52,1.05,1.88,1.32,1.06,1.53,1.31,0.85,1.77])
x-=1.5
y=factor*x
print np.round(y)

# [   44 -1000   845  -400  -978    67  -422 -1445   600]
