from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:evangelista4ever@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma=Marshmallow(app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email= fields.String(required=True)
    phone= fields.String(required=True)
    class Meta:
        fields = ('name', 'email', 'phone', 'id')



class ProductSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)
    class Meta:
        fields = ('name', 'price', 'id')



class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)
    class Meta:
        fields = ('username', 'password', 'customer_id', 'id')

class OrderSchema(ma.Schema):
    date =fields.Date(required=True)
    customer_id= fields.Integer(required=True)
    class Meta:
        fields = ('id', 'date', 'customer_id')



order_schema=OrderSchema()
orders_schema=OrderSchema(many=True)

customeraccount_schema= CustomerAccountSchema()
customeraccounts_schema = CustomerAccountSchema(many=True)

customer_schema= CustomerSchema()
customers_schema= CustomerSchema(many=True)

product_schema= ProductSchema()
products_schema = ProductSchema(many=True)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), nullable=False)
    email=db.Column(db.String(320))
    phone=db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer') 



class CustomerAccount(db.Model):
    __tablemane__='Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer= db.relationship('Customer', backref='customer_account', uselist=False)

order_product= db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)


class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders= db.relationship('Order', secondary=order_product, backref=db.backref('products'))



class Order(db.Model):
    __tablename__='Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))


# New customer
@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400  
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'New customer added successfully'}), 201


# All customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customer=Customer.query.all()
    return customers_schema.jsonify(customer)



@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer=Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)


# Update customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer=Customer.query.get_or_404(id)
    try:
        customer_data= customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    customer.name=customer_data['name']
    customer.email=customer_data['email']
    customer.phone=customer_data['phone']
    db.session.commit()
    return jsonify({'message': 'Customer details updated successfully'}), 200


# Delete customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer= Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer removed successfully'}), 200


# Create Customer Account
@app.route('/customeraccount', methods=['POST'])
def add_account():
    try:
        account_data= customeraccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_account = CustomerAccount(username=account_data['username'], password=account_data['password'], customer_id=account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'message': 'New Customer Account added successfully'}), 201   


# Get Customer Accounts
@app.route('/customeraccount', methods=['GET'])
def get_accounts():
    accounts=CustomerAccount.query.all()
    return customeraccounts_schema.jsonify(accounts)


# Update Customer Account
@app.route('/customeraccount/<int:id>', methods=['PUT'])
def update_customeraccount(id):
    account=CustomerAccount.query.get_or_404(id)
    try:
        account_data= customeraccount_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    account.username=account_data['username']
    account.password=account_data['password']
    account.customer_id=account_data['customer_id']
    db.session.commit()
    return jsonify({'message': 'Customer Account details updated successfully'}), 200


# Delete Customer Account
@app.route('/customeraccount/<int:id>', methods=['DELETE'])
def delete_customeraccount(id):
    account= CustomerAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Customer Account removed successfully'}), 200


# Create Product
@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data=product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201


# Product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product=Product.query.get_or_404(id)
    return product_schema.jsonify(product)


# Update Products
@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        print(err.messages), 400
    product.name= product_data['name']
    product.price= product_data['price']
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200


# Delete Product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


# List Products
@app.route('/products', methods=['GET'])
def get_products():
    products= Product.query.all()
    return products_schema.jsonify(products)


# Make order
@app.route('/orders', methods=['POST'])
def make_order():
    try:
        order_data=order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order= Order(date=order_data['date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message':'Order added successfully'}), 201


# Show orders
@app.route('/orders', methods=['GET'])
def get_orders():
    orders=Order.query.all()
    return orders_schema.jsonify(orders)


# Get order by id
app.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    order=Order.query.get_or_404(id)
    return order_schema.jsonify(order)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)