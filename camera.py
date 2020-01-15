from picamera import PiCamera 
from time import sleep
#id1 = input("input your id card : ");
#id=str(id1)
camera = PiCamera()
camera.resolution=(800,600)
camera.rotation=90
camera.start_preview()
sleep(5)
camera.capture('/home/pi/new.jpg')
camera.stop_preview()
camera.close()
