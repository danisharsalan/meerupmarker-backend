from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import ast
from bson import Binary, Code
from bson.json_util import dumps

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'meetup_marker_db'
app.config['MONGO_URI'] = 'mongodb://danish:admin1@ds046357.mlab.com:46357/meetup_marker_db'

mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message' : 'It works'})

@app.route('/add')
def addMe():
    user = mongo.db.users
    user.insert({
        'user_id' : '1039810918392',
        'firstname' : 'fake',
        'lastname' : 'name',
        'bio' : 'this is a fake user, for testing purposes',
        'picurl' : 'http://www.danisharsalan.github.io'
    })
    return "Added user!"

@app.route('/add_event', methods=["POST"])
def addEvent():
    event = mongo.db.events
    event.insert({
        'user_id' : '1039810918392',
        'lat' : '42.102019',
        'long' : '68.293290',
        'num_people' : '1',
        'basketball' : 'False',
        'soccer' : 'False',
        'work_out' : 'False',
        'tennis' : 'True',
        'racquetball' : 'False',
        'hockey' : 'False',
        'users_joined' : [
            '1039810918394'
        ],
        'spots_open' : '0'
    })
    return "Added event!"

@app.route('/event_registered', methods=['GET'])
def event_registered():
    user_id = request.args.get('user_id')
    if check_event_registered(user_id):
        return "true"
    else:
        return "false"

@app.route('/get_event_by_host', methods=['GET'])
def get_event_by_host():
    user_id = request.args.get('user_id')
    event = mongo.db.events
    cur = event.find_one({'user_id' : user_id})
    return dumps(cur)

@app.route('/get_event_by_joined', methods=['GET'])
def get_event_by_joined():
    user_id = request.args.get('user_id')
    event = mongo.db.events
    cur = event.find_one({'users_joined' : int(float(user_id))})
    return dumps(cur)

@app.route('/get_user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    user = mongo.db.users
    cur = user.find({'user_id' : user_id})
    return dumps(cur)

@app.route('/register_event', methods=['POST'])
def register_event():
    # """Register event into database or update its credentials"""
    user_id = request.form['user_id']
    lat = request.form['lat']
    long = request.form['long']
    num_people = request.form['num_people']
    basketball = request.form['basketball']
    soccer = request.form['soccer']
    work_out = request.form['work_out']
    tennis = request.form['tennis']
    racquetball = request.form['racquetball']
    hockey = request.form['hockey']
    users_joined = request.form['users_joined']
    users_joined = ast.literal_eval(users_joined)
    spots_open = int(num_people) - len(users_joined)

    # check if the user is already registered
    if check_event_registered(user_id):
        event = mongo.db.events
        event.update_one({
            "user_id": user_id
        },{
            '$set': {
            'lat' : lat,
            'long' : long,
            'num_people' : num_people,
            'basketball' : basketball,
            'soccer' : soccer,
            'work_out' : work_out,
            'tennis' : tennis,
            'racquetball' : racquetball,
            'hockey' : hockey,
            'users_joined' : users_joined,
            'spots_open' : spots_open
            }
        },
            upsert=False
        )
        return "Already registered"

    # execute an insert into the DB
    event = mongo.db.events
    event.insert({
        'user_id' : user_id,
        'lat' : lat,
        'long' : long,
        'num_people' : num_people,
        'basketball' : basketball,
        'soccer' : soccer,
        'work_out' : work_out,
        'tennis' : tennis,
        'racquetball' : racquetball,
        'hockey' : hockey,
        'users_joined' : users_joined,
        'spots_open' : spots_open
    })
    return "Done"

@app.route('/register_for_event', methods=['POST'])
def register_for_event():
    host_id = request.form['host_id']
    user_id = request.form['user_id']
    if already_in_event(host_id, user_id):
        print("already signed up")
        return "Done"
    else:
        event = mongo.db.events
        spots_open = event.find({'users_joined' : user}).size() + 1
        event.update_one({
            "user_id": user_id
        },{
            '$set': {
                'users_joined' : users_joined,
                'spots_open' : spots_open
            }
        },
            upsert=False
        )


def already_in_event(host_id, user_id):
    event = mongo.db.events
    if event.find({'user_id' : host_id, 'users_joined' : user_id}).count() > 0:
        return True
    else:
        return False

def check_event_registered(user_id):
    event = mongo.db.events
    if event.find({'user_id' : user_id}).count() > 0:
        return True
    else:
        return False

@app.route('/is_registered', methods=['GET'])
def is_registered():
    user_id = request.args.get('userId')
    if check_registered(user_id):
        return "true"
    else:
        return "false"

@app.route('/register', methods=['POST'])
def register_route():
    # """Register user into database or update their credentials"""
    user_id = request.form['userId']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    bio = request.form['bio']
    pic_url = request.form['picUrl']

    # check if the user is already registered
    if check_registered(user_id):
        user = mongo.db.users
        user.update_one({
            "user_id": user_id
        },{
            '$set': {
            'firstname' : firstname,
            'lastname' : lastname,
            'bio' : bio,
            'picurl' : pic_url
            }
        },
            upsert=False
        )
        return "Already registered"

    # execute an insert into the DB
    user = mongo.db.users
    user.insert({
        'user_id' : user_id,
        'firstname' : firstname,
        'lastname' : lastname,
        'bio' : bio,
        'picurl' : pic_url
    })
    return "Done"

def check_registered(user_id):
    user = mongo.db.users
    if user.find({'user_id' : user_id}).count() > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(debug=True, port=8000)