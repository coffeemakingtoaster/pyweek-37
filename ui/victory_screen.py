from ui.ui_base import ui_base 
from config import GAME_STATUS

from direct.gui.DirectGui import DirectButton, OnscreenImage, DirectLabel

from helpers.utilities import format_seconds

import sys

from os.path import join

class victory_screen(ui_base):
    def __init__(self, run_duration, success):
        ui_base.__init__(self)
        self.ui_elements = []
        
        img = OnscreenImage(image=join("assets","icons","hud","backplane.png"), pos=(0,0,0), scale=10)
        img.setTransparency(1, 0)
        img.setAlphaScale(0.5) 
        self.ui_elements.append(img)
       
        if success: 
            outcome_label = DirectLabel(text=("You did it!"),pos=(0,0,0), scale=0.5, text_font=self.font)
            self.ui_elements.append(outcome_label)
        else:
            outcome_label = DirectLabel(text=("Game Over!"),pos=(0,0,0), scale=0.5, text_font=self.font)
            self.ui_elements.append(outcome_label)

        if success:
            timer_info = DirectLabel(text=(format_seconds(run_duration)), pos=(0,0,-.4), scale=0.3 , text_font=self.font)
            self.ui_elements.append(timer_info)
        else:
            timer_info = DirectLabel(text=("Better luck next time"), pos=(0,0,-.4), scale=0.1, text_font=self.font)
            self.ui_elements.append(timer_info)
        
        main_menu_button = DirectButton(text=("Return to main menu"), pos=(0,0,-0.7), scale=0.2, command=self.goto_main_menu, text_font=self.font)
        self.ui_elements.append(main_menu_button)
    
    def goto_main_menu(self):
        messenger.send('goto_main_menu') 