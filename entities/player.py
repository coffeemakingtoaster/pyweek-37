from config import ENTITY_CONSTANTS, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from direct.actor.Actor import Actor

from panda3d.core import CollisionNode, Point3, CollisionBox, CollisionHandlerEvent

from helpers.constants import EVENT_NAMES
from helpers.logging import debug_log

class Player(Base_Entity):
   def __init__(self, player_x, player_z) -> None:
      super().__init__()
   
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.model = Actor("assets/eggs/Player.egg",)
        
      self.model.reparentTo(render)

      self.model.setPos(player_x, 0, player_z)

      self.z_vel = 0

      self.team = TEAM_BITMASKS.PLAYER  

      self.movement_status = {"left": 0, "right": 0 }

      self.last_position = self.model.getPos()

      self.hp = ENTITY_CONSTANTS.PLAYER_MAX_HP

      self._setup_keybinds()

      self.notifier = CollisionHandlerEvent()

      self.is_in_light_attack = False
   
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
      if self.model.getZ() < 0.1:
         self.z_vel = ENTITY_CONSTANTS.PLAYER_JUMP_VELOCITY

   def update(self, dt):
      # Clear current status
      self.model.node().resetAllPrevTransform()
      
      x_movement = ((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * ENTITY_CONSTANTS.PLAYER_MOVEMENT_SPEED 
      new_x = self.model.getX() + x_movement* dt
      new_z = 0

      # Rotate right
      if x_movement > 0:
         self.model.setH(90) 
      # Rotate left
      elif x_movement < 0:
         self.model.setH(-90)


      # Is player in midair? -> Gravity OR did player just start jumping -> Also gravity
      if self.model.getZ() > 0.1  or self.z_vel > 0:
         if self.is_in_light_attack:
            new_z = self.model.getZ()
         else:
            self.z_vel = max(self.z_vel - WORLD_CONSTANTS.GRAVITY_VELOCITY, -ENTITY_CONSTANTS.PLAYER_MAX_FALL_SPEED) 
            new_z = self.model.getZ() + (self.z_vel * dt)

      self.model.setFluidPos(min(max(new_x, -WORLD_CONSTANTS.MAP_X_LIMIT),WORLD_CONSTANTS.MAP_X_LIMIT), 0, new_z)
 
      # Make camera follow player
      base.cam.setX(min(max(self.model.getX(), -WORLD_CONSTANTS.CAMERA_X_LIMIT),WORLD_CONSTANTS.CAMERA_X_LIMIT))

      self.last_position = self.model.getPos()

      #debug_log(f'{self.model.getX(), self.model.getZ()}')

   def _change_hp(self, value):
      self.hp += value
      messenger.send(EVENT_NAMES.DISPLAY_PLAYER_HP_EVENT, [self.hp])

   def _light_attack(self):
      if self.model:
         self.attack_hitbox = self.model.attachNewNode(CollisionNode("attack"))
         self.attack_hitbox.show()
         self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-1,2),1,1,1))
         self.attack_hitbox.setTag("team", "player")
         self.attack_hitbox.setPos(0,0,-1)
         self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.ENEMY)
         base.cTrav.addCollider(self.attack_hitbox, self.notifier)
         base.taskMgr.doMethodLater(0.3, self._destroy_attack_hitbox,"destroy_light_attack_hitbox",[self.attack_hitbox, True])
      self.is_in_light_attack = True
        
   def _heavy_attack(self):
      if self.model:
         self.attack_hitbox = self.model.attachNewNode(CollisionNode("attack"))
         self.attack_hitbox.show()
         self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-2,2),1,2,1))
         self.attack_hitbox.setTag("team", "player")
         self.attack_hitbox.setPos(0,0,-1)
         self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.ENEMY)
         base.cTrav.addCollider(self.attack_hitbox, self.notifier)
         base.taskMgr.doMethodLater(0.5, self._destroy_attack_hitbox,"destroy_light_attack_hitbox",[self.attack_hitbox])

   def _destroy_attack_hitbox(self, hitbox, is_light_attack=False):
      if hitbox:
         hitbox.removeNode()
      if is_light_attack:
         self.is_in_light_attack = False
      

   def destroy(self):
      self.ignore_all()
      self.model.removeNode()
