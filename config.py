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
   ENEMY = BitMask32(1 << 1) #0010

class KEYBIND_IDENTIFIERS:
   A_KEY_DOWN = "a"
   A_KEY_UP = A_KEY_DOWN + "-up"
   D_KEY_DOWN = "d"
   D_KEY_UP = D_KEY_DOWN + "-up"
   SPACE_KEY_DOWN = "space"
   SPACE_KEY_UP = SPACE_KEY_DOWN + "-up" 
   ESCAPE_KEY_DOWN = "escape"
   O_KEY_DOWN = "o"
   O_KEY_UP = O_KEY_DOWN + "-up"
   P_KEY_DOWN = "p"
   P_KEY_UP = P_KEY_DOWN + "-up"
   COMMA_KEY_DOWN = ","
   COMMA_KEY_UP = COMMA_KEY_DOWN + "-up"
   DOT_KEY_DOWN = "."
   DOT_KEY_UP = DOT_KEY_DOWN + "-up"
   M_KEY_DOWN = "m"
   M_KEY_UP = M_KEY_DOWN + "-up"
   J_KEY_DOWN = "j"
   K_KEY_DOWN = "k"
   N_KEY_DOWN = "n"
   N_KEY_UP = N_KEY_DOWN + "-up"

class WORLD_CONSTANTS:
   GRAVITY_VELOCITY = math.pi * 5
   MAP_X_LIMIT = 8
   MAP_HEIGHT = 1
   # Make camera more dynamic
   CAMERA_X_LIMIT = MAP_X_LIMIT - 3
   TUNNEL_SPEED = 15
   CARRIAGE_SPEED = 15
   ENEMY_GRAVITY_MODIFIER = 1/8

class UI_CONSTANTS:
   MAX_HIT_INDICATORS = 5
   HIT_INDICATOR_DISPLAY_TIME = 0.3

class ENTITY_CONSTANTS:
   PLAYER_MOVEMENT_SPEED = 5
   PLAYER_JUMP_VELOCITY = 7
   PLAYER_MAX_FALL_SPEED = 15
   PLAYER_MAX_HP = 10
   PLAYER_SHADOW_CATCH_UP_SPEED = 60 
   PLAYER_SHADOW_CATCH_UP_INITIAL_DELAY = 0.1
   PLAYER_DASH_DURATION = 0.15
   PLAYER_DASH_DISTANCE = 3
   PLAYER_DASH_KNOCKUP = 50
   PLAYER_HEAVY_ATTACK_KNOCKUP = 100
   PLAYER_HEAVY_ATTACK_KNOCKBACK = 3
   PLAYER_DASH_ATTACK_KNOCKBACK = 7
   PLAYER_POST_DAMAGE_INV_PERIOD = 1
   PLAYER_COMBO_TIMEFRAME = 1.5
   PLAYER_HEAVY_ATTACK_DURATION = 0.2
   PLAYER_LIGHT_ATTACK_DURATION = 0.05
   PLAYER_HEAVY_ATTACK_CD = 0.5
   PLAYER_DASH_ATTACK_CD = 0.5
   PLAYER_LIGHT_ATTACK_CD = 0.3
   # enemies fall slower than the player to make midair combos easier
   ENEMY_MAX_FALL_SPEED = 2
   
   FOOTBALL_FAN_MOVEMENT_SPEED = 3
   FOOTBALL_FAN_ATTACK_RANGE = 1
   FOOTBALL_FAN_ATTACK_DURATION = 0.3
   FOOTBALL_FAN_ATTACK_CD = 0.7
   FOOTBALL_FAN_HP = 5

   GENT_MOVEMENT_SPEED = 2
   GENT_ATTACK_RANGE = 1
   GENT_ATTACK_DURATION = 0.6
   GENT_ATTACK_CD = 1 
   GENT_HP = 5

   BOSS_HP = 30 
   BOSS_MOVEMENT_SPEED = 2
   BOSS_MELEE_ATTACK_RANGE = 3
   BOSS_MELEE_ATTACK_CD = 3
   BOSS_MELEE_ATTACK_DURATION = 2
   BOSS_RANGED_ATTACK_CD = 6
   BOSS_RANGED_ATTACK_RANGED_AMOUNT = 3
   BOSS_RANGED_ATTACK_INTERVAL = 2
   
   QUEEN_HP = 40
   QUEEN_MOVEMENT_SPEED = 3
   QUEEN_MELEE_ATTACK_RANGE = 1
   QUEEN_MELEE_ATTACK_CD = 1
   QUEEN_MELEE_ATTACK_DURATION = 2
   QUEEN_RANGED_ATTACK_CD = 2
   QUEEN_RANGED_ATTACK_RANGED_AMOUNT = 10
   QUEEN_RANGED_ATTACK_INTERVAL = 2
   
   CAN_SPEED = 6
   CAN_RANGE = 8
