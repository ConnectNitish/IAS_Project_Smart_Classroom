import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import sys
import json
import os, uuid
import socket
import requests
from confluent_kafka import Producer, Consumer, KafkaError

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

global kafka_IP_plus_port
global runtime_application_ip_port
global repository_ip_port

kafka_IP_plus_port = None
runtime_application_ip_port = None
repository_ip_port = None

repository_URL = "http://"+sys.argv[1]

module_port_int = 8100
module_name_id_map = {}
module_name_port_map = {}
module_name_id_map_filepath = os.getcwd()+"/runtime/module_name_id_map.json"
module_name_port_map_filepath = os.getcwd()+"/runtime/module_name_port_map.json"
docker_filepath_prefix = os.getcwd()+"/runtime/docker_images/"
algo_filepath_prefix = os.getcwd()+"/runtime/algorithm/"
container_algo_path = os.getcwd()+"/runtime/container_algo.json"
container_algorithm_mapping_path = os.getcwd()+"/runtime/container_algorithm_mapping.json"
algo_base_port = "3500"

def get_free_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

def save_data(filename,data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)

def load_data(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data

@app.route('/')
def landingPage():
    return "You are at Runtime module"

@app.route('/start/<module_name>', methods=['GET'])
def start_module(module_name):
    response = {}
    try:
        module_port = get_free_port()
        
        module_name_port_map = load_data(module_name_port_map_filepath)
        module_port_int = module_name_port_map[module_name]
        
        print("module_port: ",module_port)
        print("module_port_int: ",module_port_int)

        runtime_application_ip,runtime_application_port = get_ip_and_port(runtime_application_ip_port)
        response["service_port"] = str(module_port)
        response["machine_port"] = runtime_application_port
        response["service_ip"] = "0.0.0.0"
        response["machine_ip"] = runtime_application_ip

        repository_ip,repository_port = get_ip_and_port(repository_ip_port)

        os.system("sudo rm {}.tar".format(module_name))
        os.system("wget http://{}:{}/download/{}.tar".format(repository_ip,repository_port,module_name))
        os.system("mv {}.tar {}{}.tar".format(module_name,docker_filepath_prefix,module_name))
        os.system("sudo docker load < {}{}.tar".format(docker_filepath_prefix,module_name))
        os.system("sudo docker run -p {}:{} -d {} > output.txt".format(module_port,module_port_int,module_name))

        container_id = ""

        if os.path.exists('output.txt'):
            fp = open('output.txt', "r")
            container_id = fp.read()
            fp.close()
            os.remove('output.txt')

        print("output: ",container_id)

        if container_id == "" or container_id is None:
            print("Deployment Failed")
            response["status"] = "failure"
            return jsonify(response)

        os.system("sudo docker ps -a")
        print('{} module deployed'.format(module_name))
        
        module_name_id_map[container_id[:20]] = {
        "container_id":container_id,
        "module_name":module_name
        }
        save_data(module_name_id_map_filepath,module_name_id_map)

        response["uid"] = container_id[:20]
        response["status"] = "success"
        return jsonify(response)
    
    except Exception as e:
        print(e)
        response["status"] = "failure"
        return jsonify(response)

@app.route('/stop/<module_name>', methods=['GET'])
def stop_module(module_id):

    try:
        module_name_id_map = load_data(module_name_id_map_filepath)
        container_id = module_name_id_map[module_id]["container_id"]
        module_name_id_map.pop(module_id)
        save_data(module_name_id_map_filepath,module_name_id_map)
        os.system("sudo docker stop {}".format(container_id))
        os.system("sudo docker rm {}".format(container_id))

        if os.path.exists('output.txt'):
            fp = open('output.txt', "r")
            container_id = fp.read()
            fp.close()
            os.remove('output.txt')

        print("output: ",container_id)

        os.system("sudo docker ps -a")
        print('{} module with id {} stoped'.format(module_name,module_id))

        return "success"
    except Exception as e:
        print(e)
        return "failure"

@app.route('/get_data/<sensor_id>')
def get_data_kafka(sensor_id):

    consumer = Consumer({'bootstrap.servers': kafka_IP_plus_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
    consumer.subscribe([sensor_id])
    
    msg = None
    while msg is None:
        msg = consumer.poll(8.0)
        if msg is not None:
            msg = msg.value().decode('utf-8')

        if msg is None:
            print("Message is None")
            time.sleep(2)
            
    consumer.close()

    print("sensor_id {} : message {}".format(sensor_id,msg))
    return jsonify({"sensor_id":sensor_id,"message":msg})

@app.route('/deploy_algorithm/<algo_name>', methods=['GET'])
def deploy_algorithm(algo_name):

    data = load_data(os.getcwd()+"/runtime/container_algo.json")

    if len(data) < 10:
        module_port = get_free_port()
        module_name = "algo_base"

        if os.path.exists('{}{}.tar'.format(docker_filepath_prefix,module_name)) == False:
            repository_ip,repository_port = get_ip_and_port(repository_ip_port)
            os.system("wget http://{}:{}/download_docker_image/{}.tar".format(repository_ip,repository_port,module_name))

        os.system("mv {}.tar {}{}.tar".format(module_name,docker_filepath_prefix,module_name))
        os.system("sudo docker load < {}{}.tar".format(docker_filepath_prefix,module_name))
        os.system("sudo docker run -p {}:{} -d --net=dockernet -v /home/prakashjha/semester4/ias/pr/IAS_Project_Smart_Classroom/Algorithm_Docker:/algo_base {} > output.txt".format(module_port,algo_base_port,module_name))
        
        container_id = ""

        if os.path.exists('output.txt'):
            fp = open('output.txt', "r")
            container_id = fp.read()
            container_id = container_id.strip()
            fp.close()
            os.remove('output.txt')

        print("output: ",container_id)
        
        container_algo_json = load_data(container_algo_path)
        if container_algo_json is None or len(container_algo_json) == 0:
            container_algo_json = {}

        container_algo_json[container_id] = {"algo_list":[],"ip":"0.0.0.0","port":module_port}
        save_data(container_algo_path,container_algo_json)

        container_algorithm_mapping = load_data(container_algorithm_mapping_path)
        if container_algorithm_mapping is None or len(container_algorithm_mapping) == 0:
            container_algorithm_mapping = {}

        container_algorithm_mapping[container_id] = {"algo_list":[]}
        save_data(container_algorithm_mapping_path,container_algorithm_mapping)

    container_algorithm_mapping = load_data(container_algorithm_mapping_path)
    
    min_load = 500
    target_container = None

    for container in container_algorithm_mapping:
        if len(container_algorithm_mapping[container]["algo_list"]) < min_load:
            min_load = len(container_algorithm_mapping[container]["algo_list"])
            target_container = container            

    container_algo_json = load_data(container_algo_path)
    container_algo_json[target_container]["algo_list"].append(algo_name)
    save_data(container_algo_path,container_algo_json)    

    if os.path.exists('{}{}.zip'.format(algo_filepath_prefix,algo_name)) == False:
        repository_ip,repository_port = get_ip_and_port(repository_ip_port)
        os.system("wget http://{}:{}/download_algorithm/{}.zip".format(repository_ip,repository_port,algo_name))
        os.system("mv {}.zip {}{}.zip".format(algo_name,algo_filepath_prefix,algo_name))
        os.system("unzip {}{}.zip -d {}".format(algo_filepath_prefix,algo_name,algo_filepath_prefix))

    os.system("docker exec {} mkdir {}".format(target_container,algo_name))
    os.system("docker cp {}{}/. {}:/algo_base/{}".format(algo_filepath_prefix,algo_name,target_container,algo_name))
    
    return jsonify({"status":"success"})
    

@app.route('/test')
def test():
    return jsonify({"status":"success"})

@app.route('/start', methods=['POST'])
def start_algorithm():

    global repository_ip_port
    global runtime_application_ip_port
    
    reply = {}
    reply["status"] = "failure"
    data = request.json
    algo_name = data["algo_name"]
    params = data["params"]

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(data)

    algo_id = str(uuid.uuid4())
    data = load_data(container_algo_path)
    target_container = None
    for container in data:
        if algo_name in data[container]["algo_list"]:
            target_container = container
    if target_container is not None:
        container_ip = data[target_container]["ip"]
        container_port = data[target_container]["port"]

        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(container_ip,container_port)

        req = {}
        req["algo_name"] = algo_name
        req["params"] = params
        req["repository_ip_port"] = repository_ip_port
        req["runtime_ip_port"] = runtime_application_ip_port

        response = requests.post('http://{}:{}/execute'.format(container_ip,container_port),json=req)
        response = json.loads(response.text)
        process_id = response["process_id"]

        cont_alg = load_data(container_algorithm_mapping_path)
        if target_container not in cont_alg:
            cont_alg[target_container] = {}

        cont_alg[target_container]["algo_list"].append({algo_id:process_id})
        save_data(container_algorithm_mapping_path,cont_alg)
        
        runtime_application_ip,runtime_application_port = get_ip_and_port(runtime_application_ip_port)

        reply["status"] = "success"
        # reply["s"] = response["s"]
        reply["process_id"] = process_id
        reply["container_id"] = target_container
        reply["algo_id"] = algo_id
        reply["runtime_ip"] = runtime_application_ip
        reply["runtime_port"] = runtime_application_port

    return jsonify(reply)

'''
@app.route('/stop/<algo_id>', methods=['GET'])
def stop_algorithm(algo_id):
    data = load_data(container_algorithm_mapping_path)
    process_id = None
    container_id = None
    for key in data:
        if algo_id in data[key]["algo_list"] 
            process_id = data[key]["algo_list"][algo_id]
            container_id = key

    if process_id is not None and container_id is not None:
        container_ip = None
        container_port = None
         
        response = requests.get()
    #find container_id and process_id
    #send kill request to container
    #send boolean
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
    
    global runtime_application_ip_port
    runtime_application_ip_port = get_ip_port("Runtime_Application")
    
    global repository_ip_port
    repository_ip_port = get_ip_port("Repository_Service")

    if __debug__:
        print(" runtime_application_ip_port ",runtime_application_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

if __name__=='__main__':

    get_Server_Configuration()
    runtime_application_ip,runtime_application_port = get_ip_and_port(runtime_application_ip_port)
    kafka_ip,kafka_port = get_ip_and_port(kafka_IP_plus_port)

    if __debug__:
        print(" runtime_application_ip,runtime_application_port ",runtime_application_ip,runtime_application_port)

    app.run(host=runtime_application_ip,debug=True,port=int(runtime_application_port),threaded=True)


'''
container algo json
{
    "container_id": {
        "algo_list":[],
        "ip":"0.0.0.0",
        "port":"3500"   
    }
}

container algorithm mapping
{
    "container_id":{
        "algo_list":[{"algo_id:process_id"}]
    }
}

'''