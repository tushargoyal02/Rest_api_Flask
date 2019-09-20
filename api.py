from flask import Flask, request, jsonify
# to generte random public_id
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt                           #importing jwt to generate token
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisakey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/tushar/Desktop/myflaskapp/todo.db'

db = SQLAlchemy(app)


# creating the model with sqlite
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    admin=db.Column(db.Boolean)

class todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text =  db.Column(db.String(50))
    complete= db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()
    output = []
    for user in users:
        user_data ={}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({"users": output})

@app.route('/user/<public_id>', methods=['GET'] )
def one_user(public_id):
    user = User.query.filter_by(public_id=public_id ).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})
    
    user_data ={}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    
    return jsonify({'user': user_data})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()  #requesting the data in json format
    #hashed_password = generate_password_hash( data['password'], method='sha256')  #generate hash password with sha256

    new_user = User(public_id=data['public_id'], name=data['name'], password=data['password'], admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({ 'message': 'New user is created'})


@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id ).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})
    
    user.admin=True
    db.session.commit()
    return jsonify({'message': 'user is promoted'})

    
    

@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id ).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()
    msg = user + "has been deleted"
    return jsonify({"message": msg})


@app.route('/login')
def login():
    
    auth = request.authorization
    #checking below is having username and password
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify:', 401  , { 'WWW-Authenticate' : 'Basic realm="login required!" '})

    #filter username
    user = User.query.filter_by(name=auth.username).first()
    
    # if user name is not valid
    if not user:
        return make_response('Could not verify:', 401  , { 'WWW-Authenticate' : 'Basic realm="login required!" '})

    if (user.password == auth.password):
        # datetime delta is used to set the validity of token! 
        token = jwt.encode({'public_id': user.public_id,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
         app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    
    # if password is not correct 
    return make_response('Could not verify:', 401  , { 'WWW-Authenticate' : 'Basic realm="login required!" '})
    

if __name__ == "__main__":
    app.run(debug=True)