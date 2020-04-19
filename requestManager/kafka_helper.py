import sys,time
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError

no_of_retry = 50

class kafka_api():

	# topic , "default", client_id(consuming(ip+port)) , server_id(sending(ip+port))
	def produce_topic(self,topic_name,receiver_id,value,kafka_id):
	    producer = KafkaProducer(retries=no_of_retry,bootstrap_servers=kafka_id,key_serializer=lambda m: json.dumps(m).encode('utf-8'),value_serializer=lambda m: json.dumps(m).encode('utf-8'))
	    producer.send(topic_name,key=receiver_id,value=value)
	    producer.flush()

	# topic , client_id(consuming(ip+port)) , server_id(sending(ip+port))
	def consume_topic(self,function_name,client_id,server_id):
	    consumer = KafkaConsumer(function_name,group_id=client_id,bootstrap_servers=server_id,key_deserializer=lambda m: json.loads(m.decode('utf-8')),value_deserializer=lambda m: json.loads(m.decode('utf-8')))
	    return consumer

# counter = 1
# kafka_api_obj = kafka_api()

# while(True):

# 	# value of the Data / message 
# 	reply = "kafka_data_" + str(counter)
# 	topic_name = "topic_name_logging"
# 	# key of the Data / message 
# 	client_id = "default"
# 	server_id = "127.0.0.1:9092"
# 	print(" Start Producing ")
# 	kafka_api_obj.produce_topic(topic_name,client_id,reply,server_id)
# 	counter = counter + 1
# 	time.sleep(60)