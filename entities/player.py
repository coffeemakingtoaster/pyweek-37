from direct.showbase.ShowBase import messenger
from config import ENTITY_CONSTANTS, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from direct.actor.Actor import Actor

from panda3d.core import CollisionNode, Point3, CollisionBox, CollisionHandlerEvent, CollisionEntry, AudioSound

from helpers.constants import EVENT_NAMES, PLAYER_ATTACK_NAMES
from helpers.logging import debug_log
from collections import defaultdict
from time import time

import random

from os.path import join

from helpers.sfx import play_jump

class Player(Base_Entity):
   def __init__(self, player_x, player_z) -> None:
      super().__init__()
   
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self._load_models()
      self._set_model_pos(player_x, player_z)
      self._set_model_h(90)

      self.z_vel = 0

      self.team = TEAM_BITMASKS.PLAYER  

      self.movement_status = {"left": 0, "right": 0 }

      self.last_position = self.main_model.getPos()

      self.hp = ENTITY_CONSTANTS.PLAYER_MAX_HP

      self._setup_keybinds()

      self.notifier = CollisionHandlerEvent()

      self.is_in_light_attack = False

      self.is_in_animation = False

      self.curr_dash_duration = 0

      self.last_hit_timestamp = 0

      self.is_dashing = False

      self.is_dead = False

      self.is_blocking = False

      self.cooldowns = defaultdict(lambda: 0.0)

      self.collision = self.main_model.attachNewNode(CollisionNode("player"))

      self.collision.node().addSolid(CollisionBox(Point3(0,-0.25,0),(1,0.25,1.5)))

      #self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.PLAYER)

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into")

      self.accept(f"player-into", self._enemy_hit)
      
      self.accept('arrived_open_leave',self.enter_station)
      self.accept('arrived_open_enter',self.enter_carriage)
      
      self.currentY = 0

      base.cTrav.addCollider(self.collision, self.notifier)

      self.max_jump_height = WORLD_CONSTANTS.MAP_HEIGHT
      
      self.isBeingKicked = False
      
      self.canBeKicked = False
      
      self.currentQueenX = 0

      self.jump_audio = base.loader.loadSfx(join("assets", "sfx", "jump.mp3"))

      self.punch_audio = [   
         base.loader.loadSfx(join("assets", "sfx", "punch1.wav")),
         base.loader.loadSfx(join("assets", "sfx", "punch2.wav")),
         base.loader.loadSfx(join("assets", "sfx", "punch3.wav")),
         base.loader.loadSfx(join("assets", "sfx", "punch4.wav")),
      ]

   def enter_station(self):
      
      self.currentY = 4
      #TODO Camera
      #TODO Anim
      self.max_jump_height = 3
      
   def enter_carriage(self):
      
      self.currentY = 0
      #TODO Camera
      #TODO Anim
      self.max_jump_height = WORLD_CONSTANTS.MAP_HEIGHT
      
   def leave_station(self):
      print("player Leaving")
      self.currentY = 0
      self.max_jump_height = WORLD_CONSTANTS.MAP_HEIGHT

   def _load_models(self):
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.main_model = Actor("assets/anims/Secretary.egg",{
         'Idle': 'assets/anims/Secretary-Idle.egg',
         'Light-Punch-1':'assets/anims/Secretary-Light Punch.egg',
         'Light-Punch-2':'assets/anims/Secretary-Light Punch 2.egg',
         'Heavy-Punch-1':'assets/anims/Secretary-Heavy Punch.egg',
         'Jump':'assets/anims/Secretary-Jump.egg',
         'Block': 'assets/anims/Secretary-Block',
         'Walk': 'assets/anims/Secretary-Walk',
      })
        
      self.main_model.reparentTo(render)

      self.main_model.loop("Idle")

   def _setup_keybinds(self) -> None:
      self.accept(KEYBIND_IDENTIFIERS.A_KEY_DOWN, self._update_movement_status, ["left", True])
      self.accept(KEYBIND_IDENTIFIERS.A_KEY_UP, self._update_movement_status, ["left", False])
      self.accept(KEYBIND_IDENTIFIERS.D_KEY_DOWN, self._update_movement_status, ["right", True])
      self.accept(KEYBIND_IDENTIFIERS.D_KEY_UP, self._update_movement_status, ["right", False])
      self.accept(KEYBIND_IDENTIFIERS.SPACE_KEY_DOWN, self._jump)
      self.accept(KEYBIND_IDENTIFIERS.O_KEY_DOWN, self._change_hp, [-1])
      self.accept(KEYBIND_IDENTIFIERS.P_KEY_DOWN, self._change_hp, [1])
      self.accept(KEYBIND_IDENTIFIERS.COMMA_KEY_DOWN, self._light_attack)
      self.accept(KEYBIND_IDENTIFIERS.DOT_KEY_DOWN, self._heavy_attack)
      self.accept(KEYBIND_IDENTIFIERS.M_KEY_DOWN, self._block)
      self.accept(KEYBIND_IDENTIFIERS.M_KEY_UP, self._end_block)
      self.accept(KEYBIND_IDENTIFIERS.N_KEY_DOWN, self._dash_attack)
      self.accept("isKicking",self.canBeKicked)
      self.accept("isNotKicking",self.cantBeKickedAnymore)

   def _update_movement_status(self, direction: str, pressed: bool) -> None:
      messenger.send('user_input')
      if pressed:
         self.movement_status[direction] = 1 
      else:
         self.movement_status[direction] = 0

   def canBeKicked(self,queenX):
      self.canBeKicked = True
      self.currentQueenX = queenX
      
   def cantBeKickedAnymore(self):
      self.canBeKicked = False
   
   def _jump(self):
      # Player cannot jump again if midair
      if self.main_model.getZ() < 0.1:
         self.main_model.play('Jump')
         self.z_vel = ENTITY_CONSTANTS.PLAYER_JUMP_VELOCITY

      play_jump ()

   def offboard(self):
      print("offBoarding")
   
   def board(self):
      print("boarding carriage")
   
   def fullHeal(self):
      self._change_hp(ENTITY_CONSTANTS.PLAYER_MAX_HP-self.hp)
   
   def update(self, dt):
      # Clear current status
      
      
      self.main_model.node().resetAllPrevTransform()
      
      x_movement = ((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * ENTITY_CONSTANTS.PLAYER_MOVEMENT_SPEED 
      if self.is_blocking:
         x_movement = 0
      
      new_x = self.main_model.getX() + x_movement* dt
      new_z = 0

      # Rotate right
      if x_movement > 0:
         self._set_model_h(90)
      # Rotate left
      elif x_movement < 0:
         self._set_model_h(-90)

      # Is player in midair? -> Gravity OR did player just start jumping -> Also gravity
      if self.main_model.getZ() > 0.1  or self.z_vel > 0:
         self.z_vel = max(self.z_vel - (WORLD_CONSTANTS.GRAVITY_VELOCITY * dt), -ENTITY_CONSTANTS.PLAYER_MAX_FALL_SPEED) 
         new_z = min(self.main_model.getZ() + (self.z_vel * dt), self.max_jump_height)
         if new_z == WORLD_CONSTANTS.MAP_HEIGHT and self.z_vel > 0:
            self.z_vel /= 2 

      if self.is_dashing:
         if self.curr_dash_duration >= ENTITY_CONSTANTS.PLAYER_DASH_DURATION:
            self.is_dashing = False
            self.curr_dash_duration = 0
            debug_log(f'{self.main_model.getX(), self.main_model.getZ()}')
         else:
            new_x = self.main_model.getX() + (self.dash_direction_x * ( dt / ENTITY_CONSTANTS.PLAYER_DASH_DURATION))
            self.curr_dash_duration += dt
      if not self.isBeingKicked:
         self.main_model.setFluidPos(min(max(new_x, -WORLD_CONSTANTS.MAP_X_LIMIT),WORLD_CONSTANTS.MAP_X_LIMIT), self.currentY, new_z)
      else:
         if self.curr_dash_duration >= ENTITY_CONSTANTS.PLAYER_DASH_DURATION:
            self.isBeingKicked = False
            self.curr_dash_duration = 0
         else:
            if self.currentQueenX > self.main_model.getX():
               new_x = self.main_model.getX() + (-5 * ( dt / ENTITY_CONSTANTS.PLAYER_DASH_DURATION))
            else:
               new_x = self.main_model.getX() + (5 * ( dt / ENTITY_CONSTANTS.PLAYER_DASH_DURATION))
            self.main_model.setFluidPos(min(max(new_x, -WORLD_CONSTANTS.MAP_X_LIMIT),WORLD_CONSTANTS.MAP_X_LIMIT), self.currentY, new_z)
            self.curr_dash_duration += dt
      # Make camera follow player
      base.cam.setX(min(max(self.main_model.getX(), -WORLD_CONSTANTS.CAMERA_X_LIMIT),WORLD_CONSTANTS.CAMERA_X_LIMIT))

      self.last_position = self.main_model.getPos()

      # Animation handling
      if self.is_dashing or self.is_in_animation:
         return
      current_animation = self.main_model.getCurrentAnim() 
      if abs(x_movement) > 0 and current_animation != "Walk":
         self.main_model.loop("Walk")
      elif x_movement == 0 and current_animation == "Walk":
         self.main_model.loop("Idle")
         
      if self.isBeingKicked:
         print("isBeingKicked")

      #debug_log(f'{self.main_model.getX(), self.main_model.getZ()}')

   def _change_hp(self, value):
      self.hp += value
      self.hp = min(self.hp, ENTITY_CONSTANTS.PLAYER_MAX_HP)
      messenger.send(EVENT_NAMES.DISPLAY_PLAYER_HP_EVENT, [self.hp])
      if self.hp <= 0:
         self.is_dead = True

   def _block(self):
      self.is_blocking = True
      self.main_model.loop("Block")

   def _end_block(self):
      self.is_blocking = False
      self.main_model.loop("Idle")

   def _light_attack(self):
      # Prevent animation cancel
      if self.is_in_animation or time() - self.cooldowns[PLAYER_ATTACK_NAMES.LIGHT_ATTACK] < ENTITY_CONSTANTS.PLAYER_LIGHT_ATTACK_CD:
         return
      if self.main_model:
         self.main_model.play(random.choice(['Light-Punch-1', 'Light-Punch-2']))
         self._add_attack_hitbox(PLAYER_ATTACK_NAMES.LIGHT_ATTACK, CollisionBox(Point3(0,-0.3,1.75),1,0.3,0.75), ENTITY_CONSTANTS.PLAYER_LIGHT_ATTACK_DURATION, True)
      self.is_in_light_attack = True
      self.is_in_animation = True
      self.cooldowns[PLAYER_ATTACK_NAMES.LIGHT_ATTACK] = time()
      random.choice(self.punch_audio).play()

   def _heavy_attack(self):
           # Prevent animation cancel
      if self.is_in_animation or time() - self.cooldowns[PLAYER_ATTACK_NAMES.HEAVY_ATTACK] < ENTITY_CONSTANTS.PLAYER_HEAVY_ATTACK_CD:
         return
      if self.main_model:
         self.main_model.play('Heavy-Punch-1')
         self._add_attack_hitbox(PLAYER_ATTACK_NAMES.HEAVY_ATTACK,CollisionBox(Point3(0,-0.5,1.7),1,0.5,0.3), ENTITY_CONSTANTS.PLAYER_HEAVY_ATTACK_DURATION)
      self.is_in_animation = True
      self.cooldowns[PLAYER_ATTACK_NAMES.HEAVY_ATTACK] = time()
      random.choice(self.punch_audio).play()
        
   def _dash_attack(self):
      # Prevent animation cancel
      if self.is_in_animation or time() - self.cooldowns[PLAYER_ATTACK_NAMES.DASH_ATTACK] < ENTITY_CONSTANTS.PLAYER_DASH_ATTACK_CD or self.is_blocking:
         return
      if self.main_model:
         box = CollisionBox(Point3(0,-(ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE / 2),2),1,ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE/2,1)
         self._add_attack_hitbox(PLAYER_ATTACK_NAMES.DASH_ATTACK, box,0.05)

         self.is_dashing = True

         self.cooldowns[PLAYER_ATTACK_NAMES.DASH_ATTACK] = time()

         # right
         self.dash_direction_x = ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE
         
         # left
         if (self.main_model.getH() < 0):
            self.dash_direction_x = - ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE

   def _add_attack_hitbox(self, attack_name, box, attack_duration, is_light_attack = False):
         self.attack_hitbox = self.main_model.attachNewNode(CollisionNode(attack_name))
         #self.attack_hitbox.show()
         self.attack_hitbox.node().addSolid(box)
         self.attack_hitbox.setTag("team", "player")
         self.attack_hitbox.setPos(0,0,-1)
         self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.ENEMY)
         base.cTrav.addCollider(self.attack_hitbox, self.notifier)
         base.taskMgr.doMethodLater(attack_duration, self._destroy_attack_hitbox,f"destroy_{attack_name}_hitbox",[self.attack_hitbox, is_light_attack])

   def _destroy_attack_hitbox(self, hitbox, is_light_attack=False):
      if hitbox:
         hitbox.removeNode()
      if is_light_attack:
         self.is_in_light_attack = False
      self.is_in_animation = False

   def _enemy_hit(self, entry: CollisionEntry):
      # Still in inv period 
      if time() - self.last_hit_timestamp < ENTITY_CONSTANTS.PLAYER_POST_DAMAGE_INV_PERIOD or self.is_blocking:
         return
      messenger.send(EVENT_NAMES.RESET_COMBO_COUNTER)
      #if entry.into_node.getName() in [ENEMY_ATTACK_NAMES.FOOTBALL_FAN_ATTACK]:
      if entry.into_node.getTag("team") == "enemy":
         self._change_hp(-1)
         self.last_hit_timestamp = time()
         if self.canBeKicked:
            self.isBeingKicked = True
            
         

   def _set_model_pos(self, x,z):
      self.main_model.setPos(x, 0, z)

   def _set_model_h(self, h):
      self.main_model.setH(h)

   def getPos(self):
      return self.main_model.getPos()

   def destroy(self):
      self.ignore_all()
      self.main_model.cleanup()
      self.main_model.removeNode()
