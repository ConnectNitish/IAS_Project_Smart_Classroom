import socket                
import threading
import sys
import json
import random
import datetime
import time,random

sensor_information = "Sensor_data.json"
sensor_specific_configuration = "Sensor_Specific_Data.json" 

# ------------------------------ Nitish Changes 

def get_All_Sensor_information():
    with open(sensor_information, 'r') as fp:
        all_sensor_info = json.load(fp)
    
    if __debug__:
        print(all_sensor_info)

    return all_sensor_info

def get_All_Sensor_Configuration():
    with open(sensor_specific_configuration, 'r') as fp:
        get_All_Sensor_Configuration = json.load(fp)
    
    if __debug__:
        print(get_All_Sensor_Configuration)

    return get_All_Sensor_Configuration

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

def generate_logic_for_temp_sensor():
    secure_random = random.SystemRandom()
    probability = secure_random.random()

    if __debug__:
        print(" Genrated probability is for Temperature Sensor ",probability)

    if probability>=0.0 and probability<0.5:
        return str(random.randrange(200,500))
    elif probability>=0.5 and probability<0.2:
        return str(random.randrange(101,120))
    elif probability>=0.2 and probability<0.4:
        return str(random.randrange(10,59))
    elif probability>=0.4:
        return str(random.randrange(60,100))

def generate_logic_for_attendance_sensor():
    return [str(random.randrange(0,250)),str(random.randrange(100,500))]

def generage_logic_for_binary_sensor():
    secure_random = random.SystemRandom()
    probability = secure_random.random()

    if __debug__:
        print(" Genrated probability is for binary Sensor ",probability)

    if probability>=0 and probability<0.9:
        return str(0)
    elif probability>=0.9:
        return str(1)


def generate_random_sensor_data(data_of_sensor):
    random_data = {}
    random_data["type"] = "sensor_data"
    content = {}
    content["time"] = str(datetime.datetime.now())

    if __debug__:
        print(" Sensor Configuration ")
        print(data_of_sensor["sensor_configuration"],"")

    lcl_type_of_sensor = data_of_sensor["sensor_type"].lower()

    if "Temperature_Sensor".lower() in lcl_type_of_sensor:
        content["value"] = str(generate_logic_for_temp_sensor())
    elif "Binary_Door_Step_Sensor".lower() in lcl_type_of_sensor:
        content["value"] = generage_logic_for_binary_sensor()
    elif "Numeric_Attendance_Sensor".lower() in lcl_type_of_sensor:
        content["value"] = generate_logic_for_attendance_sensor()
    elif "Parking_Lot_Sensor".lower() in lcl_type_of_sensor:
        content["value"] = generage_logic_for_binary_sensor()
    else:
        content["value"] = str(random.randrange(1000,2000))

    if __debug__:
        print("##### ------- name_of_sensor")
        print(data_of_sensor,"")

    content["Sensor_Name"] = data_of_sensor["name_of_sensor"]
    content["location"] = data_of_sensor["location_name"]
    content["ip_port"] = data_of_sensor["ip_port"]
    random_data["content"] = content
    random_data = json.dumps(random_data)
    return random_data

# ------------------------------ Nitish Changes End 

def get_All_Sensor_information():
    with open(sensor_information, 'r') as fp:
        all_sensor_info = json.load(fp)
    
    if __debug__:
        print(all_sensor_info,"")


    return all_sensor_info

def get_Sensor_Info_As_perlocation(all_sensor_location,location_name):
    return all_sensor_location[location_name]

def udp_init():
    sensor_ip = "127.0.0.1"
    sensor_port = 6722
    sensor_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sensor_sock.bind((sensor_ip, sensor_port))
    return sensor_ip, sensor_port, sensor_sock

# sensor data format (gateway sends this to sensor topic (ip_port of sensor))
# {
#     "type": "sensor_data",
#     "content": {
#         "time": "...", \\get time using datetime.datetime.utcnow()
#         "value": "..." \\generate value randomly
#     }
# }

def generate_random_data(start, end):
    random_data = {}
    random_data["type"] = "sensor_data"
    content = {}
    content["time"] = str(datetime.datetime.now())
    content["value"] = str(random.randrange(start, end))

    global name_of_sensor 

    if __debug__:
        print("##### ------- name_of_sensor")
        print(name_of_sensor)

    content["Sensor_Name"] = name_of_sensor
    random_data["content"] = content
    random_data = json.dumps(random_data)
    return random_data
    

def receive_data(recipient_socket_address):
    data, addr = recipient_socket_address.recvfrom(1024)
    print("Message: ", data.decode())
    return data.decode()

def send_data(sock, sender_socket_address, recipient_ip_address, recipient_port, Message):
    sender_socket_address.sendto(Message.encode(), (recipient_ip_address, recipient_port))
    print("########### -- Sensor Data")
    print(Message)

def receive_from_gateway(sensor_socket_address):
    gateway_data = receive_data(sensor_socket_address)
    return gateway_data

def send_to_gateway(sensor_socket_address, gateway_ip_address, gateway_port, Registration_Message,data_of_sensor):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_data(sock, sensor_socket_address, gateway_ip_address, gateway_port, Registration_Message)
    while True:
        
        if __debug__:
            print("\nData Of Sensor Before Sleep")
            print(data_of_sensor)
            print("\n")

        Message = generate_random_sensor_data(data_of_sensor)
        send_data(sock, sensor_socket_address, gateway_ip_address, gateway_port, Message)

        lcl_type_of_unit,lcl_frequency = None,None

        if "unit" in data_of_sensor["sensor_configuration"].keys():
            if "Frequency" in data_of_sensor["sensor_configuration"].keys():
                lcl_type_of_unit = data_of_sensor["sensor_configuration"]["unit"]
                lcl_frequency = data_of_sensor["sensor_configuration"]["Frequency"]

        if lcl_type_of_unit != None and lcl_frequency!=None:
            if lcl_type_of_unit == "sec" and int(lcl_frequency)>0:
            
                if __debug__:
                    print("Default Timer is Set up by Configuration --- Sec ")
                
                time.sleep(int(lcl_frequency))
            
            elif lcl_type_of_unit == "min" and int(lcl_frequency)>0:
            
                if __debug__:
                    print("Default Timer is Set up by Configuration --- Min")
                
                time.sleep(int(lcl_frequency)*60)

        else:
            if __debug__:
                print("Default Timer is set for Sensor")
            time.sleep(45)



def sensor_gateway_thread_init(sensor_socket_address, gateway_ip_address, gateway_port, Message,data_of_sensor):
    send_to_gateway(sensor_socket_address, gateway_ip_address, gateway_port, Message,data_of_sensor)


def gateway_sensor_thread_init(sensor_socket_address):
    gateway_data = receive_from_gateway(sensor_socket_address)
    return gateway_data

def start_sensor_gateway_thread(sensor_socket_address, gateway_ip_address, gateway_port, Message,data_of_sensor):
    t1 = threading.Thread(target=sensor_gateway_thread_init, args=(sensor_socket_address, gateway_ip_address, gateway_port, Message,data_of_sensor))
    t1.start()
    print("t1 started")
    return t1

def start_gateway_sensor_thread(sensor_socket_address):
    t2 = threading.Thread(target=gateway_sensor_thread_init, args=(sensor_socket_address, ))
    t2.start()
    print("t2 started")
    return t2

def get_gateway_details():
    gateway_ip_address = "127.0.0.1"
    gateway_port = 6745
    return gateway_ip_address, gateway_port

def get_sensor_info(sensor_file_name):
    with open(sensor_file_name, 'r') as fp:
        sensor_data = json.load(fp)
    sensor_data = json.dumps(sensor_data)
    return sensor_data

sensor_config_file_name = "config_sensor2.json"

def main():
    # sensor_config_file_name = sys.argv[1]
    sensor_data = get_sensor_info(sensor_config_file_name)

    # sensor_data = {'name':'a'}

    #--------------------------------------

    if __debug__:
        print("--------------- Nitish Changes Start ---------------- ")

    all_sensor_info_with_location =  get_All_Sensor_information()
    lcl_all_sensor_config = get_All_Sensor_Configuration()

    if __debug__:
        print(" All Sensor Information ")
        print(all_sensor_info_with_location,"")
        print(" All Sensor Configuration ")
        print(lcl_all_sensor_config,"")

    for item in all_sensor_info_with_location:
        
        # if __debug__:
        #     print(" ---- Room Details ---- ")
        #     print(item,"")
        
        for location_sensor in all_sensor_info_with_location[item].keys():

            if __debug__:
                print(" Debug Details ")
                print(location_sensor,"")
            
            if __debug__:
                print(location_sensor , " Details in  ",item,"")
                print(all_sensor_info_with_location[item][location_sensor],"")

            lcl_get_location_of_sensor = all_sensor_info_with_location[item][location_sensor]["socket"]
            lcl_sensor_type = all_sensor_info_with_location[item][location_sensor]["sensor_type"]

            lst_lcl_get_location_of_sensor = lcl_get_location_of_sensor.split("_")  

            lcl_ip_sensor = lst_lcl_get_location_of_sensor[0]
            lcl_port_sensor = lst_lcl_get_location_of_sensor[1]

            if __debug__:
                print(" Ip port of Sensor ")
                print(lcl_ip_sensor,lcl_port_sensor)

            lcl_sensor_socket = udp_init_for_Sensor(lcl_ip_sensor,lcl_port_sensor)
            gateway_ip_address, gateway_port = get_gateway_details()

            data_of_sensor = {}
            data_of_sensor["location_name"] = item
            data_of_sensor["name_of_sensor"] = location_sensor
            data_of_sensor["ip_port"] = lcl_get_location_of_sensor
            data_of_sensor["sensor_type"] = lcl_sensor_type
            data_of_sensor["sensor_configuration"] = lcl_all_sensor_config[lcl_sensor_type]

            sensor_gateway_thread = start_sensor_gateway_thread(lcl_sensor_socket, gateway_ip_address, gateway_port, sensor_data,data_of_sensor)


    if __debug__:
        print("--------------- Nitish Changes End ---------------- ")

if __name__ == "__main__":
    main()





























