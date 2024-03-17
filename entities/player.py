from config import ENTITY_CONSTANTS, TEAM_BITMASKS, KEYBIND_IDENTIFIERS, WORLD_CONSTANTS
from entities.base import Base_Entity
from direct.actor.Actor import Actor

from helpers.logging import debug_log

class Player(Base_Entity):
   def __init__(self, player_x, player_y) -> None:
      super().__init__()
   
      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.model = Actor("assets/eggs/Player.egg",)
        
      self.model.reparentTo(render)

      self.model.setPos(player_x, player_y, 0)

      self.z_vel = 0

      self.team = TEAM_BITMASKS.PLAYER  

      self.movement_status = {"left": 0, "right": 0 }

      self.last_position = self.model.getPos()

      self._setup_keybinds()
   
   def _setup_keybinds(self) -> None:
      self.accept(KEYBIND_IDENTIFIERS.A_KEY_DOWN, self._update_movement_status, ["left", True])
      self.accept(KEYBIND_IDENTIFIERS.A_KEY_UP, self._update_movement_status, ["left", False])
      self.accept(KEYBIND_IDENTIFIERS.D_KEY_DOWN, self._update_movement_status, ["right", True])
      self.accept(KEYBIND_IDENTIFIERS.D_KEY_UP, self._update_movement_status, ["right", False])
      self.accept(KEYBIND_IDENTIFIERS.SPACE_KEY_DOWN, self._jump)

   def _update_movement_status(self, direction: str, pressed: bool) -> None:
      if pressed:
         self.movement_status[direction] = 1 
      else:
         self.movement_status[direction] = 0

   def _jump(self):
      # Player cannot jump again if midair
      if self.model.getZ() < 0.1:
         self.z_vel = ENTITY_CONSTANTS.PLAYER_JUMP_VELOCITY
         debug_log("Jump")

   def update(self, dt):
      # Clear current status
      self.model.node().resetAllPrevTransform()

      new_x = self.model.getX() +((self.movement_status["left"] * -1 ) + self.movement_status["right"]) * ENTITY_CONSTANTS.PLAYER_MOVEMENT_SPEED * dt
      new_z = 0
   
      # Is player in midair? -> Gravity OR did player just start jumping -> Also gravity
      if self.model.getZ() > 0.1 or self.z_vel > 0:
         self.z_vel = max(self.z_vel - WORLD_CONSTANTS.GRAVITY_VELOCITY, -ENTITY_CONSTANTS.PLAYER_MAX_FALL_SPEED) 
         debug_log(self.z_vel)
         new_z = self.model.getZ() + (self.z_vel * dt)

      self.model.setFluidPos(new_x, 0, new_z)
 
      # Make camera follow player
      base.cam.setX(self.model.getX())

      self.last_position = self.model.getPos()

      #debug_log(f'{self.model.getX(), self.model.getZ()}')

   def destroy(self):
      self.ignore_all()
      self.model.removeNode()
