import subprocess
import re
import os
import time
import socket
import serial
import time
import ipaddress
import board
import digitalio

xband_numbers = ['19209492263', '18002071194', '0355703001', '0120717360']
peerAddr = ipaddress.ip_address("123.123.123.123")
ring = False

FR = digitalio.DigitalInOut(board.D17)
FR.direction = digitalio.Direction.OUTPUT

RingMode = digitalio.DigitalInOut(board.D27)
RingMode.direction = digitalio.Direction.OUTPUT

Hook = digitalio.DigitalInOut(board.D22)
Hook.direction = digitalio.Direction.INPUT

dtmf = subprocess.Popen(['multimon-ng','-aDTMF'],stdout=subprocess.PIPE)
#dialTone = subprocess.Popen(['mpv', '--loop', '-ao=jack', '/home/pi/longdial.wav'])
dialTone = subprocess.Popen(['mpv', '--loop', '--audio-device=alsa/sysdefault:CARD=Set', '/home/pi/longdial.wav'])
ser = serial.Serial('/dev/ttyACM0', timeout=0)

if ring:
	jackTrip = subprocess.Popen(['jacktrip', '-s', '-n', '1', '--bufstrategy', '-1',  '--udprt'], stdout=subprocess.PIPE)

num = ""
while True:
	print("Listening for Initial Dial")
	line = dtmf.stdout.readline().decode("UTF-8")
	if not line:
		break
	if re.match(r"DTMF: [0-9*#]\n", line):
		num += line[6]
	if len(num) >= 11 or num in xband_numbers:
		print('Dialed: ' + num)
		break

dtmf.terminate()
dialTone.terminate()

if num in xband_numbers:
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
		if sock.fileno() == -1:
			print("Socket Closed")
			break
		if not ser.cd:
			print("Modem Hung Up")
			break
	if ring:
		print("Waiting for Jacktrip Client")
		while True:
			line = jackTrip.stdout.readline().decode("UTF-8")
			if not line:
				break
			if "Received Connection from Peer" in line:
				break
		print("Connection received, ringing line")
		while True:
			RingMode.value = True
			for i in range(0,25):
				FR.value = True
				time.sleep(1/50)
				FR.value = False
				time.sleep(1/50)
				if Hook.value == True:
					RingMode.value = False
					print('Off Hook')
					break
			else:
				RingMode.value = False
				time.sleep(3)
				if not Hook.value:
					continue
			break
		print("XBAND picked up, let the games begin")
		while True:
			line = jackTrip.stdout.readline().decode("UTF-8")
			if not line:
				break
			if "Stopping JackTrip" in line:
				break
		print("Jacktrip Lost Connection, looping")
	
else:
	#peerAddr = ipaddress.ip_address(int(num[1:]))
	
	jackTrip = subprocess.Popen(['jacktrip', '-c', str(peerAddr), '-n', '1', '--bufstrategy', '-1',  '--udprt'], stdout=subprocess.PIPE)
	while True:
		line = jackTrip.stdout.readline().decode("UTF-8")
		if not line:
			break
		print(line)
		if "Stopping JackTrip" in line:
				break
