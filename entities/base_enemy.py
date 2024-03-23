from panda3d.core import CardMaker, CollisionNode, CollisionHandlerEvent, CollisionEntry, TextNode

import uuid 
from time import time

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
      self._is_dead = False
   
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

      self.death_animation_duration = 0

      self.time_of_death = 0

      self.time_since_last_hit = 0

   def is_dead(self):
      if time() - self.time_of_death > self.death_animation_duration:
         return self._is_dead
      return False

   def add_collision_node(self):

      if self.model is None:
         return

      self.collision = self.model.attachNewNode(CollisionNode("enemy"))

      #self.collision.show()
        
      self.collision.node().setCollideMask(TEAM_BITMASKS.ENEMY)

      self.collision.setTag("id", self.id)

      self.collision.setTag("team", "enemy")

      self.notifier = CollisionHandlerEvent()

      self.notifier.addInPattern("%fn-into")

      self.accept(f"enemy-into", self._player_hit)

      base.cTrav.addCollider(self.collision, self.notifier)

   def add_enemy_name(self,name, x_offset=-0.5, z_offset=2.0):
      self.name_node = TextNode('Enemy Name')
      self.name_node.setTextColor(255,255,255,1)
      self.name_node.setText(name)
      self.name_display = self.parentNode.attachNewNode(self.name_node)
      self.name_display.setPos(x_offset, 0, z_offset)
      self.name_display.setScale(0.2)


   def attach_hp_bar_to_model(self, x_offset=-0.5, z_offset=3.0):
      cmfg = CardMaker('fg')
      cmfg.setFrame(0, 1, -0.1, 0.1)
      self.fg = self.parentNode.attachNewNode(cmfg.generate())
      self.fg.setPos(x_offset,0,z_offset)

      #cmbg = CardMaker('bg')
      #cmbg.setFrame(-1, 0, -0.1, 0.1)
      #self.bg = self.model.attachNewNode(cmbg.generate())
      #self.bg.setPos(-1, 1, 1)

      self.fg.setColor(255, 0, 0, 1)
      #self.bg.setColor(255, 255, 255, 1)S

   def _update_hp_display(self):
      hp_fraction = min(max(self.hp/self.max_hp,0.001), 1)
      self.fg.setScale(hp_fraction, 1, 1)
      #self.bg.setScale(1.0 - hp_fraction, 1, 1)

   def _update_hp(self, value):
      self.hp += value
      self._update_hp_display()
      if self.hp <= 0:
         self._is_dead = True
         self.time_of_death = time()
         self.model.play("Dead")

   def destroy(self):
      if self.model is not None:
         self.model.cleanup()
      self.parentNode.removeNode()

   def _destroy_attack_hitbox(self, _):
      if self.attack_hitbox:
         self.attack_hitbox.removeNode()
         self.attack_hitbox = None
      if self.model:
         self.model.loop("Idle")
      self.is_in_attack = False

   def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id or self._is_dead or entry.from_node.getTag("team") == entry.into_node.getTag("team"):
         return
      
      self._destroy_attack_hitbox(None)

      # Prevent multiple hits with same strike
      if time() - self.time_since_last_hit < 0.5:
         return
      
      self.time_since_last_hit = 0
      attack_identifier = entry.into_node.getName()

      messenger.send(EVENT_NAMES.INCREMENT_COMBO_COUNTER)
      messenger.send(EVENT_NAMES.DISPLAY_HIT, [self.parentNode.getPos()])

      self.model.play("Flinch")

      # Allow light attack to stop enemy from being knocked back
      self.knockback_velocity = 0
      if attack_identifier in [PLAYER_ATTACK_NAMES.HEAVY_ATTACK, PLAYER_ATTACK_NAMES.DASH_ATTACK]:
         print("kncking up")
         self.model.play("Knockup")
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
               self.knockback_velocity = ENTITY_CONSTANTS.PLAYER_DASH_ATTACK_KNOCKBACK
         # This adjusts the knockback direction based on enemy orientation
         # This works because the enemy is always facing the player
         if self.model.getH() > 0:
            self.knockback_velocity *= -1
      self._update_hp(-1)
