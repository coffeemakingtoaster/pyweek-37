from entities.base_enemy import Base_Enemy

from direct.actor.Actor import Actor

from os.path import join

from panda3d.core import CollisionBox, Point3, CollisionEntry, CollisionNode

from config import ENTITY_CONSTANTS, TEAM_BITMASKS, WORLD_CONSTANTS
from helpers.constants import ENEMY_ATTACK_NAMES, EVENT_NAMES

from entities.can import Can


class Boss(Base_Enemy):
   def __init__(self, boss_x, boss_z) -> None:
      super().__init__()

      self.model = Actor(join("assets", "eggs", "Player.egg"))
   
      # Set initial rotation
      self.model.setH(90)
        
      self.model.reparentTo(self.parentNode)

      self.parentNode.setPos(boss_x, 0, boss_z)

      self.hp = ENTITY_CONSTANTS.BOSS_HP
      self.max_hp = ENTITY_CONSTANTS.BOSS_HP 

      self.attach_hp_bar_to_model()
      self.add_collision_node()

      self.collision.node().addSolid(CollisionBox(Point3(0,-1,0),(1,1,2)))

      self.attack_range = ENTITY_CONSTANTS.BOSS_MELEE_ATTACK_RANGE

      self.movement_speed = ENTITY_CONSTANTS.BOSS_MOVEMENT_SPEED

      self.time_since_last_range_attack = 0

      self.time_since_last_melee_attack = 0

      self.time_since_last_can = 0

      self.is_throwing_cans = False

      self.thrown_cans = 0

      self.cans = []


   def update(self, dt, player_pos):
      
      if self.is_dead:
         return
      
      x_movement = 0

      if self.time_since_last_can > ENTITY_CONSTANTS.BOSS_RANGED_ATTACK_CD and not self.is_in_attack and not self.is_throwing_cans:
         self._range_attack()

      if not self.is_in_attack:
         x_diff_to_player = self.parentNode.getX() - player_pos.getX()

         if abs(x_diff_to_player) < self.attack_range:
            self._melee_attack()

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
      
      self.parentNode.setFluidPos(new_x, 0, new_z)

      self.time_since_last_range_attack += dt
      self.time_since_last_melee_attack += dt
      self.time_since_last_can += dt
   
      remaining_cans = []
      for can in self.cans:
         if can.is_dead:
            can.destroy()
            continue
         can.update(dt)
         remaining_cans.append(can)

      self.cans = remaining_cans

      if self.is_throwing_cans and self.time_since_last_can >= ENTITY_CONSTANTS.BOSS_RANGED_ATTACK_INTERVAL:
         direction = 1
         if self.model.getH() < 90:
            direction = -1
         self.cans.append(Can(self.parentNode.getX(), self.parentNode.getZ(), direction))
         self.thrown_cans += 1
         self.time_since_last_can = 0
         if self.thrown_cans >= ENTITY_CONSTANTS.BOSS_RANGED_ATTACK_RANGED_AMOUNT:
            self.is_throwing_cans = False
            self.is_in_attack = False
            self.time_since_last_range_attack = 0

   def _melee_attack(self):
      if self.time_since_last_melee_attack < ENTITY_CONSTANTS.BOSS_MELEE_ATTACK_CD or self.time_since_last_range_attack < ENTITY_CONSTANTS.BOSS_MELEE_ATTACK_CD:
         return
      self.is_in_attack = True
      self.attack_hitbox = self.model.attachNewNode(CollisionNode(ENEMY_ATTACK_NAMES.FOOTBALL_FAN_ATTACK))
      self.attack_hitbox.show()
      self.attack_hitbox.node().addSolid(CollisionBox(Point3(0,-1,2),1,1,1))
      self.attack_hitbox.setTag("team", "enemy")
      self.attack_hitbox.setPos(0,0,-1)
      self.attack_hitbox.node().setCollideMask(TEAM_BITMASKS.PLAYER)
      base.cTrav.addCollider(self.attack_hitbox, self.notifier)
      self.time_since_last_melee_attack = 0
      base.taskMgr.doMethodLater(ENTITY_CONSTANTS.BOSS_MELEE_ATTACK_DURATION, self._destroy_attack_hitbox,f"destroy_{ENEMY_ATTACK_NAMES.BOSS_MELEE_ATTACK}_hitbox")

   def _range_attack(self):
      if self.time_since_last_range_attack < ENTITY_CONSTANTS.BOSS_RANGED_ATTACK_CD or self.time_since_last_melee_attack < ENTITY_CONSTANTS.BOSS_RANGED_ATTACK_CD:
         return
      self.thrown_cans = 0
      self.is_throwing_cans = True
      self.is_in_attack = True

   def _player_hit(self, entry: CollisionEntry):
      if entry.from_node.getTag("id") != self.id:
         return

      messenger.send(EVENT_NAMES.INCREMENT_COMBO_COUNTER)
      messenger.send(EVENT_NAMES.DISPLAY_HIT, [self.parentNode.getPos()])

      self._update_hp(-1)
   
   def destroy(self):
      super().destroy()
      for can in self.cans:
         can.destroy()
      self.cans = []
