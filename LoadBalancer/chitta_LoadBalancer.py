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
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from confluent_kafka import Consumer, KafkaError

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

    

    

# @app.route('/getallservers')
# @app.route('/getfreeserver')
# @app.route('/getallservices')
# @app.route('/getservice_ip/<service_name>')
# @app.route('/getserver_stats/<ip>')
# @app.route('/register_service', methods=['POST'])
# @app.route('/unregisterservice', methods=['POST'])
# @app.route('/updateserverstatus', methods=['POST'])
# @app.route('/updateserverutilization', methods=['POST'])


app = Flask(__name__)
@app.route('/')
def index():
    return 'Load balancer'

# @app.route('/get_all_services_from_server/<ip>')
# def get_all_services_from_server():
#     return jsonify(load_balancer.get_all_services_from_server(ip))


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



kafka_ip = sys.argv[1]
ip = sys.argv[2]
port = sys.argv[3]
host_url = ip + ":" + str(port)

print("kafka_ip ",kafka_ip)
print("host_url ",host_url)

load_balancer = LoadBalancer('servers.json', 'services.json')

c = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id': '1', 'auto.offset.reset': 'earliest'})
c.subscribe(['monitor'])

x = threading.Thread(target=updateServerDetails, args=(load_balancer,))
x.start()

if __name__ == '__main__':
    print ('LOAD BALANCER HAS BEEN INITIATED')
    app.run(debug=False, host='0.0.0.0',port=port)
