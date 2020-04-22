import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json
import time

from Email import *

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

device_data_file = "Location_Device_Information.json"

global kafka_IP_plus_port
global app_notification_ip_port

kafka_IP_plus_port = None
app_notification_ip_port = None

repository_URL = "http://"+sys.argv[1]
@app.route('/')
def landingPage():
    return "You are at Action Notification module"

def load_data(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    # device_file_name = json.dumps(device_file_name)
    return data

def save_data(device_file_name,data):
    with open(device_file_name, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)


@app.route('/start_device/<location>/<device>/<status>')
def change_status_of_device(location,device,status):

    repo_response = requests.get(repository_URL+"/update_sensor_status/{}/{}/{}".format(location,device,status)).content
    repo_response = json.loads(repo_response.decode('utf-8'))

    return repo_response


path_for_configuration_file = os.getcwd()+"/Repository/Scheduler_Config_file"

@app.route('/send_email/<message>')
def send_email(message):

    lcl_dict_message = eval(message)

    if __debug__:
        print(" message to Send Email Dict ")
        print(lcl_dict_message,"")
        print(type(lcl_dict_message),"")
        print(" message to Send Email Text ")
        print(lcl_dict_message,"")
        print(type(lcl_dict_message),"")

    try:
        lcl_data = {}

        lcl_data['location'] = lcl_dict_message['location']
        lcl_data['time_stamp'] = lcl_dict_message['time_stamp']
        lcl_data['status'] = lcl_dict_message['status']
        lcl_algorithm_name = lcl_dict_message['algorithm']

        lcl_path_of_scheduler_config = path_for_configuration_file + \
                                        "/" + lcl_algorithm_name + \
                                        ".scheduler_config.json"

        if __debug__:
            print(" Path of Scheduler Config ")
            print( lcl_path_of_scheduler_config,"" )

        lcl_load_data_from_scheduler_file = \
                    get_device_info_for_room(lcl_path_of_scheduler_config)

        try:

            if lcl_load_data_from_scheduler_file['function'][0]['email_address'] != "":
                lcl_data['to_email_id'] =  \
                    lcl_load_data_from_scheduler_file['function'][0]['email_address']

        except:
                lcl_data['to_email_id'] = "self"
                lcl_data['status'] = "Error in Configuration file"

        if __debug__:
            print( " Final Email Data To Send ")
            print(lcl_data,"")

        sendemail_via_gmail(lcl_data)

    except:
        return "Problem In Sending Email"

    return "Mail Sent Successfully"



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
    
    global app_notification_ip_port
    app_notification_ip_port = get_ip_port("App_Notification_Service")
    
    if __debug__:
        print(" app_notification_ip_port ",app_notification_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

if __name__ == '__main__':

    print (' Initiating App Notification ')
    get_Server_Configuration()
    app_ip,app_port = get_ip_and_port(app_notification_ip_port)

    if __debug__:
        print("app_ip,app_port",app_ip,app_port)

    app.run(debug=True, host=app_ip,port=int(app_port),threaded=True)
