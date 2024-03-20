from entities.base import Base_Entity

from direct.actor.Actor import Actor

class Hit_Indicator(Base_Entity):
   def __init__(self) -> None:
      super().__init__()
      self.model = Actor("assets/anims/Secretary.egg")
        
      self.model.reparentTo(render)

      self.hide()

   def hide(self):
      self.model.hide()

   def show(self):
      self.model.show()

   def move_to(self, pos):
      self.model.setPos(pos)
      self.model.show()
  
   def destroy(self):
      self.model.cleanup()
      self.model.removeNode()
