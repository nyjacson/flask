from flask import Flask, jsonify, request
from redis import Redis, RedisError
import json
import os
import socket

# Redis に接続
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

@app.route("/")
def index():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostnames:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)

@app.route('/api/<name>', methods=['GET'])
def get_json(name):
  NAME = name
  result = {
    "data": {
      "id": 1,
      "name": NAME
    }
  }
  return jsonify(result)

@app.route('/post', methods=['POST'])
def post_json():
  try:
    json = request.get_json()
    NAME = json['name']
    result = {
      "data": {
        "id": 2,
        "name": NAME
      }
    }
    return jsonify(result) 
  except Exception as e:
    result = error_handler(e)
    return result

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)

def error_handler(error):
  exception_type = error.__class__.__name__
  exception_message = str(error)
  result_error = { 
      "error": {
      "type": exception_type, 
      "message": exception_message
      }
  }
  return jsonify(result_error)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
