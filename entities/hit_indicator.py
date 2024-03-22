from entities.base import Base_Entity

from panda3d.core import TextNode

import random

HIT_TEXTS = [
   "BOOM",
   "BAM",
   "HIT",
   "PUNCH",
   "OUCH!",
   "NICE HIT",
   "PANDA3D ROCKS!",
   "BANG"
]

class Hit_Indicator(Base_Entity):
   def __init__(self) -> None:
      super().__init__()
      #self.model = Actor("assets/anims/Secretary.egg")
      self.text_node = TextNode('Hit Indicator')
      self.text_node.setTextColor(255,0,0,1)
      self.display = render.attachNewNode(self.text_node)

      self.display.reparentTo(render)
      self.display.setScale(0.1)

      self.hide()

   def hide(self):
      self.display.hide()

   def show(self):
      self.display.show()

   def move_to(self, pos):
      pos.setY(pos.getY() - 1)
      pos = self.__apply_noise(pos)
      self.text_node.setText(random.choice(HIT_TEXTS))
      self.display.setR(random.randrange(-45,45))
      self.display.setPos(pos)
      self.display.show()

   def __apply_noise(self, pos):
      pos.addX(random.uniform(-0.5,0.5))
      pos.addZ(random.uniform(-0.5,0.5) + 1) # They are always a bit low...so lets move them up a bit 

      # Return is not necesary, just for easier use
      return pos
  
   def destroy(self):
      self.display.removeNode()
