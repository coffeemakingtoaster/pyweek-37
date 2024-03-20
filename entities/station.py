from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor

class Station(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.moving = False
        self.goalX = 120
        self.model = Actor("assets/eggs/Station.egg")
        self.model.setPosHprScale(60, 1,0, 90, 0, 0, 1, 1, 1)
        self.model.reparentTo(render)
           
        
    def startBoss(self):
        print("Start Boss")
    def stopBoss(self):
        print("Stop Boss")
    def arrive(self):
        self.moving = True
        self.goalX = 0
    def leave(self):
        self.moving = True
        self.goalX = -60
        
        
    def update(self,dt):
        if self.moving:
            
            self.model.setFluidX(self.model.getX() - WORLD_CONSTANTS.TUNNEL_SPEED * dt)
            if self.model.getX() <= self.goalX:
                self.moving = False
    
    def destroy(self):
        self.model.cleanup 