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


        # consumer = KafkaConsumer(function_name,group_id=server_id,bootstrap_servers=server_id,key_deserializer=lambda m: json.loads(m.decode('utf-8')),value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        # print("Consuming End")
        # print(consumer)
        # for item in consumer:
        #     print("****************8")
        #     print(item)
        #     print(item.key)


# sensor_information = "Sensor_data.json"

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
    
    # if __debug__:
    #     print(all_sensor_info)

    return all_sensor_info

def kafka_receive_message(c, consumer_topic_name):
    c.subscribe([consumer_topic_name])
    msg = c.poll(8.0)
    if msg is not None:
        msg = msg.value().decode('utf-8')
    return msg

notification_URL = "http://127.0.0.1:8100/"

def update_status(location,device,status):
    custom_URL = notification_URL+"/start_device/"+location+"/" + device + "/" + status
    r=requests.get(url=custom_URL).content
    r = r.decode('utf-8')
    print(r)
    return r

sensor_specific_configuration = "Sensor_Specific_Data.json" 

def get_All_Sensor_Configuration():
    with open(sensor_specific_configuration, 'r') as fp:
        get_All_Sensor_Configuration = json.load(fp)
    
    if __debug__:
        print(get_All_Sensor_Configuration)

    return get_All_Sensor_Configuration

def main():
    kafka_helper_obj = kafka_api()
    lcl_room_to_precool = sys.argv[1]
    lcl_get_device_info_file = sys.argv[2]
    lcl_get_all_sensor_information = sys.argv[3]
    lcl_sensor_type = sys.argv[4]

    lcl_device_file_data_for_all_room = get_device_info_for_room(lcl_get_device_info_file)
    lcl_get_sensor_information_for_all_room = get_All_Sensor_information(lcl_get_all_sensor_information)
    lcl_get_all_Sensor_Configuration = get_All_Sensor_Configuration()


    if __debug__:
        print(" --- Location Device Information --- ")
        print(lcl_device_file_data_for_all_room,"")
        print(" --- Sensor Configuration --- ")
        print(lcl_get_sensor_information_for_all_room,"")

    # if __debug__:
    #     print(lcl_get_sensor_information_for_all_room[lcl_room_to_precool])

    temp_value = 0.0
    count_of_sensor = 0

    for item,value in lcl_get_sensor_information_for_all_room[lcl_room_to_precool].items():
         

        if __debug__:
            print(" Start Consumption ")
            print(item,value)

        if "working_type" in lcl_get_all_Sensor_Configuration[item].keys():
            if "temperature".lower() not in \
                lcl_get_all_Sensor_Configuration[item]["working_type"].lower():
                
                if __debug__:
                    print(" Getting Sensor Working Type From Config ")

                print(" Sensor is Not for Temperature ")
                continue

        lst_temp = value.split("_")
        client_port = lst_temp[0] + ":" + lst_temp[1]

        print("Client client_port",client_port)

        c = Consumer({'bootstrap.servers': '127.0.0.1:9092', 'group.id': '1', 'auto.offset.reset': 'earliest'})
        message_recieved = kafka_receive_message(c,value) 
        c.close()

        if message_recieved == None:
            time.sleep(5)
            continue

        print(type(message_recieved))

        message_recieved = eval(message_recieved)

        if __debug__:
            print("message_recieved by Server ",message_recieved)

        if "content" in message_recieved.keys():
            for item,value in message_recieved["content"].items():

                if __debug__:
                    print("-----------------")
                    print(item,value)

                if item == "Sensor_Name" and "temperature" in value.lower():
                    if "value" in message_recieved["content"].keys():
                        temp_value = temp_value + float(message_recieved["content"]["value"])
                        count_of_sensor = count_of_sensor + 1

                        if __debug__:
                            print(temp_value , " Senosr Value " , count_of_sensor)



        time.sleep(5)

        if __debug__:
            print(" End Consumption ")


    avearge_temperature = 0.0 

    if count_of_sensor>0:
        avearge_temperature = (temp_value/count_of_sensor)

    if __debug__:
        print("avearge_temperature" , avearge_temperature)

    final_action_to_do = None

    if avearge_temperature>=0 and avearge_temperature<=59:
        update_status(lcl_room_to_precool,"AC","LOW_TEMP"+str(avearge_temperature))
        final_action_to_do = "LOW_TEMP"
    elif avearge_temperature>=60 and avearge_temperature<=100:
        update_status(lcl_room_to_precool,"AC","NORMAL_TEMP"+str(avearge_temperature))
        final_action_to_do = "NORMAL_TEMP"
    elif avearge_temperature>=101 and avearge_temperature<=120:
        update_status(lcl_room_to_precool,"AC","HIGH_TEMP"+str(avearge_temperature))
        final_action_to_do = "HIGH_TEMP"
    else:
        update_status(lcl_room_to_precool,"AC","EXTREME_HIGH_TEMP"+str(avearge_temperature))
        final_action_to_do = "EXTREME_HIGH_TEMP"


    print(final_action_to_do)


    #--------------------------------------

    if __debug__:
        print("--------------- Nitish Changes Start ---------------- ")

    # consumer = KafkaConsumer(function_name,group_id=server_id,bootstrap_servers=server_id,key_deserializer=lambda m: json.loads(m.decode('utf-8')),value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    # print("Consuming End")
    # print(consumer)
    # for item in consumer:
    #     print("****************8")
    #     print(item)
    #     print(item.key)


    if __debug__:
        print("--------------- Nitish Changes End ---------------- ")

    #--------------------------------------

    # OLD Aditi's Code 
    # sensor_ip, sensor_port, sensor_sock = udp_init()
    # gateway_ip_address, gateway_port = get_gateway_details()
    # sensor_gateway_thread = start_sensor_gateway_thread(sensor_sock, gateway_ip_address, gateway_port, sensor_data)
    # gateway_sensor_thread = start_gateway_sensor_thread(sensor_sock)
    # sensor_gateway_thread.join()
    # gateway_sensor_thread.join()

if __name__ == "__main__":
    main()





























