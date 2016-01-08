#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Ice
import math
Ice.loadSlice('Drobots.ice')
import drobots 
from collections import namedtuple
MOVE=0
SCAN=1
ATTACK=2
class Client(Ice.Application): 
    def run(self, argv):
	broker = self.communicator()
	######################################################
	adapter = broker.createObjectAdapter("Adapter")
	servant = PlayerI(broker,adapter)
	proxy_player = adapter.add(servant, broker.stringToIdentity("player1"))
	print(proxy_player)
	adapter.activate()
	sys.stdout.flush()
	######################################################
	player = drobots.PlayerPrx.checkedCast(proxy_player)
	adapter.activate() #activar el adaptador
	######################################################
        proxy_game = self.communicator().stringToProxy(argv[1])
	print(proxy_game)
        game = drobots.GamePrx.checkedCast(proxy_game)
        if not game:
            raise RuntimeError('Invalid proxy')
	######################################################
	game.login(player,"Diego");
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

class PlayerI(drobots.Player):
    def __init__(self,broker,adapter,current=None): 
	print "jugador creado"
	self.broker=broker
	self.adapter=adapter
    def makeController(self,bot,current=None):
	print "makeController called"
	servant=RobotControllerI(bot)
	proxy_controller = self.adapter.add(servant, self.broker.stringToIdentity("controller1"))
	controller = drobots.RobotControllerPrx.checkedCast(proxy_controller)
	print(proxy_controller)
	return controller

    def win(self,current=None): 
	print("Win")
	sys.exit(0)
    def lose(self,current=None):
	print("Lose")
	sys.exit(0)
    def gameAbort(self,current=None):
        print("Game Aborted")
        sys.exit(0)

class RobotControllerI(drobots.RobotController):
    def __init__(self,bot):
        print "controler creado"
        self._bot=bot
	self._x=MOVE
	self._botDetected=0
	self._angleScan=0
	self._wide=20
	self._landmark_x=500
	self._landmark_y=500
	self._counter=0
	self._turn=0
	self._distanceMisil=40
    def turn(self,current=None):
        print "siguiente turno"
	self._turn=self._turn+1
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#-----------------------------------ESTADO MOVE----------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	if(self._x==MOVE):
		print "ESTOY MOVIENDOME"
		if(self._turn <= 10): #SE MUEVE DURANTE 'X' TURNOS
			coordenates=self._bot.location()
			angle=calculateAngle(coordenates.x,self._landmark_x,coordenates.y,self._landmark_y)
			print(coordenates)
			velocity=calculateVelocity(coordenates.x,coordenates.y,self._landmark_x,self._landmark_y)
			print(velocity)
			self._bot.drive(int(angle),int(velocity))
		else:
			self._x=SCAN

	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#-----------------------------------ESTADO SCAN----------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	elif(self._x==SCAN):
		print "ESTOY ESCANEADO"
		if(self._angleScan < 359): ##SI AUN ESTA ESCANEADO 360 GRADOS
			self._botDetected=self._bot.scan(int(self._angleScan),int(self._wide))
			print(self._botDetected)
			if(self._botDetected > 0): #SI DETECTA A UN BOT
				self._wide=self._wide/2
				self._counter=self._counter+1
				
			else: #SI NO DETECTA A NINGUN ROBOT
				self._angleScan=self._angleScan+self._wide
			if(self._counter==3): #SI YA HA DETECTADO A UNO O VARIOS ROBOTS 'COUNTER' VECES
				self._x=ATTACK 
				self._counter=0
				self._turn=0
		else: ##SI NO HA ENCONTRADO NADA
			self._x=MOVE #CAMBIO A ESTADO MOVE
			self._angleScan=0
			self._wide=20

	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#-----------------------------------ESTADO ATTACK--------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	elif(self._x==ATTACK):
		print "ESTOY ATACANDO"
		if(self._turn <= 20): #ATACA DURANTE 'X' TURNOS
			self._bot.cannon(int(self._angleScan),int(self._distanceMisil))
			self._distanceMisil=self._distanceMisil+35
		else:
			self._x=MOVE
			self._turn=0
			self._angleScan=0
			self._wide=20
			self._distanceMisil=40


    def robotDestroyed(self,current=None): 
        print("Robot Destruido")

def calculateAngle(x1,x2,y1,y2):
    x=x2-x1
    y=y2-y1
    if(x == 0):
        x=1
    if((x<0 and y>0) or (x<0 and y<0)):
        angle=180
    elif(x>0 and y<0):
        angle=360
    else:
        angle=0
    return (math.degrees(math.atan(float(y)/float(x)))+angle)

def calculateVelocity(x,y,position_x,position_y):
	if( ((x < position_x+10) and (x > position_x-10)) and ((y < position_y+10) and (y >position_y-10))):
		return 20
	else:		
		return 100

sys.exit(Client().main(sys.argv))













