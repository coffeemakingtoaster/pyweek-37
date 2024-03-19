from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from panda3d.core import *
from direct.actor.Actor import Actor

class Tunnel(Base_Entity):
    def __init__(self):
        super().__init__()
        
        self.segments = []
        
        model1 = Actor("assets/eggs/tunnel.egg")
        model1.setPosHprScale(1,3,1, 90, 0, 0, 1, 1, 1)
        model1.reparentTo(render)
        
        self.segments.append(model1)
        
        model2 = Actor("assets/eggs/tunnel.egg")
        model2.setPosHprScale(28,3,1, 90, 0, 0, 1, 1, 1)
        model2.reparentTo(render)
        
        self.segments.append(model2)
        
        
    def update(self, dt):
        for model in self.segments:
            model.setFluidX(model.getX() - WORLD_CONSTANTS.TUNNEL_SPEED * dt)
            if model.getX() < -28:
                model.setX(28)
    
    
    def destroy(self):
        for model in self.models:
            model.cleanup()