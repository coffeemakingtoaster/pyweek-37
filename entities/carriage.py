from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.core import TransparencyAttrib
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *

from helpers.constants import EVENT_NAMES

class Carriage(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.model = Actor("assets/anims/Carriage.egg",{
         'Close_Doors': 'assets/anims/Carriage-Close_Doors.egg','Open_Doors':'assets/anims/Carriage-Open_Doors.egg'
      })
        self.model.reparentTo(render)
        self.model.setPosHprScale(1,-1.5,-9, 90, 0, 0, 1, 1.5, 1)
        self.started = False
        self.goalX = 9999
        self.accept('arrived',self.arrived)
        self.open_doors_interval = self.model.actorInterval('Open_Doors')
        self.send_player_leave_signal_interval = Func(self.send_player_leave_signal)
        self.send_player_enter_signal_interval = Func(self.send_player_enter_signal)
        self.close_doors_interval = self.model.actorInterval('Close_Doors')
        
        self.send_station_leave_signal_interval = Func(self.send_station_leave_signal)
        self.leave_interval = Func(self.leave)
        self.arrive_interval = Func(self.arrive)
        self.spawn_boss_signal = Func(messenger.send,EVENT_NAMES.SPAWN_BOSS_EVENT)
        self.arrived_sequence = Sequence(self.open_doors_interval,Wait(1),self.send_player_leave_signal_interval,Wait(1),self.close_doors_interval,self.leave_interval, Wait(5), self.spawn_boss_signal)
        self.leave_sequence = Sequence(self.open_doors_interval,Wait(1),self.send_player_enter_signal_interval,Wait(1),self.close_doors_interval,Wait(1),self.send_station_leave_signal_interval)
        self.arriving = False
        self.leavingBool = False
    
    def send_player_leave_signal(self):
        messenger.send('arrived_open_leave')
        
    def send_player_enter_signal(self):
        messenger.send('arrived_open_enter')
        
    def send_station_leave_signal(self):
        messenger.send('station_leave')

     
    def arrived(self):
        self.arrived_sequence.start()
    
    def leaving(self):
        self.leave_sequence.start()
           
    def arrive(self):
        self.arriving = True
        self.model.setX(-100)
        self.started = True
        self.goalX = 1.5 
        
    def update(self,dt):       
        if self.started:
            self.model.setFluidX(self.model.getX() + WORLD_CONSTANTS.CARRIAGE_SPEED * dt)
            if self.model.getX() <= self.goalX+1 and self.model.getX() >= self.goalX-1:
                self.started = False
                if self.leavingBool:
                    self.leavingBool = False
                if self.arriving:
                    self.arriving = False
                    self.leaving()
    
    def leave(self):
        self.leavingBool = True
        print("Carriage Leaving")
        self.started = True
        self.goalX = 200
        
    def startEnemies(self):
        print("Starting Enemies")
    def stopEnemies(self):
        print("Stopping Enemies")
    
    def destroy(self):
        self.model.cleanup()
