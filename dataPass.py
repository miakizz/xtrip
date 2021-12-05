import serial
import time
import socket

ser = serial.Serial('/dev/ttyACM0', timeout=0)
time.sleep(0.25)
ser.write(b"ATA\r")
while True:
    if ser.read() == b"0":
        break

sock = socket.socket()
sock.connect(("16bit.retrocomputing.network", 56969))
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.setblocking(False)
while True:
    try:
        if sock.recv(1024):
            sock.send(b"///////PI-wyatt\r")
            break
    except:
        pass

while True:
    try:
        sockData = sock.recv(1024)
        if sockData:
            ser.write(sockData)
    except:
        pass		
    serData = ser.read(1024)
    if serData:
        sock.send(serData)
