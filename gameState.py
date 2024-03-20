from direct.fsm.FSM import FSM

class GameFSM(FSM):
    def __init__(self,player,map,carriage):#optional because FSM already defines __init__
        #if you do write your own, you *must* call the base __init__ :
        FSM.__init__(self, 'GameFSM')
        self.player = player
        self.map = map
        self.carriage = carriage
       

    def enterDrive(self):
        
        self.player.board()
        #self.carriage.startEnemies()
        

    def exitDrive(self):
        #self.carriage.stopEnemies()
        self.map.enterStation()

    def enterStation(self):
        print("Enter Station")
        
        
        #self.player.offboard()
        #self.station.startBoss()
        
    def exitStation(self):
        self.carriage.arrive()
        #self.map.leaveStation()
        #self.station.stopBoss()
        #self.station.leave()

