from panda3d.core import CardMaker, CollisionNode, CollisionHandlerEvent, CollisionEntry

import uuid 


from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from entities.base import Base_Entity
from helpers.constants import EVENT_NAMES, PLAYER_ATTACK_NAMES

class Base_Enemy(Base_Entity):
   def __init__(self) -> None:
      super().__init__()
      
      # Create empty parent node to allow rotating model without rotating hp bar
      self.parentNode = render.attachNewNode("enemy")

      self.hp = 5
      self.max_hp = 5
      self.model = None
      self.is_dead = False
   
      self.z_velocity = 0

      self.hp = 15
      self.max_hp = 15

      self.model = None

      self.id = str(uuid.uuid4())
      self.is_in_attack = False

      self.last_attack_time = 0

      self.attack_hitbox = None

      self.knockback_velocity = 0

      self.attack_range = 0

      self.movement_speed = 0

   def add_collision_node(self):

      if self.model is None:
         return

      self.collision = self.model.attachNewNode(CollisionNode("enemy"))

      self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.ENEMY)

      self.collision.setTag("id", self.id)

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into")

      self.accept(f"enemy-into", self._player_hit)

      base.cTrav.addCollider(self.collision, self.notifier)



   def attach_hp_bar_to_model(self, x_offset=-0.5, z_offset=3):
      cmfg = CardMaker('fg')
      cmfg.setFrame(0, 1, -0.1, 0.1)
      self.fg = self.parentNode.attachNewNode(cmfg.generate())
      self.fg.setPos(x_offset,0,z_offset)

      #cmbg = CardMaker('bg')
      #cmbg.setFrame(-1, 0, -0.1, 0.1)
      #self.bg = self.model.attachNewNode(cmbg.generate())
      #self.bg.setPos(-1, 1, 1)

      self.fg.setColor(255, 0, 0, 1)
      #self.bg.setColor(255, 255, 255, 1)

   def _update_hp_display(self):
      hp_fraction = min(max(self.hp/self.max_hp,0.001), 1)
      self.fg.setScale(hp_fraction, 1, 1)
      #self.bg.setScale(1.0 - hp_fraction, 1, 1)

   def _update_hp(self, value):
      self.hp += value
      self._update_hp_display()
      if self.hp <= 0:
         self.is_dead = True

   def destroy(self):
      self.parentNode.removeNode()

   def _destroy_attack_hitbox(self, _):
      if self.attack_hitbox:
         self.attack_hitbox.removeNode()
         self.attack_hitbox = None
      self.is_in_attack = False

   def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id:
         return
      attack_identifier = entry.into_node.getName()

      messenger.send(EVENT_NAMES.INCREMENT_COMBO_COUNTER)
      messenger.send(EVENT_NAMES.DISPLAY_HIT, [self.parentNode.getPos()])

      self._destroy_attack_hitbox(None)
      # Allow light attack to stop enemy from being knocked back
      self.knockback_velocity = 0
      if attack_identifier in [PLAYER_ATTACK_NAMES.HEAVY_ATTACK, PLAYER_ATTACK_NAMES.DASH_ATTACK]:
         # This is a CC attack
         if self.model.getZ() > 0.1:
            # Stop the fall
            self.z_velocity = 3 
         else:
            if attack_identifier == PLAYER_ATTACK_NAMES.HEAVY_ATTACK:
               self.z_velocity = ENTITY_CONSTANTS.PLAYER_HEAVY_ATTACK_KNOCKUP
               self.knockback_velocity = ENTITY_CONSTANTS.PLAYER_HEAVY_ATTACK_KNOCKBACK
            else:
               self.z_velocity = ENTITY_CONSTANTS.PLAYER_DASH_KNOCKUP
         # This adjusts the knockback direction based on enemy orientation
         # This works because the enemy is always facing the player
         if self.model.getH() > 0:
            self.knockback_velocity *= -1
      self._update_hp(-1)
