from config import UI_CONSTANTS
from entities.base import Base_Entity
from entities.hit_indicator import Hit_Indicator
from helpers.constants import EVENT_NAMES

from direct.task.Task import Task

class Hit_Indicator_Handler(Base_Entity):
   def __init__(self) -> None:
      self.pool = [] 
      for _ in range(UI_CONSTANTS.MAX_HIT_INDICATORS):
         self.pool.append(Hit_Indicator())
      self.used = []
      self.accept(EVENT_NAMES.DISPLAY_HIT, self._display_hit)

   def _display_hit(self, pos):
      if len(self.pool) == 0:
         return
      # Move point towards camera so it covers other entities
      pos.setY(-1) 
      indicator = self.pool.pop()
      indicator.move_to(pos)
      self.used.append(indicator)
      base.taskMgr.doMethodLater(UI_CONSTANTS.HIT_INDICATOR_DISPLAY_TIME, self._release_indicator, "release_indicator_to_pool")

   def _release_indicator(self,_):
      if len(self.used) < 0:
         return Task.done
      
      indicator = self.used.pop(-1)
      indicator.hide()
      self.pool.append(indicator)
      return Task.done

   def destroy(self):
      self.ignoreAll()
      base.taskMgr.remove("release_indicator_to_pool")
      for indicator in self.pool + self.used:
         indicator.destroy()
