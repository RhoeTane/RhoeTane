# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 10:19:34 2021

@author: yrtst
"""




from queue import Queue
from threading import Thread
import cdsapi
from time import time
import datetime
import os

def downloadonefile(riqi):
    ts = time()
    filename="/Volumes/DATA1/ERADATA/mslp."+riqi+".nc"
    if(os.path.isfile(filename)): #如果存在文件名则返回
      print("ok",filename)
    else:
      print(filename)
      c = cdsapi.Client()
      c.retrieve(
          'reanalysis-era5-pressure-levels',
          {
              
              'year'         : riqi[0:4],
              'month'        : riqi[-4:-2],
              'day'          : riqi[-2:],
              'product_type':'reanalysis',
              # 'variable':[
              #     'divergence','fraction_of_cloud_cover','geopotential',
              #     'ozone_mass_mixing_ratio','potential_vorticity'
              #,'relative_humidity',
              #     'specific_cloud_ice_water_content',
              #'specific_cloud_liquid_water_content','specific_humidity',
              #     'specific_rain_water_content',
              #'specific_snow_water_content','temperature',
              #     'u_component_of_wind','v_component_of_wind',
              #'vertical_velocity',
              #     'vorticity'
              # ],
              'variable':[
                  'divergence','geopotential',
                   'potential_vorticity','relative_humidity',
                   'specific_humidity',
                   'temperature',
                   'u_component_of_wind','v_component_of_wind',
                   'vertical_velocity',
                   'vorticity'
              ],
              # 'pressure_level':[
              #     '250','300','350',
              #     '400','450','500',
              #     '550','600','650',
              #     '700','750','775',
              #     '800','825','850',
              #     '875','900','925',
              #     '950','975','1000'
              # ],
              'pressure_level':[
              #'250','300','350',
              #     '400','450','500',
              #     '550','600','650',
              #     '700','750','775',
              #     '800','825','850',
              #     '875','900','925',
              #     '950','975',
                   '1000'
               
              ],
              
              'time':[
                  '00:00','01:00','02:00',
                  '03:00','04:00','05:00',
                  '06:00','07:00','08:00',
                  '09:00','10:00','11:00',
                  '12:00','13:00','14:00',
                  '15:00','16:00','17:00',
                  '18:00','19:00','20:00',
                  '21:00','22:00','23:00'
              ],
              'area':'0/110/50/180', ## North, West, South, East. Default: global
              'grid': '0.25/0.25',
              'format':'netcdf'
            
          },
          filename)


    
#下载脚本 
class DownloadWorker(Thread):
   def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue
 
   def run(self):
       while True:
           # 从队列中获取任务并扩展tuple
           riqi = self.queue.get()
           downloadonefile(riqi)
           self.queue.task_done()

#主程序 
def main():
   #起始时间
   ts = time()

   #起始日期
   begin = datetime.date(2021,9,9)  
   end = datetime.date(2021,9,10)
   d=begin
   delta = datetime.timedelta(days=1)
   
   #建立下载日期序列
   links = []
   while d <= end:
       riqi=d.strftime("%Y%m%d")
       links.append(str(riqi))
       d += delta

   #创建一个主进程与工作进程通信
   queue = Queue()

   # 20191119更新# 新的请求规则 https://cds.climate.copernicus.eu/live/limits
   # 注意，每个用户同时最多接受4个request https://cds.climate.copernicus.eu/vision
   #创建四个工作线程
   for x in range(4):
       worker = DownloadWorker(queue)
       #将daemon设置为True将会使主线程退出，即使所有worker都阻塞了
       worker.daemon = True
       worker.start()
       
   #将任务以tuple的形式放入队列中
   for link in links:
       queue.put((link))

   #让主线程等待队列完成所有的任务
   queue.join()
   print('Took {}'.format(time() - ts))

if __name__ == '__main__':
   main()

















































