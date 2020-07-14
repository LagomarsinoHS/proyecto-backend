from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Producto
from config import Development

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(Development)
db.init_app(app)
Migrate(app, db)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'msg': 'The {} token has expired. Please Login Again'.format(token_type)
    }), 401

@app.route('/')
def home():
    return 'Hola mundo'

@app.route('/api/empresas', methods = ['GET'])
def empresas():
    if request.method == 'GET':
        empresas = Empresa.query.all()
        empresas = list(map(lambda empresa: empresa.serialize(),empresas))
        print(empresas)
        return jsonify(empresas),200

@app.route("/api/login/", methods = ["POST"])
def login():
    rut = request.json.get("rut", None)
    password = request.json.get("password", None)

    if not rut:
        return jsonify({"msg": "Rut no puede estar vacío"}),400
    if not password:
        return jsonify({"msg": "Password no puede estar vacío"}),400

    userR = Usuario.query.filter_by(rut = rut).first()
    if not user:
        return jsonify({"msg":"Rut o contraseña inválido."}),401
    if not bcrypt.check_password_hash(userR.password, password):
        return jsonify({"msg":"Rut o contraseña inválido."}), 401

    expires = datetime.timedelta(hour=24)
    access_token = create_access_token(identity=userR.rut, expires_delta=expires)

    data = {
        "access_token": access_token,
        "user": userR.serialize()
    }
    
    return jsonify(data), 200

@app.route('/api/productos', methods = ['GET'])
@app.route("/api/productos/<nombre_producto>", methods=["GET", "POST", "PUT", "DELETE"])
def productos(nombre_producto = None):
    if request.method == 'GET':
        if nombre_producto is None:
            productos = Producto.query.all()
            if productos:
                productos = list(map(lambda producto: producto.serialize(),productos))
                return jsonify(productos),200
            else:
                return jsonify({"msg" : "No hay datos de productos"}),400
        if nombre_producto is not None:
            producto = Producto.query.filter(Producto.descripcion.ilike(f"%{nombre_producto}")).first()
            if producto:
                return jsonify(producto.serialize()),200
            else:
                return jsonify({"msg" : "Producto no encontrado"})
    if request.method == 'POST':
        data = request.get_json()
        if data["sku"]=="" or data["sku"] == None:
            return jsonify({"msg" : "SKU del producto nuevo no puede estar vacio"})
        
        if data["descripcion"]=="" or data["descripcion"] == None:
            return jsonify({"msg" : "Descripcion del producto nuevo no puede estar vacio"})
        
        if data["codigo_barra"]=="" or data["codigo_barra"] == None:
            return jsonify({"msg" : "Codigo de Barra del producto nuevo no puede estar vacio"})
        
        if data["unidad_entrega"]=="" or data["unidad_entrega"] == None:
            return jsonify({"msg" : "Unidad de Entrega del producto nuevo no puede estar vacio"})
        
        if not data["categoria_id"]:
            return jsonify({"msg" : "Categoría del producto nuevo no puede estar vacio"})

        producto = Producto.query.filter_by(descripcion = data["descripcion"]).first()
        if producto:
            return jsonify({"msg" : "Producto ya existe"})
        
        producto = Producto()
        producto.sku = data["sku"]
        producto.descripcion = data["descripcion"]
        producto.codigo_barra = data["codigo_barra"]
        producto.unidad_entrega = data["unidad_entrega"]
        producto.categoria_id = data["categoria_id"]

        db.session.add(producto)
        db.session.commit()

        return jsonify({"msg": "Producto creado exitosamente"}), 201

if __name__ == "__main__":
    manager.run()
