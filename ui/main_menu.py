from ui.ui_base import ui_base 
from helpers.utilities import save_config
from helpers.constants import EVENT_NAMES

from direct.gui.DirectGui import DirectButton
from panda3d.core import TransparencyAttrib


import sys
from os.path import join

class main_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.ui_elements = []
        
        self.load_background_image()
        
        start_button = DirectButton(text="start",pos=(0,0,-0.1), scale=0.3, command=self.start_game, text_font=self.main_font, text_fg=(255,255,255,1), relief=None)
        self.ui_elements.append(start_button)
        
        settings_button = DirectButton(image=join("assets", "icons", "main menu","settings.png"), scale=0.1, pos=(-1.6,0,0.85), command=self.open_settings, relief=None)
        settings_button.setTransparency(TransparencyAttrib.MAlpha)
        self.ui_elements.append(settings_button)
        
        quit_button = DirectButton(text=("quit"), pos=(0,0,-0.6), scale=0.2, command=self.quit_game, text_font=self.main_font, text_fg=(255,255,255,1), relief=None)
        self.ui_elements.append(quit_button)

    def start_game(self):
        print("Start button pressed")
        # Use global event messenger to start the game
        messenger.send(EVENT_NAMES.START_GAME_EVENT) 
        
    def open_settings(self):
       messenger.send(EVENT_NAMES.TOGGLE_SETTINGS_EVENT)
       
    def quit_game(self):
        save_config(join("user_config.json"))
        sys.exit()
