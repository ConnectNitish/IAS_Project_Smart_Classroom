import socket                
import threading
import sys
import os
import json
import random
import datetime
import time,requests

debug_AC_Service = True
global repository_URL
global app_notification_ip_port

def save_data(filename,data):
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)

def load_data(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data

def get_ip_port(module_name):
    global repository_URL
    custom_URL = repository_URL+"get_running_ip/"+module_name
    response=requests.get(url=custom_URL).content
    response = response.decode('utf-8')
    return response

def get_Server_Configuration():

    global app_notification_ip_port
    port = get_ip_port("App_Notification_Service").split(":")[1]
    app_notification_ip_port = "192.168.0.1:"+port
    
    if __debug__:
        print(" app_notification_ip_port ",app_notification_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]

def update_status(location,device,status):
    global app_notification_ip_port
    get_app_notification_Url = app_notification_ip_port

    if __debug__:
        print(" Obtained URL of App Notfication Service ")
        print(get_app_notification_Url)

    notification_URL = "http://"+get_app_notification_Url+"/"

    custom_URL = notification_URL+"start_device/"+location+"/" + device + "/" + status

    if __debug__:
        print(" Obtained full URL of App Notfication Service ")
        print(custom_URL)

    
    r=requests.get(url=custom_URL).content
    r = r.decode('utf-8')
    # print(r)
    return r

def perform_automate_AC_service(room_no,sensor_type,runtime_ip_port):

    global repository_URL

    get_Server_Configuration()

    lcl_room_to_precool = room_no
    lcl_sensor_type = sensor_type

    temp_value = 0.0
    count_of_sensor = 0

    room_sensors = requests.get(repository_URL+"get_room_details/{}".format(lcl_room_to_precool)).content
    room_sensors = json.loads(room_sensors.decode('utf-8'))

    for item,value in room_sensors.items():
         

        if __debug__ or debug_AC_Service:
            print(" ---- Value of Particular Room  ")
            print(item,"",value,"")

        lcl_get_location_of_sensor_from_config =room_sensors[item]["socket"]
        lcl_sensor_type_from_config = room_sensors[item]["sensor_type"]


        if lcl_sensor_type.lower() not in \
            lcl_sensor_type_from_config.lower():
            
            if __debug__ or debug_AC_Service:
                print(" Getting Sensor Working Type From Config ")

            print(" Sensor is Not for ",lcl_sensor_type ," ")
            continue

        lst_temp = lcl_get_location_of_sensor_from_config.split("_")
        client_port = lst_temp[0] + ":" + lst_temp[1]

        if __debug__ or debug_AC_Service:
            print("Getting Sensor Port and Ip ",client_port,"")
            
        response = requests.get('http://{}/get_data/{}'.format(runtime_ip_port,lcl_get_location_of_sensor_from_config)).content
        response = json.loads(response.decode('utf-8'))

        print("kafka topic: ",response)
        message_recieved = eval(response["message"])

        if __debug__ or debug_AC_Service:
            print("message_recieved by Server ",message_recieved)

        if "content" in message_recieved.keys():
            for item,value in message_recieved["content"].items():

                if __debug__ or debug_AC_Service:
                    print("-----------------")
                    print(item,value)

                if item == "Sensor_Name" and "temperature" in value.lower():
                    if "value" in message_recieved["content"].keys():
                        temp_value = temp_value + float(message_recieved["content"]["value"])
                        count_of_sensor = count_of_sensor + 1

                        if __debug__ or debug_AC_Service:
                            print(temp_value , " Sensor Value " , count_of_sensor)


        time.sleep(5)

        if __debug__:
            print(" End Consumption ")


    average_temperature = 0.0 

    if count_of_sensor>0:
        average_temperature = (temp_value/count_of_sensor)

    if __debug__ or debug_AC_Service:
        print("average_temperature" , average_temperature)

    final_action_to_do = None

    if average_temperature>=0 and average_temperature<=59:
        update_status(lcl_room_to_precool,"Temperature","LOW_TEMP"+str(average_temperature))
        final_action_to_do = "LOW_TEMP"+str(average_temperature)
    elif average_temperature>=60 and average_temperature<=100:
        update_status(lcl_room_to_precool,"Temperature","NORMAL_TEMP"+str(average_temperature))
        final_action_to_do = "NORMAL_TEMP"+str(average_temperature)
    elif average_temperature>=101 and average_temperature<=120:
        update_status(lcl_room_to_precool,"Temperature","HIGH_TEMP"+str(average_temperature))
        final_action_to_do = "HIGH_TEMP"+str(average_temperature)
    else:
        update_status(lcl_room_to_precool,"Temperature","EXTREME_HIGH_TEMP"+str(average_temperature))
        final_action_to_do = "EXTREME_HIGH_TEMP"+str(average_temperature)

    print(final_action_to_do)


    if __debug__:
        print("--------------- Nitish Changes End ---------------- ")

    #--------------------------------------


if __name__ == "__main__":
    global repository_URL
    room_no = sys.argv[1]
    sensor_type = sys.argv[2]
    runtime_ip_port = sys.argv[3]
    repository_URL = "http://"+sys.argv[4]+"/"
    print(repository_URL)
    perform_automate_AC_service(room_no,sensor_type,runtime_ip_port)