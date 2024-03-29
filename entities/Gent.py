from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from entities.base_enemy import Base_Enemy
from direct.actor.Actor import Actor

from panda3d.core import CollisionNode,  CollisionBox, Point3

from helpers.constants import ENEMY_ATTACK_NAMES

import random
from time import time

class Gent(Base_Enemy):
   def __init__(self, enemy_x, enemy_z) -> None:
      super().__init__()
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self._load_model() 
      # Set initial rotation
      self.model.setH(90)
        
      self.model.reparentTo(self.parentNode)

      self.parentNode.setPos(enemy_x, 0, enemy_z)

      self.z_velocity = 0

      self.hp = ENTITY_CONSTANTS.GENT_HP
      self.max_hp = ENTITY_CONSTANTS.GENT_HP

      self.attach_hp_bar_to_model(x_offset=-0.5, z_offset=2)
      self.add_collision_node()

      self.collision.node().addSolid(CollisionBox(Point3(0,-0.5,0),(1,0.5,2)))

      self.attack_range = ENTITY_CONSTANTS.GENT_ATTACK_RANGE

      self.movement_speed = ENTITY_CONSTANTS.GENT_MOVEMENT_SPEED + random.uniform(-1,1)

      self.death_animation_duration = 0.5

   def _load_model(self):
      self.model = Actor("assets/anims/Gent.egg",{
         "Light-Punch": "assets/anims/Gent-Light Punch.egg",
         "Dead": "assets/anims/Gent-Dead.egg",
         "Idle": "assets/anims/Gent-Idle.egg",
         "Knockup": "assets/anims/Gent-Knockup.egg",
         "Walk": "assets/anims/Gent-Walk.egg",
         "Flinch": "assets/anims/Gent-Flinch.egg",
         "Cylinder": "assets/anims/Gent-CylinderAction.egg",
         "Kick": "assets/anims/Gent-Kick.egg",
      })

      self.attacks = {
         "Light-Punch":{
               "windup": 0.1,
               "duration": 0.1,
               "hitbox": CollisionBox(Point3(0,-0.3,2),1,0.2,1),
         },
         "Kick":{
                  "windup": 0.5,
                  "duration": 0.3,
                  "hitbox":  CollisionBox(Point3(0,-0.,1),1,0.4,1),
               }
      }

      self.model.loop("Idle")

   def update(self, dt, player_pos,frontMan):
      if self._is_dead:
         return

      x_movement = 0
      if not self.is_in_attack:
         x_diff_to_player = self.parentNode.getX() - player_pos.getX()

         if abs(x_diff_to_player) < self.attack_range:
            self._attack()

         x_movement = self.movement_speed * dt

         if  abs(x_diff_to_player) < x_movement:
            # prevent -inf exception
            x_movement = max(x_diff_to_player, x_movement / 10)
         
         # Stop moving once close to avoid glitching in player
         if abs(x_diff_to_player) < (self.attack_range / 2):
            x_movement = 0
         
         if self.parentNode.getZ() < 0.1:
            if x_diff_to_player < 0: 
               self.model.setH(90)
            elif x_diff_to_player > 0:
               self.model.setH(-90)
               x_movement *= -1

      new_z = 0

      # gravity
      if self.parentNode.getZ() > 0.1  or self.z_velocity > 0:
         base.taskMgr.remove("spawn_gent_attack_hitbox")
         self.z_velocity = max(self.z_velocity - (WORLD_CONSTANTS.GRAVITY_VELOCITY * WORLD_CONSTANTS.ENEMY_GRAVITY_MODIFIER), -ENTITY_CONSTANTS.ENEMY_MAX_FALL_SPEED) 
         new_z = min(self.parentNode.getZ() + (self.z_velocity * dt), WORLD_CONSTANTS.MAP_HEIGHT)
         x_movement = self.knockback_velocity * dt
         self.is_in_attack = False

     # Animation handling
      current_animation = self.model.getCurrentAnim() 
      if abs(x_movement) > 0 and current_animation != "Walk" and current_animation != "Knockup":
         self.model.loop("Walk")
      elif (x_movement == 0 or self.parentNode.getZ() > 0.1) and current_animation == "Walk" and current_animation != "Knockup":
         self.model.loop("Idle")
      
      new_x = max(min(self.parentNode.getX() + x_movement, WORLD_CONSTANTS.MAP_X_LIMIT), -WORLD_CONSTANTS.MAP_X_LIMIT)
      
      if frontMan == None or frontMan.parentNode.is_empty():
         self.parentNode.setFluidPos(new_x, 0, new_z)
      elif abs(frontMan.parentNode.getX()-self.parentNode.getX())>1:
         self.parentNode.setFluidPos(new_x, 0, new_z)

   def _attack(self):
      # Enemy cannot attack midair and when last attack was recently
      if time() - self.last_attack_time < ENTITY_CONSTANTS.GENT_ATTACK_CD or self.parentNode.getZ() > 0.1:
         return
      attack = random.choice(list(self.attacks.keys()))

      self.model.play(attack)
      self.is_in_attack = True
      base.taskMgr.doMethodLater(self.attacks[attack]["windup"], self._spawn_attack_hitbox,f"spawn_gent_attack_hitbox", [attack])

   def _spawn_attack_hitbox(self, attack):
      self.attack_hitbox = self.model.attachNewNode(CollisionNode("Gent attack"))
      #self.attack_hitbox.show()
      self.attack_hitbox.node().addSolid(self.attacks[attack]["hitbox"])
      self.attack_hitbox.setTag("team", "enemy")
      self.attack_hitbox.setPos(0,0,-1)
      self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.PLAYER)
      base.cTrav.addCollider(self.attack_hitbox, self.notifier)
      base.taskMgr.doMethodLater(self.attacks[attack]["duration"], self._destroy_attack_hitbox,f"destroy_gent_attack_hitbox")
      self.last_attack_time = time()

