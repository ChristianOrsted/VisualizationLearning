from flask import Flask, request

app = Flask(__name__)

@app.route("/test")
def task():
    result1 = function1()
    result2 = function2()
    return f"{result1} and {result2}"

def function1():
    return "Task 1 completed"

def function2():
    return "Task 2 completed"

@app.route("/print")
def myPrint():
    username = request.args.get("username")
    password = request.args.get("password")
    return f"username: {username} password: {password}"

@app.route("/post", methods = ['POST', 'GET'])
def getPost():
    username = request.form.get("username")
    password = request.form.get("password")

    index_1 = request.args.get("index_1")
    index_2 = request.args.get("index_2")

    json_1 = request.json.get("json_1")
    json_2 = request.json.get("json_2")
    return f"username: {username}<br>password: {password}<br>index_1: {index_1}<br>index_2: {index_2}<br>json_1: {json_1}<br>json_2: {json_2}"

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port = "7777")