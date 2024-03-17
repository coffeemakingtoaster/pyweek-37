from direct.showbase import DirectObject
from abc import abstractmethod


class Base_Entity(DirectObject.DirectObject):
   team = 0
   def __init__(self) -> None:
      super().__init__()

   @abstractmethod
   def destroy(self):
      pass

   @abstractmethod
   def update(self, dt):
      pass
