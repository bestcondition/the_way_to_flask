"""
REST api by flask
"""
import json
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)


# route返回字符串, content-type默认是text/html类型的
# @app.route('/')
# def index():
#     return json.dumps({'name': 'bestcondition', 'email': 'admin@bestcondition.cn'})

# 用flask.jsonify去dumps对象可以直接返回application/json类型
# @app.route('/')
# def index():
#     return jsonify({'name': 'bestcondition', 'email': 'admin@bestcondition.cn'})


class JsonFileDatabase:
    ENCODING = 'utf-8'

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.data: list = []
        self.load_file()

    def load_file(self):
        text = '[]'
        if self.file_path.is_file():
            _text = self.file_path.read_text(encoding=self.ENCODING)
            if _text.strip():
                text = _text
        self.data = json.loads(text)

    def save(self):
        self.file_path.write_text(
            data=json.dumps(self.data),
            encoding=self.ENCODING,
        )

    def add_one(self, record):
        self.data.append(record.copy())
        self.save()
        return True

    def search_one(self, k, v, copy=True):
        for record in self.data:
            if k in record and record[k] == v:
                return record.copy() if copy else record
        return False

    def update_one(self, k, v, record):
        old_record: dict = self.search_one(k, v, copy=False)
        if not old_record:
            return False
        old_record.update(record)
        self.save()
        return old_record

    def delete_one(self, k, v):
        old_record: dict = self.search_one(k, v, copy=False)
        if not old_record:
            return False
        old_record.clear()
        self.save()
        return True


db = JsonFileDatabase('email.db.json')


def no_name(name):
    return jsonify({'error': f'name {name} is not exist!'})


@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    record = db.search_one('name', name)
    if record:
        return jsonify(record)
    else:
        return no_name(name)


@app.route('/', methods=['PUT'])
def create_records():
    record = json.loads(request.data)
    db.add_one(record)
    return jsonify(record)


@app.route('/', methods=['POST'])
def update_records():
    record = json.loads(request.data)
    name = record['name']
    new_record = db.update_one('name', name, record)
    if new_record:
        return jsonify(new_record)
    else:
        return no_name(name)


@app.route('/', methods=['DELETE'])
def delete_records():
    record = json.loads(request.data)
    name = record['name']
    if db.delete_one('name', name):
        return jsonify(record)
    else:
        return no_name(name)


app.run()
