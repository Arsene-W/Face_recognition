import socket
import os
import sys
import struct


def sock_client(filepath):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(('192.168.1.2', 6667))
    except socket.error as msg:
        print(msg)
        print(sys.exit(1))

    while True:
        #filepath = input('input the file: ')
        
        fhead = struct.pack(b'128sq', bytes(os.path.basename(filepath), encoding='utf-8'), os.stat(filepath).st_size)
        s.send(fhead)

        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                result = s.recv(8096)
                re=bytes.decode(result)
                print(re)
                break
            s.send(data)
        s.close()
        break
        print(re)
    return re;


if __name__ == '__main__':
    sock_client(r'/home/pi/image.jpg')
