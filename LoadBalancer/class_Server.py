class Server:
    ID = 0
    def __init__(self, serverIP, username, password):
        self.serverID = Server.ID + 1
        self.serverIP = serverIP
        self.username = username
        self.password = password
        self.ram = 4096
        self.cpu = 50
        self.isUp = True
        self.listServicesRunning = []
        Server.ID += 1
    
    def updateStatus(self, param):
        self.isUp = param

    def getAllServicesRunning(self):
        return self.listServicesRunning

    def addService(self, serviceName):
        self.listServicesRunning.append(serviceName)

    def removeService(self, serviceName):
        print ("Before removing all running services are :", self.listServicesRunning)
        self.listServicesRunning.remove(serviceName)
        print (self.listServicesRunning)
        print ( serviceName ," is removed")

    def updateServerUtilization(self, ram, cpu):
        self.ram = ram
        self.cpu = cpu

    def getram(self):
        return self.ram
    
    def getcpu(self):
        return self.cpu

    def getUsername(self):
        return self.username

    def getStatus(self):
        return self.isUp

    def getPassword(self):
        return self.password

    def getServerIP(self):
        return self.serverIP
    