import mysql.connector
import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json


query = "INSERT INTO SCHEDULER (algoname, status, start_time, end_time, ip_port, processid) VALUES ('ac', 'to be sched', '11', '13', 'ipport', 'pid'); "
query = "select * from SCHEDULER;"
url_db_service  = "http://127.0.0.1:9943/db_query_response"
r=requests.post(url=url_db_service,json=query)
print(r)
if (r.ok):
    print (r.text)
