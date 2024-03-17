from panda3d.core import BitMask32
import math

class GAME_CONFIG:
   DEFAULT_WINDOW_HEIGHT = 720
   DEFAULT_WINDOW_WIDTH = 1280

class GAME_STATUS:
   MAIN_MENU = "main_menu"
   LOADING_LEVEL = "loading_level"
   PAUSED = "paused"
   RUNNING = "running"
   STARTING = "starting"
   SETTINGS = "settings"
   GAME_FINISH = "game_finish'"

class TEAM_BITMASKS:
   PLAYER =  BitMask32(1 << 0) #0001

class KEYBIND_IDENTIFIERS:
   A_KEY_DOWN = "a"
   A_KEY_UP = A_KEY_DOWN + "-up"
   D_KEY_DOWN = "d"
   D_KEY_UP = D_KEY_DOWN + "-up"
   SPACE_KEY_DOWN = "space"
   SPACE_KEY_UP = SPACE_KEY_DOWN + "-up" 
   ESCAPE_KEY_DOWN = "escape"

class WORLD_CONSTANTS:
   GRAVITY_VELOCITY = math.pi * 2 
   MAP_X_LIMIT = 100
   # Make camera more dynamic
   CAMERA_X_LIMIT = MAP_X_LIMIT - 10

class ENTITY_CONSTANTS:
   PLAYER_MOVEMENT_SPEED = 5
   PLAYER_JUMP_VELOCITY = 60
   PLAYER_MAX_FALL_SPEED = 30 
   PLAYER_MAX_HP = 10
