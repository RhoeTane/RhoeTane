# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 10:18:54 2021

@author: yrtst
"""

#Extract data from txt files and write to csv file
import pandas as pd
import numpy as np
import datetime

B=pd.DataFrame(columns=['year','number','name','time','strength','lon','lat','wind','pressure'])
for i in range(1949,2021):
  print(i)
  #The data is publicly available at http://tcdata.typhoon.org.cn/zjljsjj_zlhq.html
  #If you used these data in you publications, make sure to cite the research papers list on the above-mentioned webpage
  #The data of previous year are usually available at April, now the dataset contains data from 1949 to 2020
  f=open("./Best Track Dataset/CH"+str(i)+"BST.txt","r")
  T=f.readlines()
  f.close()
  j=0

  #parsing the track data, the format of the track data can be found at
  #http://tcdata.typhoon.org.cn/zjljsjj_sm.html
  while(j<len(T)):
    if(T[j][0:5]=="66666"):
        k=j+1
        while(k<len(T) and T[k][0:5]!="66666"):
          T1={'year':i,'number':int(T[j][16:20]),'name':T[j][30:50].rstrip(),'time':datetime.datetime(int(T[k][0:4]),int(T[k][4:6]),\
            int(T[k][6:8]),int(T[k][8:10])), 'strength':int(T[k][11]),'lon':float(T[k][17:21])/10,\
              'lat':float(T[k][13:16])/10,'wind':int(T[k][32:34]),'pressure':int(T[k][22:26])}
          B=B.append(T1,ignore_index=True)
          k=k+1
    j=j+1

B.to_csv('./typhoon_tracks.csv',encoding='gbk') 





import sqlite3
import pandas as pd

#connect to the data base
conn = sqlite3.connect('./typhoon_track.db')

#read data
A=pd.read_csv('./typhoon_tracks.csv',engine='python',encoding='gbk',index_col=0)

#insert to the database
A.to_sql(name="track", con=conn, if_exists='replace', index=False)

#close database
conn.close()




import sqlite3
import pandas as pd

#connect to the data base
conn = sqlite3.connect('./typhoon_track.db')

#read data
#This data is originall from http://tcdata.typhoon.org.cn/dlrdqx_zl.html
#I selected those typhoons that landed at east China which was my research target area
#I also added the typhoon landfall time and landfall wind speed to this table (extracted by using the typhoon landfall analysis cell)
A=pd.read_excel('./landfall_typhoon.xlsx')

#insert to the database
A.to_sql(name="landfall", con=conn, if_exists='replace', index=False)

#close database
conn.close()





'''
2. Analysis the pattern of the typhoon occurence at east China
'''





import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pylab import mpl
import copy
import sqlite3
mpl.rcParams['font.sans-serif'] = ['Times New Roman'] 

#connect to the database
conn = sqlite3.connect('./typhoon_track.db')

#read track data
sql=" select * \
     from track;"
C=pd.read_sql_query(sql,conn)

#read landfall data
sql=" select * \
     from landfall;"
D=pd.read_sql_query(sql,conn)

#close database connection
conn.close()

#keep only those typhoons that is very risky
D=D[(D.landfall_wind>32.6)]

fig, ax = plt.subplots(figsize=[8,6])

#plot the base map
ax.set_facecolor('cornflowerblue')
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world.plot(ax=ax,facecolor='white')
#GDAM mapa data are publicly available at https://gadm.org/
A=gpd.read_file('./GDAM Map Dataset/gadm36_CHN_1.shp')
A.plot(ax=ax,facecolor='whitesmoke',edgecolor='black',linewidth=1)

i1=0
i2=0
i3=0
for i in range(0,len(D)):
    T=copy.deepcopy(C[np.logical_and(C.year==D.year.iloc[i],C.number==D.number.iloc[i])])
    T=T.sort_values('time')
    if D.landfall_wind.iloc[i]<41.5:
      if i1==0:
        plt.plot(T.lon,T.lat,'aqua',label="TY")
        i1=i1+1
      else:
        plt.plot(T.lon,T.lat,'aqua')
        
    elif D.landfall_wind.iloc[i]<50.9:
        if i2==0:
            plt.plot(T.lon,T.lat,'wheat',label='STY')
            i2=i2+1
        else:
             plt.plot(T.lon,T.lat,'wheat')
    else:
        if i3==0:
             plt.plot(T.lon,T.lat,'darkorange',label='SuperTY')  
             i3=i3+1
        else:
              plt.plot(T.lon,T.lat,'darkorange')  
plt.legend(loc='upper left',fontsize=12,framealpha=0.7)
plt.xticks([])
plt.yticks([])
plt.xlim((100,155))
plt.ylim((19,53))
plt.title("Historical typhoon tracks",fontsize=14)
plt.savefig('./historical_typhoon_tracks.png',dpi=200,bbox_inches='tight')


'''
visulize the total number of typhoon that landfalled at certain proinces,
 which shows the Fujian and Zhejiang provinces are the two most frequently hit by typhoon.

'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pylab import mpl
import copy
import sqlite3
mpl.rcParams['font.sans-serif'] = ['Times New Roman'] 

#connect to the database
conn = sqlite3.connect('./typhoon_track.db')

#read landfall data
sql=" select * \
     from landfall;"
D=pd.read_sql_query(sql,conn)

#close database connection
conn.close()

#group of less risky typhoon
C1=D[(D.landfall_wind<32.6)]
A=D.groupby('province').size()
A=A.sort_values(ascending=False)

#group of very risk typhoon
C2=D[D.landfall_wind>=32.6]
B=C2.groupby('province').size()
B=B.sort_values(ascending=False)

fig, ax = plt.subplots(figsize=[8,6])
plt.bar(A.index,A,label="TY and below")
plt.bar(B.index,B,label="STY and above")
for i in range(0,len(A)):
    plt.text(A.index[i],A[i]+0.3,str(A[i]),fontsize=12)
plt.legend(loc='upper right',fontsize=12,framealpha=0.7)
ax.tick_params(axis='both',labelsize=12)
plt.xlabel("Province",fontsize=12)
plt.ylabel("Number of typhoon landfall",fontsize=12)
plt.title("Distribution of number of Typhoon Landfall",fontsize=14)
plt.ylim((0,126))
plt.savefig('./landfall_province.png',dpi=200,bbox_inches='tight')




'''
Visualize the Typhoon Temperal and Strength Distribution. 
This distribution shows that the most powerful typhoons usually occur in July and August. 
This is because the high ocean water temperature in this period can strenthen the typhoon before its landfall.
'''


import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['Times New Roman'] 

#connect to the database
conn = sqlite3.connect('./typhoon_track.db')

#read landfall data
sql=" select * \
     from landfall;"
B=pd.read_sql_query(sql,conn)
B.landfall_time=pd.to_datetime(B.landfall_time)

#close database connection
conn.close()

fig, ax = plt.subplots(figsize=[12,6])
plt.grid()
A=B[(B.landfall_wind<24.5)]
ax.scatter(A.landfall_time.dt.year,A.landfall_time.dt.month+A.landfall_time.dt.day/30,A.landfall_wind*3,color='aqua',label='TS')
A=B[np.logical_and(B.landfall_wind<32.6,B.landfall_wind>=24.5)]
ax.scatter(A.landfall_time.dt.year,A.landfall_time.dt.month+A.landfall_time.dt.day/30,A.landfall_wind*4,color='turquoise',label='STS')
A=B[np.logical_and(B.landfall_wind<41.5,B.landfall_wind>=32.6)]
ax.scatter(A.landfall_time.dt.year,A.landfall_time.dt.month+A.landfall_time.dt.day/30,A.landfall_wind*4,color='silver',label='TY')
A=B[np.logical_and(B.landfall_wind<50.9,B.landfall_wind>=41.6)]
ax.scatter(A.landfall_time.dt.year,A.landfall_time.dt.month+A.landfall_time.dt.day/30,A.landfall_wind*4,color='wheat',label='STY')
A=B[(B.landfall_wind>50.9)]
ax.scatter(A.landfall_time.dt.year,A.landfall_time.dt.month+A.landfall_time.dt.day/30,A.landfall_wind*4,color='darkorange',label='SuperTY')
for i in range(0,len(A)):
  ax.text(A.landfall_time.dt.year.iloc[i]-1.7,A.landfall_time.dt.month.iloc[i]+A.landfall_time.dt.day.iloc[i]/30,A.name.iloc[i],fontsize=12)
plt.legend(loc='lower right',fontsize=12,framealpha=0.2)
plt.xlabel("Year",fontsize=12)
plt.ylabel("Month",fontsize=12)
plt.tick_params(labelsize=12)
plt.title("Typhoon Temperal and Strength Distribution",fontsize=14)
plt.savefig("./temperal_strength.png",dpi=200,bbox_inches='tight')






'''
3. Investigate the power grid faults caused by typhoon
Regression of max wind speed and number of faults. 
It shows that the number of fault transmission lines and the maximum wind speed of typhoon generally follow the exponential relationship.

'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import functools

mpl.rcParams['font.sans-serif'] = "Times New Roman" # 指定默认字体
A=pd.read_excel('./max_wind_vs_line_trip.xlsx')

plt.plot(A.maxwind,A.linetrip,'o')
B=[20.0,25.0,30.0, 35.0, 40.0, 45.0, 50.0, 55.0]
C=[0,0,0,0,0,0,0,0]
for i in range(0,len(B)):
  C[i]=[np.exp((B[i]-18)*0.14)]

plt.plot(B,C)
plt.grid()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Maximum Wind Speed(m/s)',fontsize=14)
plt.ylabel('Number of Fault Transmission Lines ',fontsize=14)
plt.text(27,130,'y=exp((x-18)*0.14)',fontsize=14,backgroundcolor='white')

plt.savefig('./max_wind_vs_line_trip.png',dpi=200,bbox_inches='tight')

'''
visualize the geological distribution of faults. 
It shows the fault towers are mainly locate at the close proximity of the coast line, 
which is because typhoon’s intensity usually attenuate quickly after landfall 
so the strong wind of typhoon only threaten the transmission towers close to the coastline.
'''


#Don't execute it since the fault location data is not publicly available
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from pylab import mpl
mpl.rcParams['font.sans-serif'] = "Times New Roman"  

#read data
A=gpd.read_file(ADD1+'map/bou2_4l.shp')
B=gpd.read_file(ADD1+'map/diquJie_polyline.shp')
ZHEJIANG_SHAPE=gpd.read_file(ADD1+'.map/bou2_4l.shp')
ZheJiang=gpd.read_file('.map/浙江省（裁剪）.shp')
FuJian=gpd.read_file('.map/福建省（裁剪）.shp')

T1=pd.read_excel('./faultdata.xlsx') #this fault data is not publicly available

#plot
fig, ax = plt.subplots(figsize=[12.6,9])
ZheJiang.plot(ax=ax,facecolor=(0.8,0.8,0.8))
FuJian.plot(ax=ax,facecolor=(0.8,0.8,0.8))
A.plot(ax=ax,edgecolor='black',linewidth=1)
B.plot(ax=ax,linestyle='dashed',edgecolor='black',linewidth=1)
ax.plot(T1.lon,T1.lat,'ro',markersize=3,label='Fault towers')
plt.text(119.3,29,'Zhejiang',fontsize=14,backgroundcolor='white')
plt.text(117.2,26,'Fujian',fontsize=14,backgroundcolor='white')
plt.xticks([])
plt.yticks([])
plt.xlim((115.8,122.5))
plt.ylim((23.5,31.3))
plt.legend(loc='upper left',fontsize=14,facecolor='white')
plt.savefig('./fault_location.png',dpi=200,bbox_inches='tight')




'''
Histogram of distance between fault towers and coast line, 
which shows most of the fault towers are within 50km vicinity of the coastlines
'''


#Don't execute it since the fault location data is not publicly available
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import functools

mpl.rcParams['font.sans-serif'] = "Times New Roman" # 指定默认字体
A=pd.read_excel('./faultdata.xlsx') #this fault data is not publicly available
plt.hist(A.dist_coast,50,rwidth=0.8)
plt.grid()
plt.xlim((0,100))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Distance to coastline(km)',fontsize=12)
plt.ylabel('Number of faults',fontsize=12)
plt.savefig('./distance_coastline.png',dpi=200,bbox_inches='tight')





'''
Histogram of distance between fault towers to the landfall center. 
The number of faults increases gradually when the distance between 
the transmission towers to the typhoon centres increase from 0 to 30km, 
which is the wind speed in typhoon’s eye is low 
and the highest wind speed usually appears at the eye walls of typhoons. 
The radius of a strong typhoon’s eyewall is approximately 30km which coincident 
with the highest number of the faults. 
The number of faults then decreases gradually when the distance increase from 30km to 100km, 
because the wind speed decrease gradually.

'''



#Don't execute it since the fault location data is not publicly available
import numpy as np
import pandas as pd
from pylab import mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.sans-serif'] = "Times New Roman" 

A=pd.read_excel('./faultdata.xlsx') #this fault data is not publicly available
plt.hist(A.dist_landfall,70,rwidth=0.8)
plt.grid()
plt.xlim((0,200))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Distance to typhoon centre (km)',fontsize=12)
plt.ylabel('Number of faults',fontsize=12)
plt.savefig('./dist_landfall.png',dpi=200,bbox_inches='tight')




'''
Latitude difference between faults and typhoon center.
 The distribution is positively biased with mean value of 0.402°, 
 and 82.7% of the fault towers are at higher latitude than that of the typhoon center. 
 This is because in the east coast of China, the typhoons are spinning in counter-clockwise direction, 
 and the wind in the north side of the typhoon center are blowing from the sea to land, 
 which is usually more turbulent and thus more hazards to transmission lines.
'''

import numpy as np
import pandas as pd
from pylab import mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.sans-serif'] = "Times New Roman" 

A=pd.read_excel('./faultdata.xlsx') #this fault data is not publicly available
plt.hist(A.latitude,70,rwidth=0.8)
plt.grid()
plt.xlim((-2,3))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Latitude difference (°)',fontsize=12)
plt.ylabel('Number of faults',fontsize=12)
plt.savefig('./latitude.png',dpi=200,bbox_inches='tight')



'''
Monthly distribution of faults, where all the faults were happened during 
July to October while faults in August and September account for 76.4% of all the faults. 
The monthly variation of number of faults is dominated 
by the tropical cyclone formation and landfall in the north western Pacific Ocean.

'''


import numpy as np
import pandas as pd
from pylab import mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.sans-serif'] = "Times New Roman" # 指定默认字体

A=pd.read_excel('./monthly_fault.xlsx')
plt.bar(A.month,A.faults)
plt.grid()
plt.xlim((0,11))
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Month',fontsize=12)
plt.ylabel('Number of faults',fontsize=12)
plt.savefig('./monthly_fault.png',dpi=200,bbox_inches='tight')



'''

Time interval between landfalls and faults. 69.6% of the faults are happened 
during 2 hours before landfall to 1 hour after landfall. 
This time period is when the eye wall of the typhoons hitting the land that is the wildest moment of typhoon.
'''

A=pd.read_excel('./time_diff.xlsx')
plt.hist(A.time*24,80,rwidth=0.8)
plt.grid()
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlim((-15,15))
plt.xlabel('Time interval between landfalls and faults (h)',fontsize=12)
plt.ylabel('Number of faults',fontsize=12)
plt.savefig('./time_diff.png',dpi=200,bbox_inches='tight')










