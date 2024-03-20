from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor

class Map(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.model = Actor("assets/eggs/Map.egg")
        self.model.setPosHprScale(60, 1,0, 90, 0, 0, 1, 1, 1)
        self.model.reparentTo(render)
        self.enteringStation = False
        self.leavingStation = False
        self.moving = True
        self.accept('station_leave',self.leaveStation)
        
        
    
    def update(self, dt):
        if self.moving:    
            self.model.setFluidX(self.model.getX() - WORLD_CONSTANTS.TUNNEL_SPEED * dt)
            if self.model.getX() < -180 and not (self.enteringStation or self.leavingStation) :
                self.model.setX(60)
            elif self.model.getX() < -220 and not self.leavingStation:
                self.moving = False
                self.enteringStation = False
                print("Arrived")
                messenger.send('arrived')
            elif self.model.getX() < -250:
                self.leavingStation = False
                self.model.setX(60)
    
    def enterStation(self):
        self.enteringStation = True
    
    def leaveStation(self):
        self.leavingStation = True
        self.moving = True