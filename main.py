from entities.boss import Boss
from entities.queen import Queen
from handlers.hit_indicator_handler import Hit_Indicator_Handler
from helpers.constants import EVENT_NAMES
from panda3d.core import loadPrcFile, DirectionalLight, AmbientLight, LVector3, CollisionTraverser
from entities.player import Player
from entities.football_fan import Football_Fan
from entities.Gent import Gent

from entities.carriage import Carriage
from entities.map import Map
from helpers.logging import debug_log
from ui.main_menu import main_menu
from ui.pause_menu import pause_menu
from ui.settings_menu import settings_menu
from ui.victory import victory_screen
from ui.hud import game_hud
from config import GAME_STATUS, KEYBIND_IDENTIFIERS
from helpers.utilities import load_config, lock_mouse_in_window, release_mouse_from_window

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from direct.gui.OnscreenText import OnscreenText
from gameState import GameFSM

from os.path import join

# Load panda3d configfile that disables model caching
loadPrcFile("./settings.prc")

class main_game(ShowBase):
    player = None
    enemies = []
    hit_indicator_handler = None
    def __init__(self):

        ShowBase.__init__(self)

        
        # Print all occuring events
        #messenger.toggleVerbose()

        # Set camera position
        base.cam.setPos(0, -7, 1)

        load_config(join("user_config.json"))

        self.game_status = GAME_STATUS.MAIN_MENU

        self.phase = 1
        
        self.state = "Drive"
        
        self.backup = 8 #TODO 20

        self.setupLights()
        
        self.map = None

        self.carriage = None

        self.current_hud = None

        self.status_display = OnscreenText(text=GAME_STATUS.MAIN_MENU, pos=(0.9,0.9 ), scale=0.07,fg=(255,0,0, 1))

        self.active_ui = None
        self.goto_to_main_menu()

        # Create event handlers for events fired by UI
        self.accept(EVENT_NAMES.START_GAME_EVENT, self.set_game_status, [GAME_STATUS.STARTING])

        # Create event handlers for events fired by keyboard
        self.accept(KEYBIND_IDENTIFIERS.ESCAPE_KEY_DOWN, self.toggle_pause)

        self.accept(EVENT_NAMES.PAUSE_GAME_EVENT , self.toggle_pause)

        self.accept(EVENT_NAMES.GOTO_MAIN_MENU_EVENT, self.goto_to_main_menu)
        self.accept(EVENT_NAMES.TOGGLE_SETTINGS_EVENT, self.toggle_settings)
        
        self.accept(KEYBIND_IDENTIFIERS.J_KEY_DOWN,self.set_Station)
        self.accept(KEYBIND_IDENTIFIERS.K_KEY_DOWN,self.set_Drive)

        self.accept(EVENT_NAMES.SPAWN_BOSS_EVENT, self.spawn_boss)
        self.accept(EVENT_NAMES.DEFEAT_BOSS_EVENT, self.bossDied)
        
        self.accept('station_leave',self.setStateDrive)

        self.accept('player_died', self.lose_game)

        self.gameTask = base.taskMgr.add(self.game_loop, "gameLoop")

        # Load music
        background_music = base.loader.loadMusic(join("assets", "music", "music.mp3"))
        background_music.setLoop(True)
        background_music.play()
    
        render.setShaderAuto()

        base.disableMouse()
        
        self.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)

        self._cached_entities = [Player(-10000,0),Carriage(),Map()]

        self.current_run_duration = 0

    def setupLights(self):  
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.4, .4, .4, 4))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, -45, -45))
        directionalLight.setColor((0.3, 0.3, 0.3, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))

    def game_loop(self, _):

        if self.game_status == GAME_STATUS.STARTING:
            print("Starting")
            self.set_game_status(GAME_STATUS.LOADING_LEVEL)
            # Move this to task?
            self.load_game()

        # Do not progress game logic if game is not active
        if self.game_status != GAME_STATUS.RUNNING:
           return Task.cont

        if self.player.is_dead:
            self.lose_game()
            return Task.cont

        dt = self.clock.dt

        self.player.update(dt)

        self.current_run_duration += dt
        
        self.carriage.update(dt)
        
        self.map.update(dt)
        
        remaining_enemies = []

        if len(self.enemies) < 5 and self.state == "Drive" and self.backup > 1:
            if self.phase == 1:
                self.enemies.append(Football_Fan(-10,0))
                self.enemies.append(Football_Fan(20,0))
                self.backup -= 2
            else:
                self.enemies.append(Gent(-10,0))
                self.enemies.append(Gent(20,0))
                self.backup -= 2
                    
        if len(self.enemies) <= 2 and self.state == "Drive" and self.backup == 0:
            self.set_Station()

        for enemy in self.enemies:
            enemy.update(dt, self.player.getPos())
            if enemy.is_dead():
                enemy.destroy()
                continue
            # Is this inefficient? Probably yes...
            remaining_enemies.append(enemy)
        self.enemies = remaining_enemies

        return Task.cont

    def load_game(self):
        print("Loading game")

        self.active_ui.destroy()
        self.setBackgroundColor((0,0,0, 1))

        self.active_ui = game_hud()

        lock_mouse_in_window()
        self.set_game_status(GAME_STATUS.RUNNING)

        # Setup entities
        self.player = Player(0,0)
        
        self.carriage = Carriage()
        
        self.map = Map()

        self.hit_indicator_handler = Hit_Indicator_Handler()

        self.backup = 8 #TODO 20
        
        self.enemies = []
        
        self.gameState = GameFSM(self.player,self.map,self.carriage)
        
        self.gameState.request('Drive')
        
        self.state = "Drive"

        # destroy cache
        for entity in self._cached_entities:
            entity.destroy()
        self._cached_entities = []    

        self.current_run_duration = 0

    def bossDied(self):
        if self.phase == 1:
            self.phase = 2
            self.backup = 8
            self.set_Drive()
        else:
            self.win_game()
    
    def win_game(self):
        self.set_game_status(GAME_STATUS.GAME_FINISH)
        if self.current_hud:
            self.current_hud.destroy()
        self.active_ui = victory_screen(self.current_run_duration, True)

    def lose_game(self):
        self.set_game_status(GAME_STATUS.GAME_FINISH)
        if self.current_hud:
            self.current_hud.destroy()
        self.active_ui = victory_screen(self.current_run_duration, False)
   
    def set_Drive(self):
        
        self.gameState.request('Drive')
        
    def setStateDrive(self):
        self.state = "Drive"
        
    def set_Station(self):
        self.state = "Station"
        self.gameState.request('Station')
            
    def set_game_status(self, status):
        self.status_display["text"] = status
        self.game_status = status

    def toggle_pause(self):
        #self.gameState.request('Station')
        if self.game_status == GAME_STATUS.RUNNING:
            self.set_game_status(GAME_STATUS.PAUSED)
            # Not needed as of now as gui does not exist
            self.current_hud = self.active_ui
            self.current_hud.pause()
            release_mouse_from_window()
            self.active_ui = pause_menu()
        elif self.game_status == GAME_STATUS.PAUSED:
            self.active_ui.destroy()
            self.current_hud.resume()
            self.active_ui = self.current_hud
            lock_mouse_in_window()
            self.set_game_status(GAME_STATUS.RUNNING)

    def goto_to_main_menu(self):
        # no hud yet
        if self.active_ui is not None:
            self.active_ui.destroy()
        if self.current_hud is not None:
            self.current_hud.destroy()
            self.current_hud = None
        self.active_ui = main_menu()
        self.setBackgroundColor((0, 0, 0, 1))
        self.set_game_status(GAME_STATUS.MAIN_MENU)
        # Destroy player object
        if self.player is not None:
            self.player.destroy()
            self.player = None
        
        if self.map is not None:
            self.map.destroy()

        if self.carriage is not None:
            self.carriage.destroy()

        
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies = []
        if self.hit_indicator_handler is not None:
            self.hit_indicator_handler.destroy()
            self.hit_indicator_handler = None

    def toggle_settings(self):
        if self.game_status == GAME_STATUS.MAIN_MENU:
            self.active_ui.destroy()
            self.active_ui = settings_menu()
            self.set_game_status(GAME_STATUS.SETTINGS)
        elif self.game_status == GAME_STATUS.SETTINGS:
            self.active_ui.destroy()
            self.active_ui = main_menu()
            self.set_game_status(GAME_STATUS.MAIN_MENU)

    def spawn_boss(self):
        if self.game_status != GAME_STATUS.RUNNING:
            return
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies = []
        if self.phase == 1:
            self.enemies.append(Boss(0,0)) #TODO BOSS
        else:
            self.enemies.append(Queen(0,0))

        
    def finish_game(self, success: bool):
        self.set_game_status(GAME_STATUS.GAME_FINISH)
        self.active_ui.destroy()
        self.current_hud = None
        self.active_ui = victory_screen(self.current_run_duration, success)

def start_game():
    print("Starting game..")
    debug_log("Debug log enabled")
    game = main_game()
    game.run()

if __name__ == "__main__":
    start_game()
