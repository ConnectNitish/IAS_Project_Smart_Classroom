import os,sys,time
import threading as th

def execute_command(command,time_sleep):
	os.system(command)
	time.sleep(time_sleep)

repository_host=sys.argv[1]
# only_close = int(sys.argv[2])

list_ports_to_stop = [9000,9939,9935,9932,9931,9930,9941,9942]

# should be taken from "Sensor_data.json"
list_ports_for_iot_sensors = [7881,7882,7883,7884,7891,7892,7893,6745]

print(" Services Port ",list_ports_to_stop,"")
print(" Sensor Port ",list_ports_for_iot_sensors,"")


for item in list_ports_to_stop:
	item = 'sudo kill -9 $(sudo lsof -t -i:'+str(item)+') &'
	print(item)
	execute_command(item,1)

for item in list_ports_for_iot_sensors:
	item = 'sudo kill -9 $(sudo lsof -t -i:'+str(item)+') &'
	print(item)
	execute_command(item,1)


list_commands =  ['python3 Repository/app.py '+repository_host+' &', \
				'python3 LoggingModule/Platform_Logger.py '+repository_host+' &', \
				'python3 requestManager/request_manager.py '+repository_host+' &', \
				'python3 LoadBalancer/LoadBalancer.py '+repository_host+' &', \
				'python3 deployer/app.py '+repository_host+' &', \
				'python3 runtime/app.py '+repository_host+'&', \
				'python3 Sensors/app.py &', \
				'python3 Sensors/gateway.py &']

list_commands.append('python3 Action_Notification/app.py '+ repository_host +' &')
list_commands.append('python3 scheduler/schedule_service.py '+ repository_host +' &')

# list_commands.append('---- Remove Below ')
# list_commands.append('python3 chitta_schedulingService/demoRequestManager.py &')
# list_commands.append('')

execute_command('clear',0.5)

for item in list_commands:
	print(item)
	# execute_command(item,5)



