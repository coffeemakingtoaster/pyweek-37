from config import TEAM_BITMASKS
from entities.base_enemy import Base_Enemy
from direct.actor.Actor import Actor

import uuid

from panda3d.core import CollisionEntry, CollisionNode,  CollisionBox, Point3, CollisionHandlerEvent


# This is used for testing, not for the actual game
class Sample_Enemy(Base_Enemy):
   def __init__(self, enemy_x, enemy_z) -> None:
      super().__init__()
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.model = Actor("assets/eggs/Player.egg",)
   
      # Set initial rotation
      self.model.setH(90)
        
      self.model.reparentTo(self.parentNode)

      self.parentNode.setPos(enemy_x, 0, enemy_z)

      self.hp = 15
      self.max_hp = 15

      self.attach_hp_bar_to_model()

      self.accept("u", self._update_hp, [-1])

      self.id = str(uuid.uuid4())

      self.collision = self.model.attachNewNode(CollisionNode("enemy"))

      self.collision.node().addSolid(CollisionBox(Point3(0,-1,0),(1,1,2)))

      self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.ENEMY)

      self.collision.setTag("id", self.id)

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into-%in")

      self.accept("player_light_attack-into", self._player_hit)

      base.cTrav.addCollider(self.collision, self.notifier)


   def _player_hit(self, entry: CollisionEntry):
      if entry.into_node.getTag("id") != self.id:
         return
      self._update_hp(-1)

   def _update_hp(self, value):
      self.hp += value
      self._update_hp_display()
