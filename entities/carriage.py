from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.core import TransparencyAttrib


class Carriage(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.model = Actor("assets/anims/Carriage.egg",{
         'Close_Doors': 'assets/anims/Carriage-Close_Doors.egg','Open_Doors':'assets/anims/Carriage-Open_Doors.egg'
      })
        self.model.setPosHprScale(0,-1.5,-9, 90, 0, 0, 1, 1.5, 1)
        self.model.reparentTo(render)
        self.started = False
        self.goalX = 9999
        
        
        
        
    def arrive(self):
        self.model.setX(-100)
        self.started = True
        self.goalX = 0
        
    def update(self,dt):       
        if self.started:
            self.model.setFluidX(self.model.getX() + WORLD_CONSTANTS.CARRIAGE_SPEED * dt)
            if self.model.getX() <= self.goalX+1 and self.model.getX() >= self.goalX-1:
                self.started = False
    
    def leave(self):
        print("Carriage Leaving")
        self.started = True
        self.goalX = 200
    def startEnemies(self):
        print("Starting Enemies")
    def stopEnemies(self):
        print("Stopping Enemies")
    
    def destroy(self):
        self.model.cleanup()