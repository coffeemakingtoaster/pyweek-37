from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from entities.base_enemy import Base_Enemy
from direct.actor.Actor import Actor

import uuid

from panda3d.core import CollisionEntry, CollisionNode,  CollisionBox, Point3, CollisionHandlerEvent

from entities.player import Player
from helpers.constants import ENEMY_ATTACK_NAMES, PLAYER_ATTACK_NAMES

from time import time

class Football_Fan(Base_Enemy):
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

      self.notifier.addInPattern("%fn-into")

      self.accept(f"enemy-into", self._player_hit)

      base.cTrav.addCollider(self.collision, self.notifier)

      self.is_in_attack = False

      self.last_attack_time = 0

      self.attack_hitbox = None

   def update(self, dt, player_pos):
      if self.is_dead:
         return
      
      x_movement = 0
      if not self.is_in_attack:
         x_diff_to_player = self.parentNode.getX() - player_pos.getX()

         if abs(x_diff_to_player) < ENTITY_CONSTANTS.FOOTBALL_FAN_ATTACK_RANGE:
            self._attack()

         x_movement = ENTITY_CONSTANTS.FOOTBALL_FAN_MOVEMENT_SPEED * dt 

         if  x_diff_to_player < x_movement:
            # prevent -inf exception
            x_movement = max(x_diff_to_player, 0.3)
         
         # Stop moving once close to avoid glitching in player
         if abs(x_diff_to_player) < (ENTITY_CONSTANTS.FOOTBALL_FAN_ATTACK_RANGE / 2):
            x_movement = 0

         if x_diff_to_player < 0: 
            self.model.setH(90)
         elif x_diff_to_player > 0:
            self.model.setH(-90)
            x_movement *= -1

      new_z = 0

      # gravity
      if self.parentNode.getZ() > 0.1  or self.z_velocity > 0:
         self.z_velocity = max(self.z_velocity - WORLD_CONSTANTS.GRAVITY_VELOCITY, -ENTITY_CONSTANTS.ENEMY_MAX_FALL_SPEED) 
         new_z = self.parentNode.getZ() + (self.z_velocity * dt)
         x_movement = 0
      
      new_x = self.parentNode.getX() + x_movement
      
      self.parentNode.setFluidPos(new_x, 0, new_z)

      #print(f"{self.parentNode.getX()}")

   def _attack(self):
      # Enemy cannot attack midair and when last attack was recently
      if time() - self.last_attack_time < ENTITY_CONSTANTS.FOOTBALL_FAN_ATTACK_CD or self.parentNode.getZ() > 0.1:
         return
      self.is_in_attack = True
      self.attack_hitbox = self.model.attachNewNode(CollisionNode(ENEMY_ATTACK_NAMES.FOOTBALL_FAN_ATTACK))
      self.attack_hitbox.show()
      self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-1,2),1,1,1))
      self.attack_hitbox.setTag("team", "enemy")
      self.attack_hitbox.setPos(0,0,-1)
      self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.PLAYER)
      base.cTrav.addCollider(self.attack_hitbox, self.notifier)
      base.taskMgr.doMethodLater(ENTITY_CONSTANTS.FOOTBALL_FAN_ATTACK_DURATION, self._destroy_attack_hitbox,f"destroy_{ENEMY_ATTACK_NAMES.FOOTBALL_FAN_ATTACK}_hitbox")
      self.last_attack_time = time()

   def _destroy_attack_hitbox(self, _):
      if self.attack_hitbox:
         self.attack_hitbox.removeNode()
         self.attack_hitbox = None
      self.is_in_attack = False

   def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id:
         return
      attack_identifier = entry.into_node.getName()

      self._destroy_attack_hitbox(None)
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
