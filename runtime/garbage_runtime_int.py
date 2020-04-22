#used as bridge between kafka and containers
import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
from kafka_api import *
import sys
import json
import os

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

global kafka_server_id
kafka_server_id = "127.0.0.1:9092"

@app.route('/output',methods=['POST'])
def output():

	print(response)

@app.route('/get_data/<sensor_id>')
def get_data_kafka(sensor_id):
	topic_name = sensor_id
	reply = {}
	kafka_api_obj = kafka_api()
	response = kafka_api_obj.consume_topic(topic_name,"default",server_id)
	print(response)
	return jsonify(response) #return type dict


if __name__=='__main__':
	kafka_server_id = sys.argv[1]
	print("sfsdfsd:",kafka_server_id)
	app.run(host="0.0.0.0",debug=True,port=4000,threaded=True)
