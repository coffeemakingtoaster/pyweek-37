from entities.base_enemy import Base_Enemy
from direct.actor.Actor import Actor


# This is used for testing, not for the actual game
class Sample_Enemy(Base_Enemy):
   def __init__(self, enemy_x, enemy_z) -> None:
      super().__init__()

      # We dont need coordinates because we use the coordinates of the model. This assures that the visual representation of the player is correct.
      self.model = Actor("assets/eggs/Player.egg",)
        
      self.model.reparentTo(render)

      self.model.setPos(enemy_x, 0, enemy_z)

      self.hp = 15
      self.max_hp = 15

      self.attach_hp_bar_to_model()

      self.accept("u", self._update_hp, [-1])


   def _update_hp(self, value):
      self.hp += value
      self._update_hp_display()
