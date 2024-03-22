from direct.actor.Actor import Actor

from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from entities.base import Base_Entity
from os.path import join

import uuid

from panda3d.core import CollisionNode, CollisionBox, Point3, CollisionHandlerEvent

class Can(Base_Entity):
   def __init__(self, can_x, can_z, direction) -> None:
      super().__init__()

      self.model = Actor(join("assets", "eggs", "Fireball.egg"))
      
      self.model.setScale(0.3)
      self.id = str(uuid.uuid4())

      # TODO: Adjust y coord for the boss stage
      self.model.setPos(can_x, 4, can_z + 0.25)

      self.collision = self.model.attachNewNode(CollisionNode("fireball"))

      self.collision.node().addSolid(CollisionBox(Point3(-0.8,-0.8,-0.8),(0.8,0.8,0.8)))

      self.collision.setTag("id", self.id)

      #self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.PLAYER)

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into")

      self.accept(f"fireball-into", self._player_hit)
      
      self.currentY = 0

      base.cTrav.addCollider(self.collision, self.notifier)

      self.model.reparentTo(render)

      self.traveled_distance = 0

      self.direction = direction

      self.is_dead = False

   def _player_hit(self, _):
      self.is_dead = True

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

