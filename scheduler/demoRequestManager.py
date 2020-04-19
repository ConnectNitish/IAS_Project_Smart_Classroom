from flask import Flask, request, render_template
import requests
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')
@app.route('/rm', methods=['GET','POST'])
def rm():
    result = ''
    if request.method == 'POST':
        result = request.form
    print(result)
    print(result["app_name"])
    appn = "pre_cool_classroom"
    appn = "turn_off_lights"
    appn = result["app_name"]
    datatosend = {}
    datatosend['appName'] = appn
    url_schedule_service = "http://127.0.0.1:9942/ScheduleService"
    r=requests.post(url=url_schedule_service,json=datatosend)

    print("msg to sc ",url_schedule_service)
    return "Your request has been received"

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9999,debug=True)

# from flask import Flask           # import flask
# app = Flask(__name__)             # create an app instance

# @app.route("/")                   # at the end point /
# def hello():                      # call method hello
#     return "Hello World!"         # which returns "hello world"
