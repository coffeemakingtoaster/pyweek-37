from config import ENTITY_CONSTANTS, GAME_CONFIG, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from direct.actor.Actor import Actor

from panda3d.core import CollisionNode, Point3, CollisionBox, CollisionHandlerEvent, Vec3

from helpers.constants import EVENT_NAMES
from helpers.logging import debug_log

class Player(Base_Entity):
   def __init__(self, player_x, player_z) -> None:
      super().__init__()

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

      self.curr_dash_duration = 0

      self.is_dashing = False


   def _load_models(self):
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.main_model = Actor("assets/eggs/Player.egg",)
        
      self.main_model.reparentTo(render)

      self.shadow_model = Actor("assets/eggs/Player.egg")

      self.shadow_model.reparentTo(render)

      self.shadow_is_detached = False
      self.shadow_is_catching_up = False

   
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

   def _update_movement_status(self, direction: str, pressed: bool) -> None:
      if pressed:
         self.movement_status[direction] = 1 
      else:
         self.movement_status[direction] = 0

   def _jump(self):
      # Player cannot jump again if midair
      if self.main_model.getZ() < 0.1:
         self.z_vel = ENTITY_CONSTANTS.PLAYER_JUMP_VELOCITY

   def update(self, dt):
      # Clear current status
      self.main_model.node().resetAllPrevTransform()
      
      x_movement = ((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * ENTITY_CONSTANTS.PLAYER_MOVEMENT_SPEED 
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
         if self.is_in_light_attack:
            new_z = self.main_model.getZ()
         else:
            self.z_vel = max(self.z_vel - WORLD_CONSTANTS.GRAVITY_VELOCITY, -ENTITY_CONSTANTS.PLAYER_MAX_FALL_SPEED) 
            new_z = self.main_model.getZ() + (self.z_vel * dt)

      if self.is_dashing:
         print("Dashing")
         if self.curr_dash_duration >= ENTITY_CONSTANTS.PLAYER_DASH_DURATION:
            self.is_dashing = False
            self.curr_dash_duration = 0
            debug_log(f'{self.main_model.getX(), self.main_model.getZ()}')
         else:
            new_x = self.main_model.getX() + (self.dash_direction_x * ( dt / ENTITY_CONSTANTS.PLAYER_DASH_DURATION))
            self.curr_dash_duration += dt
            

      self.main_model.setFluidPos(min(max(new_x, -WORLD_CONSTANTS.MAP_X_LIMIT),WORLD_CONSTANTS.MAP_X_LIMIT), 0, new_z)
      if not self.shadow_is_detached:
         self.shadow_model.setFluidPos(min(max(new_x, -WORLD_CONSTANTS.MAP_X_LIMIT),WORLD_CONSTANTS.MAP_X_LIMIT), 0, new_z)
      else:
         if self.shadow_is_catching_up:
            diff_vect = Vec3(self.main_model.getPos() - self.shadow_model.getPos())
            if diff_vect.length() < (ENTITY_CONSTANTS.PLAYER_SHADOW_CATCH_UP_SPEED * dt):
               self.shadow_is_catching_up = False
               self.shadow_is_detached = False
               self.shadow_model.setFluidPos(self.main_model.getX(), 0, self.main_model.getZ())
               self.shadow_model.setH(self.main_model.getH())
            else:
               diff_vect = diff_vect.normalized()
               diff_vect = diff_vect.normalized() * (ENTITY_CONSTANTS.PLAYER_SHADOW_CATCH_UP_SPEED * dt)
               self.shadow_model.setFluidPos(self.shadow_model.getX() + diff_vect.getX(), 0, self.shadow_model.getZ() + diff_vect.getZ())

 
      # Make camera follow player
      base.cam.setX(min(max(self.main_model.getX(), -WORLD_CONSTANTS.CAMERA_X_LIMIT),WORLD_CONSTANTS.CAMERA_X_LIMIT))

      self.last_position = self.main_model.getPos()

      #debug_log(f'{self.main_model.getX(), self.main_model.getZ()}')

   def _change_hp(self, value):
      self.hp += value
      messenger.send(EVENT_NAMES.DISPLAY_PLAYER_HP_EVENT, [self.hp])

   def _light_attack(self):
      if self.main_model:
         self.attack_hitbox = self.main_model.attachNewNode(CollisionNode("attack"))
         self.attack_hitbox.show()
         self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-1,2),1,1,1))
         self.attack_hitbox.setTag("team", "player")
         self.attack_hitbox.setPos(0,0,-1)
         self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.ENEMY)
         base.cTrav.addCollider(self.attack_hitbox, self.notifier)
         base.taskMgr.doMethodLater(0.3, self._destroy_attack_hitbox,"destroy_light_attack_hitbox",[self.attack_hitbox, True])
      self.is_in_light_attack = True
        
   def _heavy_attack(self):
      if self.main_model:
         self.attack_hitbox = self.main_model.attachNewNode(CollisionNode("attack"))
         self.attack_hitbox.show()
         self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-2,2),1,2,1))
         self.attack_hitbox.setTag("team", "player")
         self.attack_hitbox.setPos(0,0,-1)
         self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.ENEMY)
         base.cTrav.addCollider(self.attack_hitbox, self.notifier)
         base.taskMgr.doMethodLater(0.5, self._destroy_attack_hitbox,"destroy_light_attack_hitbox",[self.attack_hitbox])

         self.is_dashing = True

         # right
         self.dash_direction_x = ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE
         
         # left
         if (self.main_model.getH() < 0):
            self.dash_direction_x = - ENTITY_CONSTANTS.PLAYER_DASH_DISTANCE

         # Second model logic
         base.taskMgr.doMethodLater(ENTITY_CONSTANTS.PLAYER_DASH_DURATION + ENTITY_CONSTANTS.PLAYER_SHADOW_CATCH_UP_INITIAL_DELAY, self._shadow_ketchup, "shadow_catch_up", [0])
         # detach second model for dash effect
         self.shadow_is_detached = True

   def _destroy_attack_hitbox(self, hitbox, is_light_attack=False):
      if hitbox:
         hitbox.removeNode()
      if is_light_attack:
         self.is_in_light_attack = False

   def _shadow_ketchup(self,_):
      self.shadow_is_catching_up = True

   def _set_model_pos(self, x,z):
      self.main_model.setPos(x, 0, z)
      if not self.shadow_is_detached:
         self.shadow_model.setPos(x,0,z)

   def _set_model_h(self, h):
      self.main_model.setH(h)
      if not self.shadow_is_detached:
         self.shadow_model.setH(h)

   def destroy(self):
      self.ignore_all()
      self.main_model.removeNode()
