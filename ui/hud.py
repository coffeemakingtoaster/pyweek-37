from config import ENTITY_CONSTANTS, UI_CONSTANTS
from helpers.constants import EVENT_NAMES
from ui.ui_base import ui_base

from os.path import join

from panda3d.core import TransparencyAttrib, Point3
from direct.task.Task import Task

from direct.gui.DirectGui import DirectLabel, OnscreenImage

class game_hud(ui_base):
    hp_display_x_scale = 0.5
    combo_counter_position = (0,0,0.8)
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

        self.combo_counter_display = DirectLabel(text="", scale=0.1, pos=self.combo_counter_position, text_font=self.font, relief = None, text_fg=(0,0,0,1))
        self.ui_elements.append(self.combo_counter_display)

        self.combo_count = 0
        
        self.accept(EVENT_NAMES.DISPLAY_PLAYER_HP_EVENT, self._update_hp_display)
        self.accept(EVENT_NAMES.INCREMENT_COMBO_COUNTER, self._increment_combo_counter)
        self.accept(EVENT_NAMES.RESET_COMBO_COUNTER, self._stop_combo)

        self.time_since_last_combo_attack = 0

        self.hit_indicators = []
        self.pooled_hit_indicators = [DirectLabel(text="BAM",scale=1.1, pos=Point3(0,0,0), text_font=self.font, relief=None, text_fg=(0,0,0,1))] * UI_CONSTANTS.MAX_HIT_INDICATORS
        for item in self.pooled_hit_indicators:
            item.hide()

    def _show_combo_counter(self, is_visible):
        if self.combo_counter_display is None:
            return
        if is_visible:
            self.combo_counter_display.show()
        else:
            self.combo_counter_display.hide()

    def _update_combo_timeframe(self, _):
        if self.time_since_last_combo_attack >= ENTITY_CONSTANTS.PLAYER_COMBO_TIMEFRAME:
            self.combo_count = 0 
            self._show_combo_counter(False)
            return Task.done
        self.time_since_last_combo_attack += base.clock.dt 
        return Task.again

    def _get_current_time(self):
        return base.clock.getLongTime()

    def _update_hp_display(self, hp_value: int) -> None:
        hp_value = max(0, hp_value)
        self.hp_display["text"] =  "{}".format(hp_value)
        x_scale = (self.hp_display_x_scale * min((hp_value/ENTITY_CONSTANTS.PLAYER_MAX_HP),1))
        self.hp_display_bar.setScale(x_scale,1,0.05)
        self.hp_display_bar.setX(-1.35 + -self.hp_display_x_scale + x_scale)

    def _increment_combo_counter(self):
        self.combo_count+=1
        self.combo_counter_display["text"] = "x{}".format(self.combo_count)
        self.time_since_last_combo_attack = 0
        if not base.taskMgr.hasTaskNamed("combo_timeframe_watcher"):
            base.taskMgr.doMethodLater(0.1,self._update_combo_timeframe, "combo_timeframe_watcher")
        self._show_combo_counter(True)

    def _stop_combo(self):
        if base.taskMgr.hasTaskNamed("combo_timeframe_watcher"):
            base.taskMgr.remove("combo_timeframe_watcher")
        self.combo_count = 0
        self._show_combo_counter(False)

    def destroy(self) -> None:
        self.ignoreAll()
        base.taskMgr.removeTasksMatching("hud_update*")
        try:
            super().destroy()
            for indicator in self.hit_indicators + self.pooled_hit_indicators:
                indicator.destroy()
        except:
            print("Nodes were already cleaned up")

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
