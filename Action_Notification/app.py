import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json

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

@app.route('/')
def landingPage():
    return "You are at Action Notification module"

def get_device_info_for_room(device_file_name):
    with open(device_file_name, 'r') as fp:
        device_file_name = json.load(fp)
    # device_file_name = json.dumps(device_file_name)
    return device_file_name

def save_data(device_file_name,data):
    with open(device_file_name, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)

@app.route('/start_device/<location>/<device>/<status>')
def change_status_of_device(location,device,status):

	lcl_get_device_info_for_room = get_device_info_for_room(device_data_file)

	if __debug__:
		print(lcl_get_device_info_for_room)

	lcl_get_device_info_for_room[location][device]["status"] = status

	save_data(device_data_file,lcl_get_device_info_for_room)

	return "Success"

repository_URL = "http://"+sys.argv[1]

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
