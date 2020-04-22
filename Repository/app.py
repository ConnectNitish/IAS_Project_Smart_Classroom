import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys,time
import json


app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)
app.registry_config_file = "initiate_server.json"

global kafka_IP_plus_port
global repository_ip_port

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

registry_object = Registry(app.registry_config_file)
@app.route('/')
def landingPage():
    return "You are at Repository module"
@app.route('/get_algo_name/<usecase_name>')
def get_algo_name(usecase_name):
    filename = os.getcwd() + "/Repository/Use_Case_Mapping.json"
    data = load_data(filename)
    algo_name = ""
    if usecase_name in data:
        algo_name = data[usecase_name]
    reply = {} 
    if algo_name == "":
        reply["status"] = "failure"
    else:
        reply["status"] = "success"
    reply["algo_name"] = algo_name
    return jsonify(reply)
@app.route('/get_manifest/<algo_name>')
def get_manifest(algo_name):
    filename = os.getcwd() + "/Repository/algorithm_repository/algorithm_manifest.json"
    data = load_data(filename)
    reply = data[algo_name]
    print(reply)
    return jsonify(reply)

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

@app.route('/download_docker_image/<filename>')
def download_docker_image(filename):
    filepath = os.getcwd() + "/Repository/docker_repository/" + filename
    return send_file(filepath, as_attachment=True)
@app.route('/download_algorithm/<filename>')
def download_algorithm(filename):
    filepath = os.getcwd() + "/Repository/algorithm_repository/" + filename
    return send_file(filepath, as_attachment=True)
@app.route('/get_room_details/<room_id>')
def get_room_details(room_id):
    filepath = os.getcwd() + "/Repository/Sensor_data.json"
    data = load_data(filepath)
    reply = data[room_id]
    return jsonify(reply)
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
@app.route('/update_sensor_status/<location>/<device>/<status>')
def update_sensor_status(location,device,status):
    filename = os.getcwd()+"/Repository/Location_Device_Information.json"
    data = load_data(filename)
    data[location][device]["status"] = status
    data[location][device]["last-modified"] = time.strftime("%A, %d %B %Y %I:%M%p")
    save_data(filename,data)

    return jsonify({"status":"success"})

@app.route('/get_all_sensor_info')
def get_all_sensor_info():
    filename = os.getcwd() + "/Repository/Sensor_data.json"
    data = load_data(filename)
    return jsonify(data)

@app.route('/get_all_sensor_config')
def get_all_sensor_config():
    filename = os.getcwd() + "/Repository/Sensor_Specific_Data.json"
    data = load_data(filename)
    return jsonify(data)
@app.route('/get_location_info')
def get_location_info():
    filename = os.getcwd() + "/Repository/Location_Device_Information.json"
    data = load_data(filename)
    return jsonify(data)
@app.route('/get_use_case_mapping')
def get_use_case_mapping():
    filename = os.getcwd() + "/Repository/Use_Case_Mapping.json"
    data = load_data(filename)
    return data
def save_data(filename,data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)
def load_data(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data

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



if __name__=='__main__':
    get_Server_Configuration()
    repository_ip,repository_port = get_ip_and_port(repository_ip_port)

    if __debug__:
        print(" repository_ip,repository_port ",repository_ip,repository_port)

    app.run(host=repository_ip,debug=True,port=int(repository_port),threaded=True)
