import socket
import os
import sys
import struct
import Face_recognition as face
import numpy as np
import tensorflow as tf
import time




def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('192.168.1.2 ', 6667))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("Wait")
    i=0
    while True:
        time_end = time.time()
        print('num:',i)
        print('datetime:',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        print('******************************************')
        i=i+1
        sock, addr = s.accept()
        sock.settimeout(1)
        time_start=time.time()
        deal_data(sock, addr)
        time_end=time.time()
        print('time:',time_end-time_start)


    s.close()
def deal_data(sock, addr):
    print("Accept connection from {0}".format(addr))
    while True:
        time_start=time.time()
        fileinfo_size = struct.calcsize('128sl')
        try:
            buf = sock.recv(fileinfo_size)
        except:
            print('Time out!')
            sock.send(str(1).encode('utf-8'))
            sock.close()
            return

        if buf:
            # bufarr=bytearray(buf)
            # bufarr.append(0)
            # bufarr.append(0)
            # bufarr.append(0)
            # bufarr.append(0)


            if len(buf) > 131:
                filename, filesize = struct.unpack('128sl', buf)
                fn = filename.decode().strip('\x00')
                name = os.path.splitext(os.path.basename(fn))[0]
                new_filename = os.path.join('./images/' + name+'_new'+'.jpg')
                recvd_size = 0
                fp = open(new_filename, 'wb')
                while recvd_size < filesize:
                    try:
                        data = sock.recv(1024)
                    except:
                        print('Time out!')
                        sock.send(str(1).encode('utf-8'))
                        sock.close()
                        return

                    recvd_size += len(data)
                    fp.write(data)
                fp.close()
                time_end=time.time()
                print('Network time:',time_end-time_start)
                result = face.FaceAPI('./images/' + name+'_new'+'.jpg')
                # re=np.asscalar(np.int64(result))
                # res=str(re)
                # sock.send(res.encode('utf-8'))
                sock.send(str(result).encode('utf-8'))

        sock.close()
        break
if __name__ == '__main__':
    face.load_detection_model()
    face.load_recognition_model()
    socket_service()
