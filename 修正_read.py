# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 09:59:47 2021

@author: yrtst
"""

#Extract data from txt files and write to csv file
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
#create the head；创建表头
B=pd.DataFrame(columns=['year','number','name','time','strength','lon','lat','wind','pressure'])
f=open('D:\\111\\77-86.txt',"r")
T=f.readlines()
f.close()
j=0
#use the len() to find the number of line  用len来找到有多少行
while(j<len(T)):
    
    if(T[j][0:5]=="66666"):
        k=j+1
        while(k<len(T) and T[k][0:5]!="66666"):
            YEAR=int(str(datetime.strptime(str(T[k][0:8]),"%y%m%d%H").year)\
            [:2]+str(T[k][0:2])),
            NUMBER=int(T[j][6:10])
            NAME=T[j][30:50].strip()
            TIME=datetime.strptime(str(T[k][0:8]),"%y%m%d%H")
            STRENGTH=str(T[k][13])
            LON=float(T[k][19:23])*0.1
            LAT=float(T[k][15:18])*0.1
            WIND=int(T[k][33:36])
            PRESSURE=float(T[k][24:28])
            if NAME=='':
                NAME = 'NONAME'
            
            T1={'year':YEAR,
                'number':NUMBER,
                'name':NAME,
                'time':TIME, 
                'strength':STRENGTH,
                'lon':LON,
                'lat':LAT,
                'wind':WIND,
                'pressure':PRESSURE}
            B=B.append(T1,ignore_index=True)
            k=k+1
    j=j+1

B.to_csv('D:\\111\\77-86',encoding='gbk') 






