"""
flask 集成 mongodb
"""
import json

from flask import Flask, request, jsonify
import mongoengine as me
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'the_way_to_flask',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


class User(me.Document):
    name = me.StringField()
    email = me.StringField()

    def to_json(self, *args, **kwargs):
        return {
            'name': self.name,
            'email': self.email
        }


def no_name(name):
    return jsonify({'error': f"name '{name}' is not exist!"})


@app.route('/', methods=['GET'])
def query_record():
    name = request.args.get('name')
    user = User.objects(name=name).first()
    return jsonify(user.to_json()) if user else no_name(name)


@app.route('/', methods=['PUT'])
def create_record():
    record = json.loads(request.data)
    user = User(**record)
    # save这里返回的user本身, user.save() is user
    user.save()
    return jsonify(user.to_json())


@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    name = record['name']
    user = User.objects(name=name).first()
    if not user:
        return no_name(name)
    # 原来的user没改变, update返回更改的数量
    user.update(**record)
    return jsonify(User.objects(name=name).first().to_json())


@app.route('/', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    name = record['name']
    user = User.objects(name=name).first()
    if not user:
        return no_name(name)
    # user.delete() is None
    user.delete()
    return jsonify(user.to_json())


if __name__ == '__main__':
    app.run()
