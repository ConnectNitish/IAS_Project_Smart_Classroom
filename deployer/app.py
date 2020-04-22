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
global scheduler_ip_port

kafka_IP_plus_port = None
Deployment_Service_ip_port = None
Loadbalancer_ip_port = None
scheduler_ip_port = None

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

@app.route('/deploy_algo', methods=['POST'])
def deploy_algo():
    print("algo request at deployer: ")
    data = request.json
    print(data)
    usecase_name = data["function"][0]["usecase_name"]
    #get runtime ip port
    # load_balancer_ip ,load_balancer_port = get_ip_and_port(Loadbalancer_ip_port)
    # lb_response = requests.get('http://{}:{}/get_ip_port'.format(load_balancer_ip,load_balancer_port)).content
    # lb_response = json.loads(lb_response.decode('utf-8'))

    # if lb_response["status"] == "failure":
    #     print("lb failed to provide runtime ip port")
    #     print("UseCase {} deployment failed".format(usecase_name))
    #     return jsonify({"status":"failure"})

    # runtime_ip = lb_response["ip"]
    # runtime_port = lb_response["port"]
    runtime_ip = "0.0.0.0"
    runtime_port = "9000"    
    #get algo_name corresponding to usecase name
    # repo_response = requests.get('{}/get_algo_name/{}'.format(repository_URL,usecase_name)).content
    # repo_response = json.loads(repo_response.decode('utf-8'))    

    # if repo_response["status"] == "failure":
    #     print("repo failed to provide algo name")
    #     print("UseCase {} deployment failed".format(usecase_name))
    #     return jsonify({"status":"failure"})

    # algo_name = repo_response["algo_name"]

    algo_name = "Automated_AC_Service"
    # algo_name = "Illegal_Access_Detection"


    runtime_response = requests.get('http://{}:{}/deploy_algorithm/{}'.format(runtime_ip,runtime_port,algo_name)).content
    runtime_response = json.loads(runtime_response.decode('utf-8'))    

    if runtime_response["status"] == "failure":
        print("Runtime failed to deploy")
        print("Algorithm {} deployment failed".format(algo_name))
        return jsonify({"status":"failure"})

    print("Algorithm {} deployment done successfully".format(algo_name))

    #send all details to scheduler
    data["function"][0]["runtime_ip"] = runtime_ip
    data["function"][0]["runtime_port"] = runtime_port
    data["function"][0]["algo_name"] = algo_name

    print("input to scheduler: ",data)

    # scheduler_ip,scheduler_port = get_ip_and_port(scheduler_ip_port)
    # scheduler_response = requests.post("http://{}:{}/schedule_algo".format(scheduler_ip,scheduler_port),json=data)
    # scheduler_response = json.loads(scheduler_response.text)

    # if scheduler_response["status"] == "failure":
    #     print("Failed to Schedule algo {}".format(algo_name))
    #     return jsonify({"status":"failure"})

    return  jsonify({"status":"success"})
def save_data(filename,data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)
def load_data(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data
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
    
    global scheduler_ip_port
    scheduler_ip_port = get_ip_port("Scheduling_Service")
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
