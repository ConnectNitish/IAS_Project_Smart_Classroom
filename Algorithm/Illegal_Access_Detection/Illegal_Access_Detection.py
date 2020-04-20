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
    # if __debug__:
        
    #     print(" Response From Notification ")
    #     print(r)

    return r

def send_email_to_notification(message_for_email):

    get_app_notification_Url = get_ip_port("App_Notification_Service")

    if __debug__:
        print(" Obtained URL of App Notfication Service ")
        print(get_app_notification_Url)

    str_message_for_email = str(message_for_email)

    notification_URL = "http://"+get_app_notification_Url+"/"
    custom_URL = notification_URL+"send_email/"+str_message_for_email

    if __debug__:
        print(" Obtained full URL of App Notfication Service ")
        print(custom_URL)

    
    r=requests.get(url=custom_URL).content
    r = r.decode('utf-8')
    # print(r)
    if __debug__:
        print(" Response From Notification at last of send_email_to_notification \n")
        print(r,"\n\n")

    return r

sensor_information = "Sensor_data.json"
sensor_specific_configuration = "Sensor_Specific_Data.json"
glbl_location_device_information = "Location_Device_Information.json" 

def get_All_Sensor_Configuration():
    with open(sensor_specific_configuration, 'r') as fp:
        get_All_Sensor_Configuration = json.load(fp)
    
    # if __debug__:
    #     print(get_All_Sensor_Configuration)

    return get_All_Sensor_Configuration

def get_data_for_sensor_for_minute(kafka_ip_port,counter_value,sleep_time,topic_name):
    try:
        lst_data_temp = []

        if __debug__:
            print(" Consumption topic ",topic_name," $$$ ")

        while counter_value>0:
            c = Consumer({'bootstrap.servers': kafka_ip_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
            message_recieved = kafka_receive_message(c,topic_name) 
            c.close()

            if __debug__:
                print(" Message Consumed From Sensor ")
                print(message_recieved,"")

            message_recieved = eval(message_recieved)

            if __debug__:
                print("message_recieved by Server (dict Type) ",message_recieved,"")
                print("counter_value",counter_value,"")
                print(" List ",lst_data_temp,"")

            if "content" in message_recieved.keys():

                if "value" in message_recieved["content"].keys():
                    lst_data_temp.append(int(message_recieved["content"]["value"]))

            time.sleep(int(sleep_time))
            counter_value = counter_value - 1 

        return lst_data_temp

    except:
        return None

def check_safe_unsafe(last_one_minute_data_of_sensor):

    lcl_count_of_number = 0

    for item in last_one_minute_data_of_sensor:
        if item==1:
            lcl_count_of_number = lcl_count_of_number + 1

    return (lcl_count_of_number>0)

def check_illegal_Access_time_frame(time_details_of_room):

    # if __debug__:
    #     print("check_illegal_Access_time_frame ")
    #     print(time_details_of_room,"")

    timestamp = time.strftime('%H:%M')
    hh_mm_ss_current = timestamp.split(":")
    
    hour_time_current = int(hh_mm_ss_current[0])
    minute_time_current = int(hh_mm_ss_current[1])

    hh_mm_ss_start_time = time_details_of_room["occupy_start_time"]
    hh_mm_ss_end_time = time_details_of_room["occupy_end_time"]

    hh_mm_ss_buffer_time = time_details_of_room["occupy_buffer_time"]

    hh_mm_ss_start_time = hh_mm_ss_start_time.split(":")
    start_time_hour,start_time_minute = int(hh_mm_ss_start_time[0]),int(hh_mm_ss_start_time[1])

    hh_mm_ss_end_time = hh_mm_ss_end_time.split(":")
    end_time_hour,end_time_minute = int(hh_mm_ss_end_time[0]),int(hh_mm_ss_end_time[1])

    hh_mm_ss_buffer_time = hh_mm_ss_buffer_time.split(":")
    buffer_time_hour,buffer_time_minute = int(hh_mm_ss_buffer_time[0]),int(hh_mm_ss_buffer_time[1])

    start_time_hour = (start_time_hour - buffer_time_hour + 24 ) % 24
    end_time_hour = (end_time_hour + buffer_time_hour + 24 ) % 24

    end_time_minute = (end_time_minute + buffer_time_minute + 60 ) % 60
    start_time_minute = (start_time_minute - buffer_time_minute + 60 ) % 60

    if __debug__:

        print(" Check Time Constraints Start ")
        
        print(" start_time_hour ",start_time_hour,\
            " \t end_time_hour" , end_time_hour)

        print(" hour_time_current \t ",hour_time_current,"\n")

        print(" hour_time_current >= start_time_hour ", (hour_time_current >= start_time_hour),"")
        print(" hour_time_current <= end_time_hour ", (hour_time_current <= end_time_hour),"")

        print(" Check Time Constraints Ends ")

    if hour_time_current >= start_time_hour and hour_time_current <= end_time_hour:
        
        return True

    return False

def prepare_email(status,location):
    try:

        time.sleep(3)
        lcl_message_for_email = {}
        lcl_message_for_email["status"] = status
        lcl_message_for_email["time_stamp"] = time.strftime("%A_%d_%B_%Y_%I_%M_%p")
        lcl_message_for_email["algorithm"] = "Illegal_Access_Detection"
        lcl_message_for_email["topic_name"] = "Security_Breach"
        lcl_message_for_email["location"] = location

        if __debug__:
            print("\n\n Mail Content \n")
            print(lcl_message_for_email,"\n\n")
        
        send_email_to_notification(lcl_message_for_email)
    except:
        print(" Error while Preparing Email ")


def perform_illegal_access_detection(room_no,sensor_type):

    #--------------------------------------

    if __debug__:
        print("--------------- Nitish Changes Start ---------------- ")

    get_Server_Configuration()

    lcl_room_to_precool = room_no
    lcl_get_device_info_file = glbl_location_device_information
    lcl_get_all_sensor_information = sensor_information
    lcl_sensor_type = sensor_type

    lcl_device_file_data_for_all_room = get_device_info_for_room(lcl_get_device_info_file)
    lcl_get_sensor_information_for_all_room = get_All_Sensor_information(lcl_get_all_sensor_information)
    lcl_get_all_Sensor_Configuration = get_All_Sensor_Configuration()


    if __debug__:
        print(" --- Location Device Information --- ")
        print(lcl_device_file_data_for_all_room,"")
        print(" --- Sensor Configuration --- ")
        print(lcl_get_sensor_information_for_all_room,"")

    lcl_access_breached = False

    for item,value in lcl_get_sensor_information_for_all_room[lcl_room_to_precool].items():
         

        if __debug__:
            print(" Start Consumption ")
            print(item,value)

        bool_check_time_range = True

        if bool_check_time_range and check_illegal_Access_time_frame(lcl_device_file_data_for_all_room[lcl_room_to_precool]) == True:
            print(" -- Time Out of Range -- ")
            continue

        lcl_get_location_of_sensor_from_config = lcl_get_sensor_information_for_all_room[lcl_room_to_precool][item]["socket"]
        lcl_sensor_type_from_config = lcl_get_sensor_information_for_all_room[lcl_room_to_precool][item]["sensor_type"]

        if lcl_sensor_type.lower() not in \
            lcl_sensor_type_from_config.lower():
            
            if __debug__ or debug_AC_Service:
                print(" Getting Sensor Working Type From Config ")

            print(" Sensor is Not for ",lcl_sensor_type ," ")
            continue

        lst_temp = lcl_get_location_of_sensor_from_config.split("_")
        # lcl_get_location_of_sensor_from_config = lst_temp[0] + ":" + lst_temp[1]

        if __debug__ : 
            print(" IP Port of Sensor ",lcl_get_location_of_sensor_from_config,"")
            print(" Sensor type from Config ",lcl_sensor_type_from_config,"")

        loop_iteration_value = None

        lcl_frequency_of_running_server = lcl_get_all_Sensor_Configuration[lcl_sensor_type_from_config]["Frequency"]
        lcl_frequency_of_running_server_unit = lcl_get_all_Sensor_Configuration[lcl_sensor_type_from_config]["unit"]

        if lcl_frequency_of_running_server_unit == "sec":
            loop_iteration_value = 60 / int(lcl_frequency_of_running_server) 

        if __debug__:
            print(" Loop Final Counter Value ",loop_iteration_value," --- ")

        lcl_lst_data = get_data_for_sensor_for_minute \
            ("127.0.0.1:9092",loop_iteration_value,lcl_frequency_of_running_server,lcl_get_location_of_sensor_from_config)

        if __debug__:
            print(" List of All previous 1 minute Data ")
            print(lcl_lst_data,"")

        lcl_access_breached = check_safe_unsafe(lcl_lst_data) 


        time.sleep(5)

        if __debug__:
            print(" Final Indicator ",lcl_access_breached,"")

    final_action_to_do = None

    if lcl_access_breached == True:
        update_status(lcl_room_to_precool,"Access","Breached")
        final_action_to_do = "Breached"
        prepare_email(final_action_to_do,lcl_room_to_precool)
    else:
        update_status(lcl_room_to_precool,"Access","Safe")
        final_action_to_do = "Safe"
        # prepare_email(final_action_to_do,lcl_room_to_precool)

    print(final_action_to_do)

    if __debug__:
        print("--------------- Nitish Changes End ---------------- ")

    #--------------------------------------

if __name__ == "__main__":
    room_no = sys.argv[1]
    sensor_type = sys.argv[2]
    perform_illegal_access_detection(room_no,sensor_type)





























