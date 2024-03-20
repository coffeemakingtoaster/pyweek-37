from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from entities.base_enemy import Base_Enemy
from direct.actor.Actor import Actor

import uuid

from panda3d.core import CollisionEntry, CollisionNode,  CollisionBox, Point3, CollisionHandlerEvent

from entities.player import Player
from helpers.constants import PLAYER_ATTACK_NAMES

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

      self.z_velocity = 0

      self.hp = 15
      self.max_hp = 15

      self.attach_hp_bar_to_model()

      self.id = str(uuid.uuid4())

      self.collision = self.model.attachNewNode(CollisionNode("enemy"))

      self.collision.node().addSolid(CollisionBox(Point3(0,-1,0),(1,1,2)))

      self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.ENEMY)

      self.collision.setTag("id", self.id)

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into-%in")

      self.accept(f"enemy-into-{PLAYER_ATTACK_NAMES.LIGHT_ATTACK}", self._player_hit)

      self.accept(f"enemy-into-{PLAYER_ATTACK_NAMES.DASH_ATTACK}", self._player_hit)

      self.accept(f"enemy-into-{PLAYER_ATTACK_NAMES.HEAVY_ATTACK}", self._player_hit)

      base.cTrav.addCollider(self.collision, self.notifier)

   def update(self, dt, player_pos):
      if self.is_dead:
         return
      x_diff_to_player = self.parentNode.getX() - player_pos.getX()
      if x_diff_to_player < 0: 
         self.model.setH(90)
      elif x_diff_to_player > 0:
         self.model.setH(-90)

      new_z = 0

      # gravity
      if self.parentNode.getZ() > 0.1  or self.z_velocity > 0:
         self.z_velocity = max(self.z_velocity - WORLD_CONSTANTS.GRAVITY_VELOCITY, -ENTITY_CONSTANTS.ENEMY_MAX_FALL_SPEED) 
         new_z = self.parentNode.getZ() + (self.z_velocity * dt)
      
      self.parentNode.setFluidPos(self.parentNode.getX(), 0, new_z)

   def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id:
         return
      attack_identifier = entry.into_node.getName()
      if attack_identifier in [PLAYER_ATTACK_NAMES.HEAVY_ATTACK, PLAYER_ATTACK_NAMES.DASH_ATTACK]:
         if self.model.getZ() > 0.1:
            # Stop the fall
            self.z_velocity = 0
         else:
            if attack_identifier == PLAYER_ATTACK_NAMES.HEAVY_ATTACK:
               self.z_velocity = ENTITY_CONSTANTS.PLAYER_HEAVY_ATTACK_KNOCKUP
            else:
               self.z_velocity = ENTITY_CONSTANTS.PLAYER_DASH_KNOCKUP
      self._update_hp(-1)
