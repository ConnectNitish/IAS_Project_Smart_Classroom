import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys,os
import json

load_balancer_ip = "127.0.0.1"
load_balancer_port = "7000"

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)
app.registry_config_file = "initiate_server.json"


class Registry:

    def read_registry_config(self, file_location):
        service_ip_address = {}

        with open(file_location) as f:
            data = json.load(f )

            print(data)
            
            for instance in data.items():
                print(instance)
                service_ip_address[instance[0]] = instance[1]
        
        return service_ip_address

    def __init__(self,registry_file):
        # print(os.getcwd())
        path = os.getcwd() + "/" + registry_file
        self.service_ip_address = self.read_registry_config(path)

@app.route('/')
def landingPage():
    return "You are at Repository module"

@app.route('/start/<ip>/<port>/<module_name>', methods=['GET'])
def start_service(ip,port,module_name):

    try:
        print(module_name,ip,port)
        reponse = requests.get('http://{}:{}/start/{}'.format(ip,port,module_name)).content
        reponse = json.loads(reponse.decode('utf-8'))

        if reponse["status"] == "success":
            reponse["status"] = requests.get('http://{}:{}/register/{}/{}/{}'.
                format(load_balancer_ip,load_balancer_port,module_name,ip,response["port"])).content.decode("utf-8")

        return reponse["status"]
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

@app.route('/get_running_ip/<module>',methods=['GET'])
def get_running_ip(module):
    service_details_ip = None
    try:
        service_details_ip = registry_object.service_ip_address[module]
    except KeyError:
        service_details_ip = None
    return service_details_ip

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = app.root_path + "/download/" + filename
    # print(uploads)
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_file(uploads, as_attachment=True)

global kafka_IP_plus_port
global repository_ip_port

def get_Server_Configuration():
    global kafka_IP_plus_port 
    kafka_IP_plus_port = get_running_ip("Kafka_Service")

    if __debug__:
        print(" Kafka IP and Port",kafka_IP_plus_port)
    
    global repository_ip_port
    repository_ip_port = get_running_ip("Repository_Service")
    
    if __debug__:
        print(" repository_ip_port ",repository_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

registry_object = Registry(app.registry_config_file)

if __name__=='__main__':
    get_Server_Configuration()
    repository_ip,repository_port = get_ip_and_port(repository_ip_port)

    if __debug__:
        print(" repository_ip,repository_port ",repository_ip,repository_port)

    app.run(host=repository_ip,debug=False,port=int(repository_port),threaded=True)
