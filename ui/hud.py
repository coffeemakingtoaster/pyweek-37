from config import ENTITY_CONSTANTS
from helpers.constants import EVENT_NAMES
from ui.ui_base import ui_base
from helpers.utilities import format_float

from os.path import join

from panda3d.core import TransparencyAttrib
from direct.task.Task import Task

from direct.gui.DirectGui import DirectLabel, OnscreenImage

class game_hud(ui_base):
    hp_display_x_scale = 0.5
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []
        self.is_paused = False

        self.hp_display_bar = OnscreenImage(scale=(self.hp_display_x_scale,1, 0.05), pos=(-1.35, 0, 0.95), image=join("assets", "icons", "hud", "hp_display_bar.png"), color=(255,0,0,1))
        self.hp_display_bar.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(self.hp_display_bar)
        self.hp_display_background = OnscreenImage(scale=(self.hp_display_x_scale,1, 0.05), pos=(-1.35, 0, 0.95), image=join("assets", "icons", "hud", "hp_display_backplane.png"))
        self.hp_display_background.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(self.hp_display_background)
        self.hp_display = DirectLabel(text="{}".format(ENTITY_CONSTANTS.PLAYER_MAX_HP), scale=0.1, pos=(-0.008, 0, -0.74), text_font=self.font, relief=None, text_fg=(0,0,0,1))
        self.ui_elements.append(self.hp_display)
        
        self.accept(EVENT_NAMES.DISPLAY_PLAYER_HP_EVENT, self._update_hp_display)

    def _get_current_time(self):
        return base.clock.getLongTime()

    def _update_hp_display(self, hp_value: int) -> None:
        hp_value = max(0, hp_value)
        self.hp_display["text"] =  "{}".format(hp_value)
        x_scale = (self.hp_display_x_scale * min((hp_value/ENTITY_CONSTANTS.PLAYER_MAX_HP),1))
        self.hp_display_bar.setScale(x_scale,1,0.05)
        self.hp_display_bar.setX(-1.35 + -self.hp_display_x_scale + x_scale)

    def destroy(self) -> None:
        self.ignoreAll()
        base.taskMgr.removeTasksMatching("hud_update*")
        try:
            super().destroy()
        except:
            print("Nodes were already cleaned up")

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
