from entities.base_enemy import Base_Enemy

from direct.actor.Actor import Actor

from os.path import join

from panda3d.core import CollisionBox, Point3, CollisionEntry, CollisionNode

from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from helpers.constants import ENEMY_ATTACK_NAMES, EVENT_NAMES

from entities.can import Can
from direct.interval.ActorInterval import ActorInterval
from direct.interval.IntervalGlobal import *

import random

class Queen(Base_Enemy):
    def __init__(self, boss_x, boss_z) -> None:
      super().__init__()

      self.model = Actor(join("assets", "anims", "qUEEN.egg"),{
                  "Idle": join("assets", "anims", "qUEEN-FlyIdle.egg"),
                  "Dead": join("assets", "anims", "qUEEN-Die.egg"),
                  "Kick": join("assets", "anims", "qUEEN-Standard Attack.egg"),
                  "Long-Punch": join("assets", "anims", "qUEEN-StandardAttackLong"),
                  "Fire-Roll": join("assets", "anims", "qUEEN-Fireattack1.egg"),
      })

      self.melee_attacks = {
         "Kick":{
            "hitbox": CollisionBox(Point3(0,-0.5,2),1,0.5,1),
            "duration": 0.3
            }, 
         "Long-Punch": {
            "hitbox": CollisionBox(Point3(0,-0.8,2),1,0.8,0.3),
            "duration": 0.2,
            }, 
         "Light-Punch":{
            "hitbox":  CollisionBox(Point3(0,-0.3,2),1,0.3,1),
            "duration": 1.3
            }, 
         "Jump-Attack":{
            "hitbox":  CollisionBox(Point3(0,0,1),1,1,1),
            "duration": 1.3
            }, 
      }

      # Set initial rotation
      self.model.setH(90)

      self.model.loop("Idle")
        
      self.model.reparentTo(self.parentNode)

      self.parentNode.setPos(boss_x, 4, boss_z)

      self.hp = ENTITY_CONSTANTS.QUEEN_HP
      self.max_hp = ENTITY_CONSTANTS.QUEEN_HP 

      self.attach_hp_bar_to_model()
      self.add_collision_node()

      self.collision.node().addSolid(CollisionBox(Point3(0,-0.6,0),(1,0.6,2)))

      self.attack_range = ENTITY_CONSTANTS.QUEEN_MELEE_ATTACK_RANGE

      self.movement_speed = ENTITY_CONSTANTS.QUEEN_MOVEMENT_SPEED

      self.time_since_last_range_attack = 0

      self.time_since_last_attack = 0

      self.time_since_last_can = 0

      self.is_throwing_cans = False
      
      self.is_in_attack = False

      self.thrown_cans = 0

      self.cans = []

      self.death_animation_duration = 0.7
      
      self.endAttackInterval = Func(self.endAttack)
      
      self.KickInterval = Func(self.kick)
      
      self.KickAnimInterval = self.model.actorInterval("Kick")
    
      
      self.KickSequence = Sequence(Wait(0.3),self.KickInterval,Wait(0.3),self.endAttackInterval)
     
    
      
      self.meleeAttackParallel = Parallel(self.KickAnimInterval,self.KickSequence)
      #self.fireAttackParallel = Parallel(self.FireAnimInterval,)
      

    def update(self, dt, player_pos):
       
   
      
      if self._is_dead:
         return
      
      
      x_movement = 0

      if not self.is_in_attack:
         x_diff_to_player = self.parentNode.getX() - player_pos.getX()

         if abs(x_diff_to_player) < self.attack_range and self.time_since_last_attack > ENTITY_CONSTANTS.QUEEN_MELEE_ATTACK_CD:
            self.time_since_last_attack = 0
            self.meleeAttackParallel.start()
            self.is_in_attack = True
            
         #if abs(x_diff_to_player) > self.attack_range+3 and self.time_since_last_attack > ENTITY_CONSTANTS.QUEEN_MELEE_ATTACK_CD:
            #self.time_since_last_attack = 0
            #self.meleeAttackParallel.start()
            #self.is_in_attack = True
            
         self.time_since_last_attack += dt

         x_movement = self.movement_speed * dt 

         if  abs(x_diff_to_player) < x_movement:
            # prevent -inf exception
            x_movement = max(x_diff_to_player, x_movement / 10)
         
         # Stop moving once close to avoid glitching in player
         if abs(x_diff_to_player) < (self.attack_range / 2):
            x_movement = 0

         if x_diff_to_player < 0: 
            self.model.setH(90)
         elif x_diff_to_player > 0:
            self.model.setH(-90)
            x_movement *= -1

      new_z = 0

      # gravity
      if self.parentNode.getZ() > 0.1  or self.z_velocity > 0:
         self.z_velocity = max(self.z_velocity - (WORLD_CONSTANTS.GRAVITY_VELOCITY * WORLD_CONSTANTS.ENEMY_GRAVITY_MODIFIER), -ENTITY_CONSTANTS.ENEMY_MAX_FALL_SPEED) 
         new_z = min(self.parentNode.getZ() + (self.z_velocity * dt), WORLD_CONSTANTS.MAP_HEIGHT)
         x_movement = self.knockback_velocity * dt
      
      new_x = max(min(self.parentNode.getX() + x_movement, WORLD_CONSTANTS.MAP_X_LIMIT), -WORLD_CONSTANTS.MAP_X_LIMIT)
      
      self.parentNode.setFluidPos(new_x, 4, new_z)

      
      
   
    def kick(self):
       print("kick")
       self.attack_hitbox = self.model.attachNewNode(CollisionNode(ENEMY_ATTACK_NAMES.FOOTBALL_FAN_ATTACK))
       self.attack_hitbox.show()
       self.attack_hitbox.node().addSolid(self.melee_attacks["Kick"]["hitbox"])
       self.attack_hitbox.setTag("team", "enemy")
       self.attack_hitbox.setPos(0,0,-1)
       self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.PLAYER)
       base.cTrav.addCollider(self.attack_hitbox, self.notifier)
       
    def endAttack(self):
       self.is_in_attack = False
       self._destroy_attack_hitbox(f"destroy_{ENEMY_ATTACK_NAMES.BOSS_MELEE_ATTACK}_hitbox")

    def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id or self._is_dead:
         return

      messenger.send(EVENT_NAMES.INCREMENT_COMBO_COUNTER)
      messenger.send(EVENT_NAMES.DISPLAY_HIT, [self.parentNode.getPos()])

      self._update_hp(-1)
      if self.hp <= 0:
         messenger.send(EVENT_NAMES.DEFEAT_BOSS_EVENT)
   
    def destroy(self):
      super().destroy()
      for can in self.cans:
         can.destroy()
      self.cans = []
