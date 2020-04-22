import socket                
import threading
import sys
import json
import random
import datetime
import time

sensor_information = "Sensor_data.json"

# ------------------------------ Nitish Changes 

def get_All_Sensor_information():
    with open(sensor_information, 'r') as fp:
        all_sensor_info = json.load(fp)
    
    if __debug__:
        print(all_sensor_info)

    return all_sensor_info

def get_Sensor_Info_As_perlocation(all_sensor_location,location_name):
    return all_sensor_location[location_name]

global name_of_sensor
name_of_sensor = None  

def udp_init_for_Sensor(ip,port):
    sensor_ip = ip
    sensor_port = int(port)
    sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sensor_socket.bind((sensor_ip, sensor_port))
    return sensor_socket

def generate_random_sensor_data(name_of_sensor):
    random_data = {}
    random_data["type"] = "sensor_data"
    content = {}
    content["time"] = str(datetime.datetime.now())
    content["value"] = str(random.randrange(10, 40))

    if __debug__:
        print("##### ------- name_of_sensor")
        print(name_of_sensor)

    content["Sensor_Name"] = name_of_sensor
    random_data["content"] = content
    random_data = json.dumps(random_data)
    return random_data

# ------------------------------ Nitish Changes End 

def get_device_info_for_room(device_file_name):
    with open(device_file_name, 'r') as fp:
        device_file_name = json.load(fp)
    # device_file_name = json.dumps(device_file_name)
    return device_file_name

def main():
    lcl_get_device_info_file = sys.argv[1]
    lcl_device_file_data_for_all_room = get_device_info_for_room(lcl_get_device_info_file)

    print(lcl_device_file_data_for_all_room)

    #--------------------------------------

    if __debug__:
        print("--------------- Nitish Changes Start ---------------- ")

    while True:
        str_input = input("Input Your Command\n")
        if str_input == "quit":
            break
        elif "getstatus" in str_input:
            params_value = str_input.split(" ")
            cmd_name = params_value[0]
            location_name = params_value[1]
            device_name = params_value[2]

            lcl_device_file_data_for_all_room = get_device_info_for_room(lcl_get_device_info_file)

            if __debug__:
                print(location_name)
                print(device_name)

            print(lcl_device_file_data_for_all_room[location_name][device_name]["status"])

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





























