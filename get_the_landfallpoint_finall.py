# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 14:07:48 2021

@author: yrtst
"""
#带有黄色感叹号的模块虽然被导入后未使用，但如果不导入会由于兼容问题崩溃
import cartopy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from functools import reduce
from shapely.geometry import Polygon, Point, LineString, MultiLineString
from haversine import haversine
from shapely.ops import cascaded_union







'''
class datetime.timedelta
表示两个 date 对象或者 time 对象,或者 datetime 对象之间的时间间隔，精确到微秒。
'''
#create the head；创建表头
B=pd.DataFrame(columns=['year','number','name','time','strength','lon','lat','wind','pressure'])
f=open('D:\\111\\09-20.txt',"r")
T=f.readlines()
f.close()
j=0
#use the len() to find the number of line  用len来找到有多少行
while(j<len(T)):
    
    if(T[j][0:5]=="66666"):
        k=j+1
        while(k<len(T) and T[k][0:5]!="66666"):
            YEAR_0=datetime.strptime(str(T[k][0:2]),"%y").year,
            NUMBER=int(T[j][6:10])
            NAME=T[j][30:50].strip()
            TIME=datetime.strptime(str(T[k][0:8]),"%y%m%d%H")
            STRENGTH=str(T[k][13])
            LON=float(T[k][19:23])*0.1
            LAT=float(T[k][15:18])*0.1
            WIND=int(T[k][33:36])
            PRESSURE=float(T[k][24:28])
            YEAR=YEAR_0[0]

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

B.to_csv('D:\\111\\09-20.csv',encoding='gbk') 


dataset = pd.read_csv('D:\\111\\09-20.csv',header=0,sep=',')
dataset = np.array(dataset)
m ,n    = np.shape(dataset)

year  = dataset[:,1]
tyID    = dataset[:,2]
name    = dataset[:,3]
date    = dataset[:,4]
grades  = dataset[:,5]
lons    = dataset[:,-4]
lats    = dataset[:,-3]
wind  = dataset[:,-2]
pressure  = dataset[:,-1]

data      = {}

idata     = {} # empty dictionary

yearTemp  = []
tyIDTemp  = []
nameTemp  = []
dateTemp  = []
gradeTemp = []
lonTemp   = []
latTemp   = []
windTemp  = []
pressureTemp  = []



for i in range(m-1):
    tyID1 = tyID[i] 
    tyID2 = tyID[i+1]
    if tyID2==tyID1 :   #如果以下行的数据都属于同一个台风则将他们存储在Temp里
        latTemp.append(lats[i])
        lonTemp.append(lons[i])
        gradeTemp.append(grades[i])
        dateTemp.append(date[i])
        yearTemp.append(year[i])
        pressureTemp.append(pressure[i])
        windTemp.append(wind[i])
        nameTemp.append(str(name[i]))
    else:           #存储好除最后一行的单个台风的全部数据后以数组的形式存在字典里
        latTemp.append(lats[i])
        lonTemp.append(lons[i])
        gradeTemp.append(grades[i])
        dateTemp.append(date[i])
        yearTemp.append(year[i])
        pressureTemp.append(pressure[i])
        windTemp.append(wind[i])
        nameTemp.append(str(name[i]))      
        
        latTempArr = np.array(latTemp)
        lonTempArr = np.array(lonTemp)
        gradeTempArr = np.array(gradeTemp)
        dateTempArr = np.array(dateTemp)
        yearTempArr = np.array(yearTemp)
        pressureTempArr = np.array(pressureTemp)
        windTempArr = np.array(windTemp)
        nameTempArr = np.array(nameTemp)
        
        tyIDKey = str('%04d'%int(tyID1))
        
        
        idata['lat']   = latTempArr
        idata['lon']   = lonTempArr
        idata['grade'] = gradeTempArr
        idata['date']  = dateTempArr
        idata['year']  = yearTempArr
        idata['pressure']  = pressureTempArr
        idata['wind']  = windTempArr
        idata['name']  = nameTempArr
        
        data[tyIDKey]  = idata
        
        
        latTemp   = []
        lonTemp   = []
        gradeTemp = []
        dateTemp  = []
        yearTemp  = []
        pressureTemp  = []
        windTemp  = []
        nameTemp  = []
        
        idata     = {}

#print(len(data.keys()))



landfallPoints = {}

m = Basemap(resolution='h')
m.readshapefile(r'D:\222\gadm36_PHL_shp\gadm36_PHL_0','phl',drawbounds=False)

shapes=[]

for shape in m.phl:
    iprovincePoly = Polygon(shape)
    shapes.append(iprovincePoly)
coastline = cascaded_union(shapes)

insidePoly = coastline.buffer(-0.05)
targetPoly = coastline

num = 0

for tyID in data:
    iLandfallPoint = {}
    iTyData = data[tyID]
    lats    = iTyData['lat']
    lons    = iTyData['lon']
    grades  = iTyData['grade']
    date    = iTyData['date']
    year    = iTyData['year']
    wind    = iTyData['wind']
    pressure    = iTyData['pressure']
    
    
    x=lons
    y=lats
    line=LineString(zip(x, y))

    intersection = coastline.intersection(line)

    
    if intersection.is_empty:
        coor=False


    elif type(intersection) == LineString:
        coor= list(intersection.coords)
        #print(coor)
    elif type(intersection) == MultiLineString:
        coor= reduce(lambda x, y: x + y,[list(p.coords) for p in intersection])


    

    if coor != False and not insidePoly.contains(Point(coor[0])):

        point = Point(coor[0])
        if targetPoly.intersects(point.buffer(0.1)):
            iLandfallPoint['tyID']          = tyID
            iLandfallPoint['landfallPoint'] = coor[0]
            iLandfallPoint['allLats']       = lats
            iLandfallPoint['allLons']       = lons
            iLandfallPoint['allGrades']     = grades
            iLandfallPoint['allDate']       = date
            iLandfallPoint['allwind']       = wind
            iLandfallPoint['allpressure']   = pressure
            landfallPoints[str(num)]        = iLandfallPoint
            num += 1

#landfallPoints.keys()



# for循环遍历所有登陆台风并提取信息
# 新建空字典记录台风信息
tyLfInfo = {}
for num in landfallPoints.keys():
    iTy = landfallPoints[num]
    point = Point(iTy['landfallPoint'])
    x = iTy['allLons']
    y = iTy['allLats']
    intvl = 6 #台风数据间隔6h 
    
    # 找到登陆的那一段，提取台风登陆信息
    # 登陆角度，速度，强度，登陆时间
    # for循环遍历一个登陆台风的轨迹，找到登陆点所在的一段
    for i in range(len(x)-1):
        if LineString([(x[i], y[i]), (x[i+1], y[i+1])]).intersects(point.buffer(0.01)):
            lfDirect = np.arctan2(y[i] - y[i+1], x[i] - x[i+1]) * 180 / np.pi
            lfSpeed  = haversine((y[i], x[i]), (y[i+1], x[i+1])) / intvl
            lfGrade  = iTy['allGrades'][i]
            lfDate   = iTy['allDate'][i]
            lfPressure = iTy['allpressure'][i]
            break

    # 记录提取到的所有信息
    iTyLfInfo = {} # 子字典，记录一个登陆台风的信息
    iTyLfInfo['tyID']             = iTy['tyID'] 
    iTyLfInfo['landfallPoint']    = iTy['landfallPoint']
    iTyLfInfo['landfallDirction'] = lfDirect  
    iTyLfInfo['landfallSpeed']    = lfSpeed
    iTyLfInfo['landfallGrade']    = lfGrade
    iTyLfInfo['landfallDate']     = lfDate
    iTyLfInfo['landfallPressure']     = lfPressure
    iTyLfInfo['allLats']          = iTy['allLats']
    iTyLfInfo['allLons']          = iTy['allLons']
    iTyLfInfo['allGrades']        = iTy['allGrades']
    iTyLfInfo['allDate']          = iTy['allDate']
    tyLfInfo[num] = iTyLfInfo # 子字典添加到父字典

tyLfInfo['53']['landfallPoint']



##################ploting###################



minLat=5
maxLat=22
minLon=116
maxLon=127
figName='tyLandfallPoints.png'
points = []
grades = []


for i in tyLfInfo.keys():
    iTy    = tyLfInfo[i]
    iPoint = iTy['landfallPoint']
    iGrade = iTy['landfallGrade']
    #print(iPoint)
    #print(iGrade)
    points.append(iPoint)
    grades.append(iGrade) 
points = np.array(points)
grades = np.array(grades)
lons = points[:,0]
lats = points[:,1]
   
fig = plt.gcf()
plt.rcParams['savefig.dpi'] = 3000 #像素
plt.rcParams['figure.dpi'] = 3000 #分辨率
m = Basemap(llcrnrlon=minLon,llcrnrlat=minLat, \
            urcrnrlon=maxLon,urcrnrlat=maxLat, \
            resolution='h')
m.drawcoastlines(linewidth=0.3)

#m.drawrivers(linewidth=0.3)
phl_shp = r'D:\222\gadm36_PHL_shp\gadm36_PHL_1'


m.readshapefile(phl_shp,'phl',drawbounds=True)


legendIdx = {0:'Weak than TD',1:'TD(10.8-17.1m/s)',\
           2:'Tropical Depression',3:'Tropical Storm',\
           4:'Severe Tropical Storm',5:'Typhoon',\
           6:'Extra-tropical Cyclone',
           7:'Typhoon degeneration',
           9:'Tropical Cyclone of TS intensity or higher'
           }

colorIdx = {0:'grey',7:'brown',2:'blue', \
            3:'green',4:'red',5:'magenta',\
            6:'purple',9:'yellow'}

firstIdx = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 9:1}




handlesDict = {}
for i in range(len(grades)):
    iKey  = int(grades[i])
    first = firstIdx[iKey]
    if first != 1 :
        plt.scatter(lons[i],lats[i],s=10, marker="o",\
          color=colorIdx[iKey])
    else: 
        iHandle = {}
        iHandle.update({'iLon':lons[i]})
        iHandle.update({'iLat':lats[i]})
        iHandle.update({'iColor':colorIdx[iKey]})
        iHandle.update({'iLabel':legendIdx[iKey]})
        handlesDict.update({iKey:iHandle})
        firstIdx.update({iKey:0})
for i in range(10):
    if i in handlesDict.keys():
        iHandle = handlesDict[i]
        iLon    = iHandle['iLon']
        iLat    = iHandle['iLat']
        iColor  = iHandle['iColor']
        iLabel  = iHandle['iLabel']
        plt.scatter(iLon,iLat,color=iColor,\
            s=10, marker="o",label=iLabel)

plt.legend(loc='lower left',fontsize='x-small')
plt.title(r'$ 2009-2020$',fontsize=10)
plt.show()
#fig.savefig(figName)
plt.close()






minLat=0
maxLat=30
minLon=110
maxLon=135
figName='tyLandfallPoints.png'
points = []
grades = []


for i in tyLfInfo.keys():
    iTy    = tyLfInfo[i]
    iPoint = iTy['landfallPoint']
    iGrade = iTy['landfallGrade']
    #print(iPoint)
    #print(iGrade)
    points.append(iPoint)
    grades.append(iGrade) 
points = np.array(points)
grades = np.array(grades)
lons = points[:,0]
lats = points[:,1]
   
fig = plt.gcf()
plt.rcParams['savefig.dpi'] = 3000 #像素
plt.rcParams['figure.dpi'] = 3000 #分辨率
m = Basemap(llcrnrlon=minLon,llcrnrlat=minLat, \
            urcrnrlon=maxLon,urcrnrlat=maxLat, \
            resolution='h')
m.drawcoastlines(linewidth=0.3)

#m.drawrivers(linewidth=0.3)
phl_shp = r'D:\222\gadm36_PHL_shp\gadm36_PHL_1'


m.readshapefile(phl_shp,'phl',drawbounds=True)


legendIdx = {0:'Weak than TD',1:'TD(10.8-17.1m/s)',\
           2:'Tropical Depression',3:'Tropical Storm',\
           4:'Severe Tropical Storm',5:'Typhoon',\
           6:'Extra-tropical Cyclone',
           7:'Typhoon degeneration',
           9:'Tropical Cyclone of TS intensity or higher'
           }

colorIdx = {0:'grey',7:'brown',2:'blue', \
            3:'green',4:'red',5:'magenta',\
            6:'purple',9:'yellow'}

firstIdx = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 9:1}


handlesDict = {}
countGrade = {}  #统计各强度的次数
for i in range(len(grades)):
    iTy = tyLfInfo[str(i)]
    iKey  = int(grades[i])
    first = firstIdx[iKey]
    if first != 1 :
        iLons = iTy['allLons']
        iLats = iTy['allLats']
        plt.plot(iLons,iLats,color=colorIdx[iKey], \
                      linewidth=0.5,linestyle='-')
        countGrade[iKey] = countGrade[iKey] + 1
    else: 
        iHandle = {}
        iHandle.update({'iLons':iTy['allLons']})
        iHandle.update({'iLats':iTy['allLats']})
        iHandle.update({'iColor':colorIdx[iKey]})
        iHandle.update({'iLabel':legendIdx[iKey]})
        handlesDict.update({iKey:iHandle})
        firstIdx.update({iKey:0})
        countGrade[iKey] = 1
for i in range(10):
    if i in handlesDict.keys():
        iHandle = handlesDict[i]
        iLons   = iHandle['iLons']
        iLats   = iHandle['iLats']
        iColor  = iHandle['iColor']
        iLabel0 = iHandle['iLabel']
        iLabel1 = u' '+str(countGrade[i])+' times'
        iLabel  = iLabel0+iLabel1
        plt.plot(iLons,iLats,linewidth=0.5, \
            linestyle='-',color=iColor,label=iLabel)
plt.legend(loc='lower left',shadow=True,facecolor='white',frameon=True,fontsize=6)
plt.title(r'$ 2009-2020$',fontsize=10)
plt.show()
#fig.savefig(figName)
plt.close()







minLat=5
maxLat=22
minLon=116
maxLon=127
figName='tyLandfallPoints.png'
points = []
grades = []
pressures=[]


for i in tyLfInfo.keys():
    iTy    = tyLfInfo[i]
    iPoint = iTy['landfallPoint']
    iGrade = iTy['landfallGrade']
    iPressure = iTy['landfallPressure']
    #print(iPoint)
    #print(iGrade)
    points.append(iPoint)
    grades.append(iGrade)
    pressures.append(int(iPressure))
points = np.array(points)
grades = np.array(grades)
pressures_arrange=np.array(pressures)
max_=pressures_arrange.max()
min_=pressures_arrange.min()
meridians = np.linspace(min_-1,max_+1,5)
print(pressures)
print(meridians)

pressures_box1=[]
pressures_box2=[]
pressures_box3=[]
pressures_box4=[]




for i in pressures:
    if i >meridians[0] and i<meridians[1]:
        pressures_box1.append(i)
    elif i >meridians[1] and i<meridians[2]:
        pressures_box2.append(i)
    elif i >meridians[2] and i<meridians[3]:
        pressures_box3.append(i)
    elif i >meridians[3] and i<meridians[4]:
        pressures_box4.append(i)
        
lons = points[:,0]
lats = points[:,1]


   
fig = plt.gcf()
plt.rcParams['savefig.dpi'] = 3000 #像素
plt.rcParams['figure.dpi'] = 3000 #分辨率
m = Basemap(llcrnrlon=minLon,llcrnrlat=minLat, \
            urcrnrlon=maxLon,urcrnrlat=maxLat, \
            resolution='h')
m.drawcoastlines(linewidth=0.3)


phl_shp = r'D:\222\gadm36_PHL_shp\gadm36_PHL_1'


m.readshapefile(phl_shp,'phl',drawbounds=True)


legendIdx = {0:'Weak than TD',1:'TD(10.8-17.1m/s)',\
           2:'Tropical Depression',3:'Tropical Storm',\
           4:'Severe Tropical Storm',5:'Typhoon',\
           6:'Extra-tropical Cyclone',
           7:'Typhoon degeneration',
           9:'Tropical Cyclone of TS intensity or higher'
           }

colorIdx = {0:'grey',7:'brown',2:'blue', \
            3:'green',4:'red',5:'magenta',\
            6:'purple',9:'yellow'}

firstIdx = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 9:1}




handlesDict = {}
for i in range(len(grades)):
    iKey  = int(grades[i])
    first = firstIdx[iKey]
    if first != 1 :
        plt.scatter(lons[i],lats[i],s=10, marker="o",\
          color=colorIdx[iKey])
    else: 
        iHandle = {}
        iHandle.update({'iLon':lons[i]})
        iHandle.update({'iLat':lats[i]})
        iHandle.update({'iColor':colorIdx[iKey]})
        iHandle.update({'iLabel':legendIdx[iKey]})
        handlesDict.update({iKey:iHandle})
        firstIdx.update({iKey:0})
for i in range(10):
    if i in handlesDict.keys():
        iHandle = handlesDict[i]
        iLon    = iHandle['iLon']
        iLat    = iHandle['iLat']
        iColor  = iHandle['iColor']
        iLabel  = iHandle['iLabel']
        plt.scatter(iLon,iLat,color=iColor,\
            s=10, marker="o",label=iLabel)

plt.legend(loc='lower left',fontsize='x-small')
plt.show()
#fig.savefig(figName)
plt.close()






