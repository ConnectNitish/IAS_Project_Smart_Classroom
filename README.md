# IAS_Hackathon_2

For Kafka Server : 
------------------
1. Navigate to respective Kafka Folder 

2. To run zookepper
<br />
>bin/zookeeper-server-start.sh config/zookeeper.properties

3.To run Kafka
<br />
>bin/kafka-server-start.sh config/server.properties

------------------------------

Setting Up Docker :

<br />
>curl -fsSL https://get.docker.com -o get-docker.sh
<br />
>sudo sh get-docker.sh

------------------------------

( All Module will be up , not needed to run old script if ran )
<br />
sudo python3 boot_strap.py 127.0.0.1:9939

------------------------------
<br />
( For Individual Module )
<br />
For Running Repository.py 

python3 Repository/app.py 127.0.0.1:9939

For Running Request Manger.py 

python3 requestManager/request_manager.py 127.0.0.1:9939

For Making Up Logging File 

python3 LoggingModule/Platform_Logger.py 127.0.0.1:9092

For Running Load Balancer 

python3 LoadBalancer/LoadBalancer.py 127.0.0.1:9939

For Deployment Manager

python3 deployer/app.py 127.0.0.1:9939

For App_Notification 

python3 Action_Notification/app.py 127.0.0.1:9941

-------------------------------------------------------------------------


-------------------

cd ./Action_Notification

( All Module will be up , not needed to run old script if ran )
<br />
sudo python3 app.py

------------------------

cd ./Testing

-- Up the Sensors 
1. 
python3 udp_sensor.py config_sensor2.json

python3 gateway.py 

---Only for testing "Not Compulsary"
~/kafka/kafka_2.12-2.2.1/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic 127.0.0.1_7888


-- Device Status 

2. 
python3 Device_Status.py Location_Device_Information.json
	-- Command Used : getstatus Room2 AC
					  getstatus Room1 AC
					  getstatus Room1 Access

-- Run Algorithm 

3.

python3 Algorithm/Automated_AC_Service/Automated_AC_Service.py Room1 temperature

python3 Algorithm/Illegal_Access_Detection/Illegal_Access_Detection.py Room1 binary_door_step


