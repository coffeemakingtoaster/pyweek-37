from ui.ui_base import ui_base

from direct.gui.DirectGui import DirectButton, OnscreenImage

from os.path import join

class pause_menu(ui_base):
    def __init__(self):
        ui_base.__init__(self)
        self.ui_elements = []

        img = OnscreenImage(image=join("assets","icons","pause","backplane.png"), pos=(0,0,0), scale=10)
        img.setTransparency(1, 0)
        img.setAlphaScale(0.5)
        self.ui_elements.append(img)

        continue_button = DirectButton(text=("Continue"),pos=(0,0,0), scale=0.2, command=self.unpause_game, text_font=self.font)
        self.ui_elements.append(continue_button)

        main_menu_button = DirectButton(text=("Return to main menu"), pos=(0,0,-0.6), scale=0.2, command=self.goto_main_menu, text_font=self.font)
        self.ui_elements.append(main_menu_button)

    def unpause_game(self):
        messenger.send('pause_game')

    def goto_main_menu(self):
        messenger.send('goto_main_menu')
