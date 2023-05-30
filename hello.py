#!/usr/bin/env python

from flask import Flask,jsonify, request,make_response, render_template
import aerospike 
from aerospike import exception as ex

app = Flask(__name__)

config = {
	'hosts' : [('192.168.64.21',3000)]
}
client = aerospike.client(config).connect()

namespace = 'daily_roster'
setname = 'oncall_roster'


def error_responce(error_message, status_code):
	return jsonify({'error': error_message}), status_code



@app.route('/',methods=['GET','POST','PUT','DELETE'])
def index():
	return render_template('index.html')

@app.route('/tasks',methods=['GET', 'POST'])
def create_task():
	data = request.get_json()
	if not data:
		return error_responce('No input data provided', 400)
	try:
		key=(namespace,setname,data['empid'])
		(key_, meta, record) = client.get(key)
		return error_response('Record already exists', 409)
	except ex.RecordNotFound:
		pass
	try:
		client.put((namespace,setname, data['empid']), data)
		return jsonify(data), 200
	except ex.AerospikeError as e:
		app.logger.error(e)
		return error_response(str(e), 500)


@app.route('/tasks/<int:task_id>', methods=['GET'])
def read_task(task_id):
	try:
		key =(namespace, setname, task_id)
		policy={'socket_timeout':300}
		(key_, meta, record) = client.get(key, policy=policy)
		return jsonify(record)
	except ex.RecordNotFound:
		return error_response('Task not found', 404)
	except ex.AerospikeError as e:
		app.logger.error(e)
		return error_response(str(e), 500)


@app.route('/updateTask/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	data = request.get_json()
	if not data:
		return error_response('No input data provided', 400)
	try:
		key =(namespace, setname, task_id)
		client.put(key, data)
		return jsonify(data)
	except ex.RecordNotFound:
		return error_response('Task not Found', 404)
	except ex.AerospikeError as e:
		app.logger.error(e)
		return error_respose(str(e), 500)




@app.route('/deleteTask/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	try:
		key=(namespace, setname, task_id)
		client.remove(key)
		return 'successfully deleted', 200
	except ex.RecordNotFound:
		return error_response('Task not Found', 404)
	except ex.AerospikeError as e:
		app.logger.error(e)
		return error_response(str(e), 500)



if __name__ == '__main__':
	app.run(host='0.0.0.0')

