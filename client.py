import socket, sys, os, pygame
from PIL import Image

import StringIO
import threading

from pygame.locals import *
import autopy
from autopy.mouse import CENTER_BUTTON
from autopy.mouse import RIGHT_BUTTON
from autopy.mouse import LEFT_BUTTON

import timeit
from time import sleep
import utils

HOST = '192.168.1.81'
PORT = 50007
exitFlag = False
key = 748264

def sendKeys(s, mouse):
	while exitFlag==False:
		data = mouse.getMouseValues(False)
		data = str(data)
		print "Sending ", data
		s.sendall(data)
		sleep(0.5)

threads = []

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	serverId = input("Enter the ID displayed at the server: ")
	encryptedId = serverId ^ key
	s.sendall(str(encryptedId))

	data = s.recv(1024)
	if(len(data)) == 0:
		print "Server Rejected Connection"
		s.close()
		exit()

	print "Server Accepted Connection"

	size = eval(data)
	print size

	target = size[0]*size[1]*3
	target+=20

	pygame.init()
	screen = pygame.display.set_mode(size)
	mouse = utils.MouseClass()

	exitFlag = False
	t = threading.Thread(target=sendKeys, args=(s,mouse,))
	t.daemon = True
	threads.append(t)
	t.start()

	start = timeit.default_timer()
	frames = 0.0

	while 1:
		if frames==5:
			end = timeit.default_timer()
			netTime = end - start
			fps = frames/netTime
			print "**************************** FPS: ",fps
			frames = 0
			start = timeit.default_timer()
		frames += 1
		
		data = s.recv(1024)
		if len(data) == 0:
			exitFlag=True
			break
		pre = data[:20]
		data = data[20:]
		li = pre.split(",")
		target = int(li[0])

		while len(data) != target:
			newData = s.recv(1024)
			if len(newData) == 0:
				break
			data += newData
		print "Length received = ", len(data)

		output = StringIO.StringIO(data)
		image = pygame.image.load(output)
		screen.blit(image,(0,0))
		pygame.display.flip()
		#sleep(0.2)
	s.close()
