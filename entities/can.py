from direct.actor.Actor import Actor

from config import ENTITY_CONSTANTS, WORLD_CONSTANTS
from entities.base import Base_Entity
from os.path import join

class Can(Base_Entity):
   def __init__(self, can_x, can_z, direction) -> None:
      super().__init__()

      self.model = Actor(join("assets", "eggs", "Player.egg"))
      
      # TODO: Adjust y coord for the boss stage
      self.model.setPos(can_x, 4, can_z)

      self.model.reparentTo(render)

      self.traveled_distance = 0

      self.direction = direction

      self.is_dead = False

   def update(self, dt):

      x_movement = ENTITY_CONSTANTS.CAN_SPEED * dt

      self.traveled_distance += x_movement

      self.model.setFluidX(max(min(self.model.getX() + (x_movement * self.direction), WORLD_CONSTANTS.MAP_X_LIMIT),-WORLD_CONSTANTS.MAP_X_LIMIT))

      if abs(self.model.getX()) >= WORLD_CONSTANTS.MAP_X_LIMIT or self.traveled_distance >= ENTITY_CONSTANTS.CAN_RANGE:
         self.is_dead = True

      # TODO: Adjust the rotation speed. 1 is likely to not be accurate
      self.model.setP(self.model.getP() + (360 * dt))

   def destroy(self):
      self.model.cleanup()
      self.model.removeNode()

