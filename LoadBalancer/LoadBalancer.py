import os
import sys
import time
import random
import json,requests
from flask import abort
from flask import Flask
from flask import session
from flask import request
from flask import jsonify
from flask import send_file
from flask import redirect, url_for
from flask import render_template

from flask import jsonify
import random
import threading
import time
import sys
from flask import Flask
from flask import session
from flask import redirect, url_for
from flask import render_template
from flask import request
from flask import abort
from class_Service import Service
from class_Server import Server
import json
import os

from class_Service import Service
from class_Server import Server
    


# ---------------- Configuration Section Start
#******************

root_name = "LoadBalancer"

server_config = os.getcwd()+"/"+ root_name +"/servers.json"

#*********** Conflict With New Structure of services.json 
service_config = os.getcwd()+"/"+ root_name +"/services.json"

global kafka_IP_plus_port
global load_balancer_ip_port

kafka_IP_plus_port = None
load_balancer_ip_port = None

repository_URL = "http://"+sys.argv[1]

# ---------------- Configuration Section End


'''
# Team_2_Old_Code
class LoadBalancer:

    
    def __init__(self, server_config, service_config):
        self.servers = {}
        self.services = {}

    def load_data(self):
        with open(service_config, 'r') as fp:
            self.services = json.load(fp)
        print(self.services)

    def save_data(self):
        with open(service_config, 'w') as fp:
            json.dump(self.services, fp, indent=4, sort_keys=True)

'''

class LoadBalancer:

    def __init__(self, server_json, service_json):
        self.servers = {}
        self.services = {}
        self.for_services = self.read_service_json(service_json)
        self.for_servers = self.read_server_json(server_json)
        
    def read_service_json(self, service_json):
        with open(service_json) as ff:
            json_read = json.load(ff)
            print("all servicces are")

            if __debug__:
                print(" Services Details are from service_json ","\n",service_json,"")

            for s_instance in json_read ['services']:
                service_name = s_instance['serviceName']
                instances = s_instance['instances']
                print(service_name)
                print(instances)
                sdetails = {}
                sdetails["serviceName"] = service_name
                sdetails["instances"] = instances
                self.services[service_name] = Service(service_name,instances)
        return True

    def read_server_json(self, server_json):
        with open(server_json) as ff:
            json_read = json.load(ff )
            
            for instance in json_read['servers']:
                ip = instance['serverIP']
                username = instance['username']
                password = instance['password']

                self.servers[ip ] = Server(ip, username, password)
        
        return True

    
    def getAllServers(self):
        retVal = []
        for key in self.servers.keys():
            serverObj = self.servers[key]
            dd = {}
            if serverObj.getStatus() == True:
                dd['ip'] = key
                dd['status'] = serverObj.getStatus()
                dd['cpu'] = serverObj.getcpu()
                dd['ram'] = serverObj.getram()
                retVal.append(dd)
        return retVal

    def getFreeServer(self):
        demoThreshold = 9999
        retVal_sname = ''
        server_obj = ''
        for server_name in self.servers:
            server = self.servers[server_name]
            
            if server.getcpu() < demoThreshold:
                retVal_sname = server.getServerIP()
                server_obj = server
                demoThreshold = server.getcpu()

        retVal = {}
        server_obj = self.servers[retVal_sname]
        retVal['ip'] = retVal_sname
        retVal['username'] = server_obj.getUsername()
        retVal['password'] = server_obj.getPassword()
        return retVal

    

    def getAllServices(self):
        retVal = {}
        retVal['services'] = []
        for service in self.services:
            services_data = {}
            services_data['serviceName'] = self.services[service].getServiceName()
            services_data['instances'] = self.services[service].getAllRunningInstances()
            retVal['services'].append(services_data)
            print("services_data",services_data)
        print(self.services)
        return retVal

    # def get_all_services_from_server(self,ip):
    #     server_obj = self.servers[ip]
    #     print(server_obj.getAllServicesRunning())
    #     return server_obj.getAllServicesRunning()

    def get_ip_for_service(self, serviceName):
        if serviceName not in self.services:
            return "Unkown service..... Please register"
        instances = self.services[serviceName].getAllRunningInstances()
        print("INSIDE  get_ip_for_service")
        print (instances)
        demoThreshold = 99999
        temp_inst = ''
        for instance in instances:
            ip = instance["serverIP"]
            server_obj = self.servers[ip]
            if server_obj.getcpu() < demoThreshold:
                temp_inst = instance
        instance = temp_inst
        print ('Instance:', instance["serverIP"])
        server = self.servers[instance["serverIP"]]
        retVal = {  }
        retVal['username'] = server.getUsername()
        retVal['password'] = server.getPassword()
        retVal['ip'] = server.getServerIP()
        return retVal

    def getServerDetails(self, ip):
        retVal = {}
        retVal['cpu'] = self.servers[ip].getcpu()
        retVal['ram'] = self.servers[ip].getram()
        return retVal

    def updateServerUtilization(self, serverIP, ram, cpu):
        self.servers[serverIP].updateServerUtilization(ram, cpu) 

    def updateServerStatus(self, s_ip, status):
        self.servers[s_ip].updateStatus(status)

    def registerService(self, serviceName, s_ip, s_port):
        if serviceName in self.services:
            service = self.services[serviceName]
            status = service.addInstance(s_ip,s_port)
            self.servers[str(s_ip)+":"+str(s_port)].addService(serviceName)
        else:
            inst = []
            inst.append(str(s_ip)+":"+str(s_port))
            service_obj = Service(serviceName,inst)
            self.services[serviceName] = service_obj
            self.servers[str(s_ip)+":"+str(s_port)].addService(serviceName)
    
    
    def unregisterService(self, serviceName, s_ip, s_port):
        s_url = str(s_ip)+":"+str(s_port)
        server = self.servers[s_url]
        self.services[serviceName].deleteInstance(s_ip, s_port )
        if len(self.services[serviceName].getAllRunningInstances() ) == 0:
            del self.services[serviceName]
        self.servers[s_url].removeService(serviceName)



# Initialising Load Balancer and Flask

app = Flask(__name__)

#*********** Need to Check Whther Currently Used or Not 
app.deployment_file_location = 'deployment/to_deploy_folder'
load_balancer = LoadBalancer(server_config, service_config)

# -------------------------------- New Code Rest API Chitta 
@app.route('/')
def index():
    return 'Load balancer'

@app.route('/get_all_servers')
def get_all_servers():
    return jsonify(load_balancer.getAllServers())

@app.route('/get_free_server')
def get_free_server():
    return json.dumps(load_balancer.getFreeServer() ) 

@app.route('/get_all_services')
def get_all_services():
    return jsonify(load_balancer.getAllServices())


@app.route('/get_service_ip/<service_name>')
def get_service_ip(service_name):
    return jsonify( load_balancer.get_ip_for_service(service_name) )

@app.route('/get_server_stats/<ip>')
def get_server_stats(ip):
    return jsonify( load_balancer.getServerDetails(ip) )


@app.route('/update_server_status', methods=['POST'])
def update_server_status():
    if request.method =='POST':
        print ('Inside post')
        data = request.json
        print (data)
        ip = data['IP']
        val = data['status']
        load_balancer.updateServerStatus( ip, val)
    return jsonify('{"Message":"UnRegistered successfully"')

@app.route('/update_server_utilization', methods=['POST'])
def update_server_utilization():
    # my_logger.debug('LoadBalancer \t update_server_utilization ' + str(request.json) )

    print ('Inside update')
    if request.method =='POST':
        print ('Inside post')
        data = request.json
        ip = data['LocalIP']
        print (ip)
        ram = data['ram_USAGE']
        print (ram)
        cpu = data['cpu']
        load_balancer.updateServerUtilization(ip, ram, cpu)
    return jsonify('{"Message":"Updated successfully"')

@app.route('/register_service', methods=['POST'])
def register_service():
    if request.method =='POST':
        print ('Inside post')
        data = request.json
        print (data)
        ip = data['ip']
        port = data['port']
        serviceName = data['serviceName']
        load_balancer.registerService( serviceName , ip , port)
    return jsonify('{"Message":"Registered successfully"')

@app.route('/get_unregister_service/<service_data>')
def get_unregister_service(service_data):
    serviceName, ip, port = service_data.split(";")
    load_balancer.unregisterService( serviceName , ip , port)
    return jsonify('{"Message":"UnRegistered successfully"')

@app.route('/unregister_service', methods=['POST'])
def unregister_service():
    if request.method =='POST':
        print ('Inside post')
        data = request.json
        print (data)
        print (type(data))
        ip = data['ip']
        port = data['port']
        serviceName = data['serviceName']
        load_balancer.unregisterService( serviceName , ip , port)
    return jsonify('{"Message":"UnRegistered successfully"')

def updateServerDetails(obj):
    while True:
        stats = c.poll(1.0)

        if stats is None:
            continue
        if stats.error():
            print("Consumer error: {}".format(stats.error()))
            continue

        data= json.loads(stats.value().decode('utf-8'))
        ip = data["1"]["server_ip"]
        cpu_used = data["1"]["cpu_utilization"]
        ram_used = data["1"]["used_memory"]
        print(ip,cpu_used,ram_used)
        obj.updateServerUtilization(ip,ram_used,cpu_used)
        # print('Received message: {}'.format(data))


# ------------------------------- New Code Rest API End

# Team_2_Old_Code
@app.route('/register/<module_name>/<machine_ip>/<service_ip>/<service_port>/<machine_port>/<uid>')
def register_services(module_name,machine_ip,service_ip,service_port,machine_port,uid):
    
    print(load_balancer.services)
    try:
        load_balancer.load_data()
        load_balancer.services[uid] = {
        "uid":uid,
        "module_name":module_name,
        "service_ip":service_ip,
        "service_port":service_port,
        "machine_ip":machine_ip,
        "machine_port":machine_port
        }
        print(load_balancer.services)
        load_balancer.save_data()
        return "success"
    except Exception as e:
        print("Error in register_services: ",e)
        return "failure"

#*********** Conflict With New Code 
'''
@app.route('/get_all_services')
def get_all_services():
    load_balancer.load_data()
    return jsonify(load_balancer.services)
'''

def get_ip_port(module_name):
    custom_URL = repository_URL+"/get_running_ip/"+module_name
    r=requests.get(url=custom_URL).content
    r = r.decode('utf-8')
    print(r)
    return r

def get_Server_Configuration():
    global kafka_IP_plus_port 
    kafka_IP_plus_port = get_ip_port("Kafka_Service")

    if __debug__:
        print(" Kafka IP and Port",kafka_IP_plus_port)
    
    global load_balancer_ip_port
    load_balancer_ip_port = get_ip_port("LoadBalancer_Service")
    
    if __debug__:
        print(" load_balancer_ip_port ",load_balancer_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

def spawn_function():

    if __debug__:
        print( " Obtained Kafka IP port ")
        print(kafka_IP_plus_port)

    c = Consumer({'bootstrap.servers': kafka_IP_plus_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
    c.subscribe(['monitor'])

    x = threading.Thread(target=updateServerDetails, args=(load_balancer,))
    x.start()

if __name__ == '__main__':

    print (' Initiating Load Balancer ')
    get_Server_Configuration()
    lb_ip,lb_port = get_ip_and_port(load_balancer_ip_port)

    if __debug__:
        print("lb_ip,lb_port",lb_ip,lb_port)

    app.run(debug=True, host=lb_ip,port=int(lb_port),threaded=True)
