from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow
import os

app= Flask(__name__)

# creating base file for database i.e current directory
basedir =  os.path.abspath( os.path.dirname(__file__) )

#databases work -  and file name will be [db.sqlite]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

# to stop notification for changes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# intialize database
db = SQLAlchemy(app)

# intialize ma
ma = Marshmallow(app)

#Product class
    # Model will give predefined methods
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True )
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)


    # calling constructor
    def __init__(self, name, description, price, qty):

        self.name = name
        self.description = description
        self.price = price
        self.qty = qty



# we are now creating product schema
class ProductSchema(ma.Schema):

    class Meta: 

        fields = ('id', 'name', 'description', 'price', 'qty' )

product_schema  = ProductSchema(strict=True)

#for multiple product 
products_schema = ProductSchema(many=True, strict=True)

  
''' Open Terminal 
and import db from app
call -  db.create_all()'''



# create a product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    
    new_product = Product(name, description, price, qty)
    #print(new_product)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)




# get all product
@app.route('/products', methods=['GET'])
def get_products():

    all_products = Product.query.all()
    result = products_schema.dump(all_products)

    return jsonify(result.data) 



# info for specific product
@app.route('/product/<id>', methods=['GET'])
def get_product(id):

    product = Product.query.get(id)
    return product_schema.jsonify(product) 



#  -------
# update product info
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):

    # fetch product
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name= name
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)


# ------
# to delete
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):

    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product) 


#@app.route('/', methods=['GET'])
#def get():
#    return jsonify({'msg':"hellow world"})
            
if __name__ == "__main__":
    app.run(debug=True)