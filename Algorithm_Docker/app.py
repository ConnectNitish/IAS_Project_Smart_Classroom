import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

@app.route('/')
def landingPage():
    return "container listener started"

@app.route('/execute',methods=["POST"])
def execute():
    print(request.json)

    data = request.json
    algo_name = data["algo_name"]
    params = data["params"]
    
    repository_ip , repository_port = data["repository_ip_port"].split(":")
    runtime_ip, runtime_port = data["runtime_ip_port"].split(":")
    
    repository_ip = "192.168.0.1"
    runtime_ip = "192.168.0.1"

    response = requests.get('http://{}:{}/get_manifest/{}'.format(repository_ip,repository_port,algo_name)).content
    response = json.loads(response.decode('utf-8'))

    reply = {}
    reply["status"] = "failure"

    if len(params) == response["num_input_params"]:

        package_dependency = response["package_dependency"]
        for pckg in package_dependency:
            os.system("pip3 install {}".format(pckg))
            print("pip3 install {}".format(pckg))

        params_str = ""
        for param in params:
            params_str = params_str +" "+ param
        params_str.strip()

# nohup python3 ./Automated_AC_Service/Automated_AC_Service.py Room1 temperature 192.168.0.1:9000 192.168.0.1:9939 & echo $! > qwerty
        # s = "nohup python3 {}/{}/{}.py {} {}:{} {}:{} & echo $! > out.txt".format(os.getcwd(),algo_name, algo_name, params_str ,runtime_ip,runtime_port,repository_ip,repository_port)
        # os.system('echo {} > echo.txt'.format(s))
        os.system("nohup python3 {}/{}/{}.py {} {}:{} {}:{} & echo $! > out.txt".format(os.getcwd(),algo_name, algo_name, params_str ,runtime_ip,runtime_port,repository_ip,repository_port))

        fp = open("out.txt", "r")
        process_id = fp.read().strip()
        fp.close()
        print("Process id",process_id)
        reply["status"] = "success"
        reply["process_id"] = process_id
        # reply["s"] = s
    print(reply)
    return jsonify(reply)

@app.route('/kill_process/<process_id>',methods=["GET"])
def kill_process(process_id):
	os.system("kill -9 {}".format(process_id))
	reply = {}
	reply[status] = "success"
	return jsonify(reply)

if __name__ == '__main__':

    app.run(host="0.0.0.0",debug=True,port=3500,threaded=True)