from ui.ui_base import ui_base
from helpers.utilities import set_music_volume, set_sfx_volume, set_fullscreen_value, get_music_volume, get_sfx_volume, get_fullscreen_value

from direct.gui.DirectGui import DirectButton, DirectCheckButton, DirectSlider, DirectLabel

import sys
from os.path import join

class settings_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)

        self.load_background_image()

        # Temporary layout
        fullscreen_checkbox = DirectCheckButton(text="Fullscreen", pos=(0,0,0),scale=0.2, indicatorValue=get_fullscreen_value(), command=self.toggle_fullscreen, text_font=self.font)
        self.ui_elements.append(fullscreen_checkbox)

        current_music_volume = get_music_volume()
        music_slider_text = DirectLabel(text="Music volume", scale=0.1, pos=(-0.5,0,-0.25), text_font=self.font)
        self.ui_elements.append(music_slider_text)
        self.music_volume_slider = DirectSlider(pageSize=1, range=(0,100), pos=(-0.5,0,-0.3), scale=0.4, value=int(current_music_volume * 100), command=self.update_music_volume)
        self.ui_elements.append(self.music_volume_slider)

        current_sfx_volume = get_sfx_volume()
        sfx_slider_text = DirectLabel(text="SFX volume", scale=0.1, pos=(0.5,0,-0.25), text_font=self.font)
        self.ui_elements.append(sfx_slider_text)
        self.sfx_volume_slider = DirectSlider(pageSize=1, range=(0,100), pos=(0.5,0,-0.3),  scale=0.4, value=int(current_sfx_volume * 100), command=self.update_sfx_volume)
        self.ui_elements.append(self.sfx_volume_slider)
        play_sample_sfx_button = DirectButton(text=("Play sample sound"), pos=(0.5,0,-0.4), scale=0.05, command=self.play_sample_sound, text_font=self.font)
        self.ui_elements.append(play_sample_sfx_button)

        main_menu_button = DirectButton(text=("return to main menu"), pos=(0,0,-0.6), scale=0.1, command=self.return_to_main_menu, text_font=self.font)
        self.ui_elements.append(main_menu_button)

    def return_to_main_menu(self):
        messenger.send('goto_main_menu')

    def toggle_fullscreen(self, status):
        set_fullscreen_value(status == 1)

    def update_sfx_volume(self):
        value = self.sfx_volume_slider["value"]
        set_sfx_volume(value/100)

    def update_music_volume(self):
        value = self.music_volume_slider["value"]
        set_music_volume(value/100)

    def play_sample_sound(self):
        sample_sfx = base.loader.loadSfx(join("assets", "sfx", "sample.mp3"))
        sample_sfx.play()
