from ui.ui_base import ui_base
from helpers.utilities import format_float

from panda3d.core import TransparencyAttrib
from direct.task.Task import Task

from direct.gui.DirectGui import DirectLabel, OnscreenImage

import sys
from os.path import join

class game_hud(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []

        self.is_paused = False

    def _get_current_time(self):
        return base.clock.getLongTime()

    def destroy(self):
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
