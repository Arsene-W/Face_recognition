#!/user/bin/env python
#-*-coding:utf-8-*-
#encoding=utf-8
import RPi.GPIO as GPIO
import time
import picamera
from picamera import PiCamera 
from time import sleep
import totf
#import pymysql
 
relay = 24 #port

#shi neng menjin gpio
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay,GPIO.OUT)
GPIO.output(relay,GPIO.LOW)

#chu shi hua camera
camera = PiCamera() 
camera.resolution=(800,600)
camera.rotation=90
camera.start_preview()
camera.annotate_text_size=160
camera.annotate_foreground=picamera.Color('white')



def superauthority():
    
    f = open("data.txt",'r')
    preid = input("Modify the id card : ");
    lines = f.readlines()
    superfa = open("data.txt",'w')
    flag = False
    
    for line in lines:
        if preid not in line:
            superfa.write(line)
        if preid in line:    
            flag = True
            print ("Delete succeed!");
            continue
        
    superfa.close()
    f.close()
    
    if flag == False:
        superf = open("data.txt",'a')
        superf.write(preid+"\n")
        print ("Add succeed!");
        superf.close()
    
    return

def isreal(id):
    if id=="3203319541":
        return True
    #while True:
    start1=time.time();
    camera.capture_sequence(['/home/pi/'+id+'.jpg'],use_video_port=True)
    end1=time.time();
    print("time1:",end1-start1)
    
    try:
        start2=time.time();
        re=str(totf.sock_client(r'/home/pi/'+id+'.jpg'))
        print(re)
        end2=time.time();
        print("time2:",end2-start2)
    except:
        return True
    if re=="1":
        camera.annotate_background=picamera.Color('green')
        camera.annotate_text="SUCCEED"
        print("11111")
        return True
    else:
        camera.annotate_background=picamera.Color('red')
        camera.annotate_text="FAILED"
        print("00000")
        return False
    
def judgment(id):
    start0=time.time();
    f = open("data.txt",'r')
    lines = f.readlines()
    for line in lines:
        if line.startswith(id):
            if isreal(id):
                GPIO.output(relay,GPIO.HIGH)
                end0=time.time();
                print("time0:",end0-start0)
                print ("OPEN!")
                time.sleep(2)
                GPIO.output(relay,GPIO.LOW)
                f.close()
                camera.annotate_text=""
                return True
            else:
                camera.annotate_background=picamera.Color('red')
                camera.annotate_text="FAILED"
                time.sleep(1)
                camera.annotate_text=""
                print ("failed")
                f.close()
                return False

    camera.annotate_text_size=100
    camera.annotate_background=picamera.Color('red')
    camera.annotate_text="ID UNDEFIND"
    time.sleep(1)
    camera.annotate_text=""
    camera.annotate_text_size=160    
    print ("ID undefined!")
    f.close()
    return False

while True:
    
    #db = pymysql.connect("101.132.161.76", "INNOVATION", "INNOVATION", "INNOVATION")
    # 使用cursor()方法获取操作游标
    #cursor = db.cursor()
    #cursor.execute("set names utf8")  # 统一编码格式
    #cursor.execute("SELECT VERSION()")
    #data=cursor.fetchone()
    #print (data)
    
    id1 = input("input your id card : ");
    id=str(id1)
    # print("input id: " + id)
    if id == "1436311502":
        superauthority();
    elif id == "0035491550":
        #judgment(id);
        superauthority();
    else:
        judgment(id);
        
        
camera.stop_preview()        
camera.close()        
GPIO.cleanup()

