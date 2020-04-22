import mysql.connector
import os,errno
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, send_file,session, jsonify
from flask_bootstrap import Bootstrap
import requests
import sys
import json

app = Flask(__name__)
app.debug = True

@app.route('/db_query_response', methods=['GET', 'POST'])
def db_query_response():
    data = request.json
    print(data)
    cnx = mysql.connector.connect(user='root', password='root12345678',host='127.0.0.1',database='IAS_Smart_Classroom')
    cursor = cnx.cursor(buffered=True)
    query = data
    print("query to excute ",query)
    cursor.execute(query)
    o2 = "None"
    if('select' in query or 'SELECT' in query):
        if(cursor.rowcount > 0):
            o2 =cursor.fetchall()
            print(o2)
    cnx.commit()
    print("line 23")
    cursor.close()
    print("line 24")
    cnx.close()
    print("line 25")
    print(o2)
    #cnx.reset_session()
    return str(o2)

app.run(host="127.0.0.1",debug=True,port=9943,threaded=True)
