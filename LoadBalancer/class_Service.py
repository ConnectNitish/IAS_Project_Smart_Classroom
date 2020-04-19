class Service:

    def __init__(self, service_name,service_instances):
        self.serviceName = service_name
        self.serviceInstances = service_instances
        
    def addInstance(self, s_ip, s_port):
        temp = {}
        url = s_ip + ":" + str(s_port)
        if url in self.serviceInstances:
            return False
        temp["serverID"] = "3"
        temp["serverIP"] = url
        self.serviceInstances.append(temp)
        return True

    def deleteInstance(self, s_ip, s_port):
        temp = {}
        url = s_ip + ":" + str(s_port)
        temp["serverID"] = "3"
        temp["serverIP"] = url
        self.serviceInstances.remove(temp)

    def getServiceName(self):
        return self.serviceName

    def getAllRunningInstances(self):
        return self.serviceInstances
    
    
