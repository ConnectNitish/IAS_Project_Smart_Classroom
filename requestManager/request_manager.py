from flask import Flask,request, render_template,redirect,url_for,session,jsonify
from werkzeug.utils import secure_filename
import os,json
from threading import Thread
from time import sleep
import time
import datetime
import requests
import numpy
from Logger import Logger
import logging
import xmltodict
import sys
from kafka_helper import kafka_api
from liveSensorDataDisplay_helper import getData

kafka_api_obj = kafka_api()

homepath=os.path.expanduser("~")
UPLOAD_FOLDER = homepath+"/nfs/"
ALLOWED_EXTENSIONS = set(['txt', 'json', 'png', 'jpg', 'jpeg', 'gif', 'zip'])
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

global kafka_IP_plus_port
global request_manager_ip_port
global deployment_ip_port

kafka_IP_plus_port = None
request_manager_ip_port = None
deployment_ip_port = None

app.deployment_file_location = 'deployment/to_deploy_folder'
repository_URL = "http://"+sys.argv[1]

scheduler_template_file = os.getcwd() + "/Algorithm.scheduler_config.json"
@app.route('/')
def landingPage():
    return render_template('index.html')
	
def prepare_and_send_log_message(topic_name,key,value,kafka_IP_plus_port):
    kafka_api_obj.produce_topic(topic_name,key,value,kafka_IP_plus_port)

@app.route('/Live_sensor_data')
def live_sensor_data():
    # print(os.getcwd())
    all_sensor_info = requests.get(repository_URL+"/get_all_sensor_info").content
    all_sensor_info = json.loads(all_sensor_info.decode('utf-8'))

    all_sensor_config = requests.get(repository_URL+"/get_all_sensor_config").content
    all_sensor_config = json.loads(all_sensor_config.decode('utf-8'))
    data = getData(all_sensor_info,all_sensor_config)
    return render_template('showSensorData.html',data = data)

@app.route('/Deployment_Interface')
def Deployment_Interface():
    is_deployment_done = False
    response = {}
    response["deployment_done"] = is_deployment_done
    print(response)
    print('Logging Request to Logger**')
    prepare_and_send_log_message("Request_Manager","Deployment_Interface_warning","Deployment Service is up",kafka_IP_plus_port)
    return render_template('Deployment_Interface.html',data=response)

@app.route('/Live_Service_Instances')
def getServiceInstancesDetails():
    
    load_balancer_ip_port = get_ip_port("LoadBalancer_Service")
    response=requests.get(url="http://"+load_balancer_ip_port+"/get_all_services").content
    response = json.loads(response.decode('utf-8'))
    return render_template('Service_Instances.html',data=response)

@app.route('/Start_Deployment',methods=['GET','POST'])
def add_deployment_details():

    is_deployment_done = False

    key_IP_Address = 'IP_Address'
    key_port_number = 'port_number'
    key_service_type = 'service_type'

    input_IP_Address = request.form[key_IP_Address]
    input_port_number = request.form[key_port_number]
    input_service_type = request.form.get(key_service_type)

    response = {}

    response[key_IP_Address] = input_IP_Address
    response[key_port_number] = input_port_number
    response[key_service_type] = input_service_type

    url_path_counter = app.deployment_file_location + "/to_deploy_file_Counter.txt"
    request_number = None
    # try:
    #     with open(url_path_counter, 'r') as fp:
    #         request_number = int(fp.read())
    # except FileNotFoundError:
    #     print("File Not Found")
    #     request_number = 0
    #     pass

    # url_path = app.deployment_file_location + "/to_deploy_file_"+ str(request_number + 1) +".json"
    # with open(url_path, 'a+') as fp:
    #     json.dump(response, fp)

    # with open(url_path_counter, 'w') as fp:
    #     fp.write(str(request_number + 1))

    deployment_ip,deployment_port = get_ip_and_port(deployment_ip_port)
    # print(deployment_ip,deployment_port)
    deployment_response = requests.get('http://{}:{}/start/{}/{}/{}'.
        format(deployment_ip,deployment_port,input_IP_Address,input_port_number,input_service_type)).content.decode("utf-8")

    # print(deployment_response)

    if deployment_response == "success":
        is_deployment_done = True
    else:
        is_deployment_done = False

    response["deployment_done"] = is_deployment_done

    print('Logging Request to Logger For Success Deployment')
    prepare_and_send_log_message("Request_Manager","Start_Deployment_info",response,kafka_IP_plus_port)

    print(response)

    return render_template('Deployment_Interface.html',data=response)

@app.route('/Scheduler_Invocation',methods=['GET','POST'])
def displaySchedulerDetails():
    return render_template('Scheduler_Invocation.html')

@app.route('/Scheduler_Module_Invocation',methods=['GET','POST'])
def invoke_scheduler():
    result = ''
    if request.method == 'POST':
        result = request.form
    print(result)
    print(result["app_name"])
    appn = "pre_cool_classroom"
    appn = "turn_off_lights"
    appn = result["app_name"]
    datatosend = {}
    datatosend['appName'] = appn

    url_schedule_service = "http://0.0.0.0:9942/ScheduleService"

    lcl_scheduler_service_ip_port = get_ip_port("Scheduling_Service")

    url_schedule_service = lcl_scheduler_service_ip_port

    url_schedule_service = "http://"+url_schedule_service+"/ScheduleService"

    if __debug__:
        print(" Final Scheduler Service URL  ",url_schedule_service,"")

    r=requests.post(url=url_schedule_service,json=datatosend)

    print("msg to sc ",url_schedule_service)
    
    return render_template('Scheduler_Invocation_Success.html')

@app.route('/Class_Room_Information',methods=['GET','POST'])
def get_class_room_information():

    lcl_entire_data = requests.get(repository_URL+"/get_location_info").content
    lcl_entire_data = json.loads(lcl_entire_data.decode('utf-8'))

    response  = {}

    lst_response = []

    for key,value in lcl_entire_data.items():

        for key_1,value_1 in lcl_entire_data[key].items():

            if key_1 in "Temperature" or key_1 in "Access":

                temp_list = []
                temp_list.append(str(key))
                temp_list.append(str(key_1))
                temp_list.append(lcl_entire_data[key][key_1]['status'])
                temp_list.append(lcl_entire_data[key][key_1]['last-modified'])

                if len(temp_list)>0:
                    lst_response.append(temp_list)

    response["RoomDetails"] = lst_response

    return render_template("Class_Room_Information.html",data=response)

@app.route('/Service_Execution',methods=['GET','POST'])
def get_use_case_entry_point():

    lcl_entire_data = requests.get(repository_URL+"/get_location_info").content
    lcl_entire_data = json.loads(lcl_entire_data.decode('utf-8'))
    lcl_use_case_mapping = requests.get(repository_URL+"/get_use_case_mapping").content
    lcl_use_case_mapping = json.loads(lcl_use_case_mapping.decode('utf-8'))

    response  = {}
    response["Algorithm_Details"] = lcl_use_case_mapping.items()
    response["RoomDetails"] = lcl_entire_data.keys()

    return render_template('Service_Execution.html',data=response)

@app.route('/Service_Execution_Interface',methods=['GET','POST'])
def execute_use_case():
    f = request.files['file']
    file_path = os.getcwd() + "/requestManager/" + f.filename
    f.save(file_path)
    
    print(" File Name ",file_path)

    data = load_data(file_path)
    
    deployer_ip,deployer_port = get_ip_and_port(deployment_ip_port)
    deployer_response = requests.post("http://{}:{}/deploy_algo".format(deployer_ip,deployer_port),json=data)
    deployer_response = json.loads(deployer_response.text)

    if deployer_response["status"] == "failure":
        return render_template('Scheduler_Invocation_Failure.html')

    return render_template('Scheduler_Invocation_Success.html')
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
    
    global request_manager_ip_port
    request_manager_ip_port = get_ip_port("Request_Manager_Application")

    global deployment_ip_port
    deployment_ip_port = get_ip_port("Deployment_Service")
    
    if __debug__:
        print(" request_manager_ip_port ",request_manager_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

if __name__ == '__main__':
    get_Server_Configuration()
    request_ip,request_port = get_ip_and_port(request_manager_ip_port)

    if __debug__:
        print("Request Manager IP Port ",request_ip,request_port)

    app.run(host=request_ip,port=int(request_port),debug=True,threaded=True)

