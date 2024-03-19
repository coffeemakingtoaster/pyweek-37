from panda3d.core import CardMaker


from entities.base import Base_Entity

class Base_Enemy(Base_Entity):
   def __init__(self) -> None:
      super().__init__()

      self.parentNode = render.attachNewNode("enemy")

      self.hp = 5
      self.max_hp = 5
      self.model = None

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

