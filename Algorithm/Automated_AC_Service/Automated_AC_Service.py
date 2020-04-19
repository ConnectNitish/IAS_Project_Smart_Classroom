import socket                
import threading
import sys
import json
import random
import datetime
import time,requests

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from confluent_kafka import Producer, Consumer, KafkaError

debug_AC_Service = True

from kafka_helper import *

def save_data(device_file_name):
    with open(device_file_name, 'w') as fp:
        json.dump(device_file_name, fp, indent=4, sort_keys=True)

def get_device_info_for_room(device_file_name):
    with open(device_file_name, 'r') as fp:
        device_file_name = json.load(fp)
    # device_file_name = json.dumps(device_file_name)
    return device_file_name

def get_All_Sensor_information(sensor_information):
    with open(sensor_information, 'r') as fp:
        all_sensor_info = json.load(fp)
    return all_sensor_info

def kafka_receive_message(c, consumer_topic_name):
    c.subscribe([consumer_topic_name])
    msg = c.poll(8.0)
    if msg is not None:
        msg = msg.value().decode('utf-8')
    return msg

global kafka_IP_plus_port
kafka_IP_plus_port = None

repository_URL = "http://127.0.0.1:9939/"

def get_ip_port(module_name):
    custom_URL = repository_URL+"get_running_ip/"+module_name

    # if __debug__:
    #     print(" Get IP port of Module ")
    #     print(custom_URL)

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


def update_status(location,device,status):
    get_app_notification_Url = get_ip_port("App_Notification_Service")

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

# sensor_specific_configuration = "Sensor_Specific_Data.json" 

sensor_information = "Sensor_data.json"
sensor_specific_configuration = "Sensor_Specific_Data.json"
glbl_location_device_information = "Location_Device_Information.json" 

def get_All_Sensor_Configuration():
    with open(sensor_specific_configuration, 'r') as fp:
        get_All_Sensor_Configuration = json.load(fp)
    
    if __debug__ or debug_AC_Service:
        print(get_All_Sensor_Configuration)

    return get_All_Sensor_Configuration

def perform_automate_AC_service(room_no,sensor_type):

    #--------------------------------------

    if __debug__ or debug_AC_Service:
        print("--------------- Nitish Changes Start ---------------- ")

    get_Server_Configuration()

    lcl_room_to_precool = room_no
    lcl_get_device_info_file = glbl_location_device_information
    lcl_get_all_sensor_information = sensor_information
    lcl_sensor_type = sensor_type

    lcl_device_file_data_for_all_room = get_device_info_for_room(lcl_get_device_info_file)
    lcl_get_sensor_information_for_all_room = get_All_Sensor_information(lcl_get_all_sensor_information)
    lcl_get_all_Sensor_Configuration = get_All_Sensor_Configuration()


    if __debug__ or debug_AC_Service:
        print(" --- Device Information for All Room --- ")
        print(lcl_device_file_data_for_all_room,"\n")
        print(" --- Sensor Information of All Room --- ")
        print(lcl_get_sensor_information_for_all_room,"\n")

    # if __debug__ or debug_AC_Service:
    #     print(lcl_get_sensor_information_for_all_room[lcl_room_to_precool])

    temp_value = 0.0
    count_of_sensor = 0

    for item,value in lcl_get_sensor_information_for_all_room[lcl_room_to_precool].items():
         

        if __debug__ or debug_AC_Service:
            print(" ---- Value of Particular Room  ")
            print(item,"",value,"")

        lcl_get_location_of_sensor_from_config = lcl_get_sensor_information_for_all_room[lcl_room_to_precool][item]["socket"]
        lcl_sensor_type_from_config = lcl_get_sensor_information_for_all_room[lcl_room_to_precool][item]["sensor_type"]


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
            print(" Kafka IP and Port ",kafka_IP_plus_port,"\n")

        c = Consumer({'bootstrap.servers': kafka_IP_plus_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
        message_recieved = kafka_receive_message(c,lcl_get_location_of_sensor_from_config) 
        c.close()

        if message_recieved == None:
            time.sleep(5)
            continue

        print(type(message_recieved))

        message_recieved = eval(message_recieved)

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


    avearge_temperature = 0.0 

    if count_of_sensor>0:
        avearge_temperature = (temp_value/count_of_sensor)

    if __debug__ or debug_AC_Service:
        print("avearge_temperature" , avearge_temperature)

    final_action_to_do = None

    if avearge_temperature>=0 and avearge_temperature<=59:
        update_status(lcl_room_to_precool,"Temperature","LOW_TEMP"+str(avearge_temperature))
        final_action_to_do = "LOW_TEMP"+str(avearge_temperature)
    elif avearge_temperature>=60 and avearge_temperature<=100:
        update_status(lcl_room_to_precool,"Temperature","NORMAL_TEMP"+str(avearge_temperature))
        final_action_to_do = "NORMAL_TEMP"+str(avearge_temperature)
    elif avearge_temperature>=101 and avearge_temperature<=120:
        update_status(lcl_room_to_precool,"Temperature","HIGH_TEMP"+str(avearge_temperature))
        final_action_to_do = "HIGH_TEMP"+str(avearge_temperature)
    else:
        update_status(lcl_room_to_precool,"Temperature","EXTREME_HIGH_TEMP"+str(avearge_temperature))
        final_action_to_do = "EXTREME_HIGH_TEMP"+str(avearge_temperature)

    print(final_action_to_do)





    if __debug__:
        print("--------------- Nitish Changes End ---------------- ")

    #--------------------------------------




if __name__ == "__main__":
    room_no = sys.argv[1]
    sensor_type = sys.argv[2]
    perform_automate_AC_service(room_no,sensor_type)





























