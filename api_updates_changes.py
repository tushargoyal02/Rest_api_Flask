from flask import Flask, request, jsonify, make_response
# to generte random public_id
from flask_sqlalchemy import SQLAlchemy
import jwt                           #importing jwt to generate token
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

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

'''class todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text =  db.Column(db.String(50))
    complete= db.Column(db.Boolean)
    user_id = db.Column(db.Integer)
'''

#creating the decorator for the work with token - authenticate all the request
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None        #empty token

        if 'x-access-token' in request.headers:     # in reques.header is where all token are stored
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'token is missing!'}), 401

        try:
            #decoding the token and give exception if any error:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id= data['public_id']).first()

        except:
            return jsonify({'message': 'token is invalid!'}), 401
        

        return f(current_user, *args, **kwargs)
    
    return decorated



@app.route('/user', methods=['GET'])
@token_required

def get_users(current_user):

    #check if the current_user is admin or not
    if not current_user.admin:
        return jsonify({'message':'cant perform this action'})


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
@token_required
def one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message':'cant perform this action'})

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
@token_required
def create_user(current_user):
    
    if not current_user.admin:
        return jsonify({'message':'cant perform this action'})

    data = request.get_json()  #requesting the data in json format
    hashed_password = generate_password_hash( data['password'], method='sha256')  #generate hash password with sha256
    print("PASSWORD:",hashed_password)
    #new_user = User(public_id=data['public_id'], name=data['name'], password=data['password'], admin=False)
    new_user = User(public_id=data['public_id'], name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({ 'message': 'New user is created'})


@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    
    if not current_user.admin:
        return jsonify({'message':'cant perform this action'})

    user = User.query.filter_by(public_id=public_id ).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})
    
    user.admin=True
    db.session.commit()
    return jsonify({'message': 'user is promoted'})

    
    
# this is working fine with token 
@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    
    if not current_user.admin:
        return jsonify({'message':'cant perform this action'})

    user = User.query.filter_by(public_id=public_id ).first()
    
    if not user:
        return jsonify({'message': 'No user found!'})
    
    db.session.delete(user)
    db.session.commit()
    msg = str(user) + "has been deleted" 
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
        # datetime delta is used to set the validity of token! SECRET_KEy will be used to encode token
        token = jwt.encode({'public_id': user.public_id,
         'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
         app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    
    # if password is not correct 
    return make_response('Could not verify:', 401  , { 'WWW-Authenticate' : 'Basic realm="login required!" '})


if __name__ == "__main__":
    app.run(debug=True)