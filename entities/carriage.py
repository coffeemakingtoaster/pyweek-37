from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.core import TransparencyAttrib


class Carriage(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.segments = []
        self.started = False
        
        model1 = Actor("assets/eggs/Carriage.egg")
        model1.setPosHprScale(0,0,-7.5, 90, 0, 0, 1, 1, 1)
        model1.reparentTo(render)
       
        self.segments.append(model1)
        
        model2 = Actor("assets/eggs/Carriage.egg")
        model2.setPosHprScale(16.4,0,-7.5, 90, 0, 0, 1, 1, 1)
        model2.reparentTo(render)
        
        self.segments.append(model2)
        
        model3 = Actor("assets/eggs/Carriage.egg")
        model3.setPosHprScale(-16.4,0,-7.5, 90, 0, 0, 1, 1, 1)
        model3.reparentTo(render)
        
        self.segments.append(model3)
        
    def arrive(self):
        
        for model in self.segments:
            model.setX(model.getX()-40)
            
        self.started = True
        
    def update(self,dt):       
        if self.started:
            for model in self.segments:
                model.setFluidX(model.getX() + WORLD_CONSTANTS.CARRIAGE_SPEED * dt)
                if model.getX() >= 16.4:
                    self.started = False
    
    def leave(self):
        print("Leaving")
    def startEnemies(self):
        print("Starting Enemies")
    def stopEnemies(self):
        print("Stopping Enemies")
    
    def destroy(self):
        for model in self.models:
            model.cleanup()