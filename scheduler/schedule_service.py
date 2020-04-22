from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
import json
import subprocess
import time
import sys
import schedule
from threading import Thread
from time import sleep
import time
import threading
import ast
import requests
import datetime
from datetime import datetime as date
import signal

import socket
import sys

app = Flask(__name__)

global kafka_IP_plus_port
global load_balancer_ip_port
global scheduler_ip_port
kafka_IP_plus_port = None
load_balancer_ip_port = None
scheduler_ip_port = None
repository_URL = "http://"+sys.argv[1]+"/"

def handler(signal, frame):
	global scheduler_ip, scheduler_port, load_balancer_ip_port
	print('CTRL-C pressed!')
	# unregister(scheduler_ip, scheduler_port, "SchedulingService", load_balancer_ip_port)
	sys.exit(0)


def unregister(scheduler_ip, scheduler_port, serviceName, load_balancer_ip_port):
	print('Inside UnRegister')
	lb_url = "http://"+load_balancer_ip_port
	data = {"serviceName": serviceName, "ip": scheduler_ip, "port": scheduler_port}
	print('Response:', requests.post(lb_url+'/unregister_service' , json=data))


def register(scheduler_ip, scheduler_port, serviceName, load_balancer_ip_port):
	print('Inside register')
	lb_url = "http://"+load_balancer_ip_port
	data = {"serviceName": serviceName, "ip": scheduler_ip, "port": scheduler_port}
	print('Response:', requests.post(lb_url + '/register_service', json=data))


@app.route('/health')
def health():
    return "OK"

@app.route('/')
def up():
    return "I am Scheduler Who is Up"

def startaction(path,filename, appname, port, ip,username, password,inputStream,command_line_params):
	print("IN START ACTIN FUCN------------------------",filename)
	
	#************************************

	# current_dir = os.getcwd()
	# print(current_dir)
	# os.chdir(path)

	#***************************

	params_list =  command_line_params.split(" ")
	augmented_params_list = []
	augmented_params_list.append('python3')

	# new 
	#************** filename edited 

	algorithm_path = os.getcwd()+"/Algorithm/"+filename.replace(".py","")+"/" + filename
	filename = algorithm_path

	if __debug__:
		print(" Full File Path is ",filename,"")

	# old 
	augmented_params_list.append(filename)



	for item in params_list:
		augmented_params_list.append(item)
	print("augmented_params_list is ",augmented_params_list)
	proc = subprocess.Popen(augmented_params_list)
	# proc = subprocess.Popen(['python3',filename])
	f = open(filename+"_processID.txt", "a")
	f.write(str(proc.pid)+"\n")
	f.close()

def killproc(path,filename, appname, port, ip,username, password,inputStream):
	print("IN KILL PROCESS FUCN------------------------")
	os.chdir(path)
	f = open(filename+"_processID.txt", "r")
	pid  = f.readline()
	pid = int(pid)
	print("PID TO KILL ---------------> ",pid,type(pid))
	f.close()
	os.kill(pid,signal.SIGSTOP)

#****************** path_for_config_file 
path_to_app = os.getcwd()+"/Repository/Scheduler_Config_file"

def startNewProcess(appName):
	# path_to_app = "/home/chitta/sem4/Internals_of_Application_Servers/2020/nitish/Algo_IAS_Hackathon_2 (1)/Algo_IAS_Hackathon_2/Testing/"
	scheduler_config = path_to_app+"/"+appName+".scheduler_config.json"
	
	if __debug__:
		print(" Full Path for File ","")
		print(scheduler_config,"")

	#******** Can do wget and Paste on Local ( Not Currently Needed ) 

	with open(scheduler_config) as json_file:
		sdata = json.load(json_file)
		for p in sdata['function']:
			file_name = p["file_name"]
			command_line_params = p["parameters"]
			sched_in_future_flag = p['sched_in_future']
			day = p['sched_day']
			start_date = p['start_date']
			start_month = p['start_month']
			start_year = p['start_year']

			sched_only_between = int(p['sched_only_between'])
			start_hour = (p['start_hour'])
			start_min = (p['start_min'])
			start_sec = (p['start_sec'])
			end_hour = (p['end_hour'])
			end_min = (p['end_min'])
			end_sec = (p['end_sec'])
			days_str = p['days']
			print("days_str is = " ,days_str)
			# res = ast.literal_eval(days_str) 
			# print("res is = " ,res)
			print(type(days_str))

			sched_once_at_time_flag = int(p['sched_once_at_time_flag'])
			sched_at_hr = (p['sched_at']['hour'])
			sched_at_min = (p['sched_at']['minute'])
			sched_at_sec = (p['sched_at']['second'])

			sched_at_intervals_flag = int(p['sched_at_intervals_flag'])
			interval_hours = int(p['interval_hours'])
			interval_minutes = int(p['interval_minutes'])
			interval_seconds = int(p['interval_seconds'])
			days_interval =  p['idays']
			start_hour_interval = (p['istart_hour'])
			start_min_interval = (p['istart_min'])
			start_sec_interval = (p['istart_sec'])
			end_hour_interval = (p['iend_hour'])
			end_min_interval = (p['iend_min'])
			end_sec_interval = (p['iend_sec'])


			ip = "127.0.0.1" # deploy__socket info from database
			port = "9009"
			uname = "chitta"
			password = "abc"
			stream_ip = "temp"
			print("inside START FUNCTION")
			print(type(sched_at_intervals_flag),sched_at_intervals_flag)
			print(type(interval_seconds),interval_seconds)
			if(sched_at_intervals_flag==1):
				cur_day = date.today().strftime("%A")
				print("cur_day -->",cur_day,type(cur_day))
				rv = 0
				if(cur_day in days_interval):
					rv = 1
				print("rv ",rv,type(days_interval[0]))
				print(days_interval.count(cur_day))
				while cur_day in days_interval:
					s_time = start_hour_interval+":"+start_min_interval
					e_time = end_hour_interval+":"+end_min_interval
					start_time_py = datetime.datetime.strptime(s_time,'%H:%M')
					end_time_py = datetime.datetime.strptime(e_time,'%H:%M')
					dnow=datetime.datetime.now()
					# print("dnow------------------->",dnow)
					# print(type(dnow))
					# print("start_time_py-------------> ",start_time_py)
					# print(type(start_time_py))
					tagStr = appName+"_interval_sched"
					while(dnow.time() < start_time_py.time()):
						time.sleep(1) 
						dnow=datetime.datetime.now()
					if (dnow.time() > start_time_py.time() ):
						schedule.every(1).seconds.do(startaction,path=path_to_app,filename=file_name, appname=appName, port=port, ip=ip,
															username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params).tag("intitial_sched")
						schedule.run_pending()
						time.sleep(2)
						schedule.clear(tag="intitial_sched")
						schedule.run_pending() 
						print("inside if...aftershcedu pending")
						
						if(interval_seconds!=0):
							# print("INSIDE INTERVAL_SECIONFS")
							schedule.every(interval_seconds).seconds.do(startaction,path=path_to_app,filename=file_name, appname=appName, port=port, ip=ip,
															username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params).tag(tagStr)

						elif(interval_minutes!=0):
							# print("INSIDE min")
							schedule.every(interval_minutes).minutes.do(startaction,path=path_to_app,filename=file_name, appname=appName, port=port, ip=ip,
															username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params).tag(tagStr)
						
						elif(interval_hours!=0):
							# print("INSIDE hr")
							schedule.every(interval_hours).hours.do(startaction,path=path_to_app,filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip,
														command_line_params=command_line_params).tag(tagStr)
						
					
					dnow=datetime.datetime.now()
					while(dnow.time() < end_time_py.time()):
						schedule.run_pending() 
						time.sleep(1) 
						dnow=datetime.datetime.now()
					print("Time expiration occured FOR APP---------------++++++++++++++++++>>>>>>>",appName)
					schedule.clear(tag=tagStr)
					schedule.run_pending()
					break

			else:
				print("No interval scheduling  given")

			if(sched_only_between==1):
				temp_end_min = int(start_min)+1
				start_time = start_hour + ":" + start_min
				end_time = end_hour + ":" + end_min
				# end_time = start_hour + ":" + str(temp_end_min)
				for d in days_str:
					if(d=="sun"):
						schedule.every().sunday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().sunday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="mon"):
						schedule.every().monday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().monday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="tue"):
						schedule.every().tuesday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().tuesday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="wed"):
						schedule.every().wednesday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().wednesday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="thu"):
						schedule.every().thursday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().thursday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="fri"):
						schedule.every().friday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().friday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)
					if(d=="sat"):
						schedule.every().saturday.at(start_time).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
																username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)
						schedule.every().saturday.at(end_time).do(killproc, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,
														username=uname, password=password,inputStream=stream_ip)

			if(sched_once_at_time_flag==1):
				schedule.every().day.at(sched_at_hr+":"+sched_at_min+":"+sched_at_sec).do(startaction, path=path_to_app , filename=file_name, appname=appName, port=port, ip=ip,username=uname, password=password,inputStream=stream_ip,command_line_params=command_line_params)

			while True: 
				schedule.run_pending() 
				time.sleep(1) 

@app.route('/ScheduleService', methods=['GET', 'POST'])
def ScheduleService():
	data = request.json
	print(data)
	
	# json_data = json.loads(data)
	appName = data['appName']
	# appName = "pre_cool_classroom"
	print("APP NAME ISSSSSSSSSSSSSSSSS--------------------",appName)
	x = threading.Thread(target=startNewProcess, args=(appName,))
	x.start()
	return "scheduled"

#prakash
@app.route('/schedule_algo', methods=['POST'])
def schedule_algo():
	data = request.json
	algo_name = data["function"][0]["algo_name"]
	runtime_ip = data["function"][0]["runtime_ip"]
	runtime_port = data["function"][0]["runtime_port"]
	#rest of the scheduling data can be read from data dictionary similar to parsing XYZ.scheduler_config.json 
	'''
		scheduler logic
	'''
	reply = {}
	reply["status"] = "success"
	return jsonify(reply)

#prakash
'''
Send execute request to runtime
endpoint /start
method = POST
expected return value is
{"algo_name":"XYZ", "params":["x","y"]}
'''

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
        print(" Kafka IP and Port ",kafka_IP_plus_port)
    
    global load_balancer_ip_port
    load_balancer_ip_port = get_ip_port("LoadBalancer_Service")
    
    if __debug__:
        print(" load_balancer_ip_port ",load_balancer_ip_port)

    global scheduler_ip_port
    scheduler_ip_port = get_ip_port("Scheduling_Service")

    if __debug__:
    	print(" scheduler_ip_port ",scheduler_ip_port)

def get_ip_and_port(socket):
    ip_port_temp = socket.split(':')
    print(ip_port_temp)
    return ip_port_temp[0],ip_port_temp[1]


# ------------------- End Get IP Details 


# kafka_ip_port=sys.argv[1]
# scheduler_ip = sys.argv[2]
# scheduler_port = sys.argv[3]
# load_balancer_ip_port = sys.argv[4]
def runScheduler():
	while True:
		schedule.run_pending()
		time.sleep(1)

def spawn_method(scheduler_ip,scheduler_port,load_balancer_ip_port):
	th = threading.Thread(target=runScheduler, args=())
	th.start()

	# signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':

	get_Server_Configuration()
	scheduler_ip,scheduler_port = get_ip_and_port(scheduler_ip_port)
	kafka_ip_port = kafka_IP_plus_port

	spawn_method(scheduler_ip,scheduler_port,load_balancer_ip_port)

	app.run(host=scheduler_ip,port=scheduler_port, debug=True,threaded=True)
