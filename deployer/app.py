import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

global kafka_IP_plus_port
global Deployment_Service_ip_port
global Loadbalancer_ip_port

kafka_IP_plus_port = None
Deployment_Service_ip_port = None
Loadbalancer_ip_port = None

repository_URL = "http://"+sys.argv[1]

@app.route('/')
def landingPage():
    return "You are at Deployer module"

@app.route('/start/<ip>/<port>/<module_name>', methods=['GET'])
def start_service(ip,port,module_name):

    try:
        print(module_name,ip,port)
        response = requests.get('http://{}:{}/start/{}'.format(ip,port,module_name)).content
        response = json.loads(response.decode('utf-8'))

        load_balancer_ip ,load_balancer_port = get_ip_and_port(Loadbalancer_ip_port)
        
        if response["status"] == "success":
            response["status"] = requests.get('http://{}:{}/register/{}/{}/{}/{}/{}/{}'.
                format(load_balancer_ip,load_balancer_port,module_name,ip,response["service_ip"],
                       response["service_port"],response["machine_port"],response["uid"])).content.decode("utf-8")
            print("inside: ",response)

        return response["status"]
    except Exception as e:
        print(e)
        return "failure"


@app.route('/stop/<ip>/<port>/<module_name>', methods=['GET'])
def stop_service(ip,port,module_name):
    try:
        print(module_name,ip,port)
        return requests.get('http://{}:{}/stop/{}'.format(ip,port,module_name)).content.decode("utf-8")
    except Exception as e:
        print(e)
        return "failure"

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
    
    global Deployment_Service_ip_port
    Deployment_Service_ip_port = get_ip_port("Deployment_Service")

    global Loadbalancer_ip_port
    Loadbalancer_ip_port = get_ip_port("LoadBalancer_Service")
    
    if __debug__:
        print(" Deployment_Service_ip_port ",Deployment_Service_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

if __name__ == '__main__':

    print (' Initiating Deployer ')
    get_Server_Configuration()
    Deployment_Service_ip,Deployment_Service_port = get_ip_and_port(Deployment_Service_ip_port)

    if __debug__:
        print("Deployment_Service_ip,Deployment_Service_port",Deployment_Service_ip,Deployment_Service_port)

    app.run(host=Deployment_Service_ip,debug=True,port=int(Deployment_Service_port),threaded=True)
