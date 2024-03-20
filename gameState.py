from direct.fsm.FSM import FSM

class GameFSM(FSM):
    def __init__(self,player,tunnel,carriage,station):#optional because FSM already defines __init__
        #if you do write your own, you *must* call the base __init__ :
        FSM.__init__(self, 'GameFSM')
        self.player = player
        self.tunnel = tunnel
        self.carriage = carriage
        self.station = station

    def enterDrive(self):
        
        self.player.board()
        self.tunnel.start()
        self.carriage.startEnemies()
        

    def exitDrive(self):
        self.carriage.stopEnemies()
        self.tunnel.stop()

    def enterStation(self):
        print("Enter Station")
        self.station.arrive()
        self.carriage.leave()
        self.player.offboard()
        self.station.startBoss()
        
    def exitStation(self):
        self.carriage.arrive()
        self.station.stopBoss()
        self.station.leave()

