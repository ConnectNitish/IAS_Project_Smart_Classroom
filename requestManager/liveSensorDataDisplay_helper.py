import json
import socket                
import threading
import sys
import json
import copy
import random
import datetime
import os
import time,requests
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from confluent_kafka import Producer, Consumer, KafkaError

repository_URL = "http://0.0.0.0:9939/"


def get_ip_port(module_name):
    custom_URL = repository_URL+"get_running_ip/"+module_name
    r=requests.get(url=custom_URL).content
    r = r.decode('utf-8')
    # print(r)
    return r

def kafka_receive_message(c, consumer_topic_name):
    c.subscribe([consumer_topic_name])
    msg = c.poll(8.0)
    if msg is not None:
        msg = msg.value().decode('utf-8')
    return msg

def getData(all_sensor_info,all_sensor_config):

    kafka_IP_plus_port = get_ip_port("Kafka_Service")

    retDict = {} 
    temp = {}
    cnt = 1
    all_list = []
    for key,value in all_sensor_info.items():
        # print(key)
        retDict['location'] = key
        ot = []
        for sensor_type,sensor_info in value.items():
            tlist = []
            print(sensor_type)
            print(sensor_info)
            retDict['sensor_name'] = sensor_type
            retDict['sensor_socket'] = sensor_info["socket"]

            topic = sensor_info["socket"]
            c = Consumer({'bootstrap.servers': kafka_IP_plus_port, 'group.id': '1', 'auto.offset.reset': 'earliest'})
            message_recieved = kafka_receive_message(c,topic) 
            c.close()
            
            if __debug__:
                print(" Read From Sensors ")
                print(message_recieved)

            if message_recieved == None:
                continue

            message_recieved = eval(message_recieved)
            retDict['time'] = message_recieved["content"]["time"]
            retDict['value'] = message_recieved["content"]["value"]
            tlist.append(key)
            tlist.append(sensor_type)
            tlist.append(topic)
            tlist.append(message_recieved["content"]["time"])
            tlist.append(message_recieved["content"]["value"])
            t = copy.deepcopy(tlist)
            ot.append(t)
            cnt = cnt + 1
            # temp.update(retDict)
            t = copy.deepcopy(retDict)
            all_list.append(t)
        # retDict["value"] = ot
    return all_list
           
