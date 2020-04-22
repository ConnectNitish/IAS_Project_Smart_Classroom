import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import sys
import json
import os, uuid
import socket
import requests

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)


@app.route('/')
def index():

	req = {}
	req["algo_name"] = "Automated_AC_Service"
	req["params"] = ["Room1","temperature"]
	# req["repository_ip_port"] = "0.0.0.0:9939"
	# req["runtime_ip_port"] = "0.0.0.0:9000"
	# response = requests.post('http://0.0.0.0:3500/execute',json=req)
	response = requests.post('http://0.0.0.0:9000/start',json=req)
	response = json.loads(response.text)

	# #
	# response = requests.get("http://0.0.0.0:9000/stop/af0c9fc1-f5b4-4d1f-b386-0e5023c623fa")
	# response = json.loads(response.decode('utf-8'))

	print(response)
	return response

if __name__=='__main__':

    app.run(host="0.0.0.0",debug=True,port=15000,threaded=True)