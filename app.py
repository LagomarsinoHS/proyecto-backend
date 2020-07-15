from flask import Flask, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import db, Empresa, Usuario, Producto, Categoria, Proveedor
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

@app.route('/api/empresas', methods = ['GET', "POST"])
@app.route('/api/empresas/<int:id>', methods = ['GET', "PUT","DELETE"])
#@jwt_required
def empresas(id=None):
    ### Ver Empresas ###
    if request.method == 'GET':
        if not id:
            empresas = Empresa.query.all()
            empresas = list(map(lambda empresa: empresa.serialize(),empresas))
            return jsonify(empresas),200

    ### Ver Empresa por ID ###
        empresa = Empresa.query.get(id)
        if empresa:
            return jsonify(empresa.serialize()),200
        return jsonify({"msg": "Empresa no se encuentra en el sistema"}),400

    ### Eliminar Empresa por ID ###
    if request.method == "DELETE":
        if id:
            empresa= Empresa.query.get(id)
            if empresa:
                empresa.delete()
                return jsonify({"msg": f"Empresa <{empresa.nombre}> eliminada exitosamente!"}),200
            else:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),400

    ### Ingresar Empresa ###
    if request.method == "POST":
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)

        if not nombre:
            return jsonify({"msg": "Nombre de empresa no puede estar vacío"}),400
        if not rut:
            return jsonify({"msg": "Rut de empresa no puede estar vacío"}),400
        if not razon_social:
            return jsonify({"msg": "Razon Social de empresa no puede estar vacío"}),400
        if not rubro:
            return jsonify({"msg": "Rubro de empresa no puede estar vacío"}),400
        
        validaRutExistente = Empresa.query.filter_by(rut = rut).first()
        if validaRutExistente:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}),401

        validaRazonSocialExistente = Empresa.query.filter_by(razon_social = razon_social).first()
        if validaRazonSocialExistente:
            return jsonify({"msg": "Razon social de empresa ya se encuentra registrado"}),401

        empresa = Empresa()
        empresa.nombre = nombre
        empresa.rut = rut
        empresa.razon_social = razon_social
        empresa.rubro = rubro
        empresa.save()

        return jsonify(empresa.serialize()),200
    ### Actualizar Empresa by ID ###
    if request.method == "PUT":
        if id:
            empresaActualizar = Empresa.query.get(id)
            if not empresaActualizar:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}),401


            nombre = request.json.get("nombre", None)
            rut = request.json.get("rut", None)
            razon_social = request.json.get("razon_social", None)
            rubro = request.json.get("rubro", None)

           
            

            rutOcupado = Empresa.query.filter_by(rut = rut).first()
            if rutOcupado and rut is not None:
                return jsonify({"msg": "Rut ya se encuentra registrado."}),401
            razonSocialOcupado = Empresa.query.filter_by(razon_social = razon_social).first()
            if razonSocialOcupado and razon_social is not None:
                return jsonify({"msg" : "Razon social ya se encuentra registrada."}),401

            if nombre is not None:
                if not nombre:
                    return jsonify({"msg": "Nombre no puede ir vacío"}),401
                empresaActualizar.nombre = nombre
            
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío"}),401
                empresaActualizar.rut = rut
            
            if razon_social is not None:
                if not razon_social:
                    return jsonify({"msg": "Razon social no puede ir vacío"}),401
                empresaActualizar.razon_social = razon_social
            
            if rubro is not None:
                if not rubro:
                    return jsonify({"msg": "Rubro no puede ir vacío"}),401
                empresaActualizar.rubro = rubro


            empresaActualizar.update()
            data = {
                "msg": "Empresa Modificada",
                "empresa": empresaActualizar.serialize()
            }
            return jsonify(data),200

@app.route("/api/usuarios", methods = ["GET","POST"])
@app.route("/api/usuarios/<int:id>", methods = ["GET","DELETE", "PUT"])
def usuarios(id = None):
    ### Ver Usuarios ###
    if request.method == "GET":
        if id is None:
            usuarios = Usuario.query.all()
            if not usuarios:
                return jsonify({"msg": "No hay usuarios"})
            usuarios = list(map(lambda usuario: usuario.serialize(), usuarios))
            return jsonify(usuarios),200

    ### Ver Usuario by ID ###
        else:
            usuario = Usuario.query.get(id)
            if not usuario:
                return jsonify({"msg": "No se encuentra usuario."}),401
            return jsonify(usuario.serialize()),200

    ### Eliminar Usuario ###
    if request.method == "DELETE":
        if id:
            usuario = Usuario.query.get(id)
            if usuario:
                usuario.delete()
                return jsonify({"msg": f"Usuario <{usuario.nombre}> eliminado exitosamente."}),200
            else:
                return jsonify({"msg": "Usuario no se encuentra registrado."}),401

    ### Insertar Usuario ###
    if request.method == "POST":
        data = request.get_json()
        if not data["nombre"]:
            return jsonify({"msg":"Nombre no puede estar vacío"}),401
        if not data["apellido"]:
            return jsonify({"msg":"Apellido no puede estar vacío"}),401
        if not data["rut"]:
            return jsonify({"msg":"Rut no puede estar vacío"}),401
        if not data["rol"]:
            return jsonify({"msg":"Rol no puede estar vacío"}),401
        if not data["email"]:
            return jsonify({"msg":"Email no puede estar vacío"}),401
        if not data["password"]:
            return jsonify({"msg":"Password no puede estar vacío"}),401
        if not data["empresa_id"]:
            return jsonify({"msg":"Empresa_id no puede estar vacío"}),401
        
        rut_ocupado = Usuario.query.filter_by(rut = data["rut"]).first()
        if rut_ocupado:
            return jsonify({"msg": "Rut ya se encuentra registrado."}),401
        email_ocupado= Usuario.query.filter_by(email = data["email"]).first()
        if email_ocupado:
            return jsonify({"msg": "Email ya se encuentra registrado."}),401
        
        usuario = Usuario()
        usuario.nombre = data["nombre"]
        usuario.apellido = data["apellido"]
        usuario.rut = data["rut"]
        usuario.rol = data["rol"]
        usuario.email = data["email"]
        usuario.password = bcrypt.generate_password_hash(data["password"])
        usuario.empresa_id = data["empresa_id"] 
        usuario.save()
        usuario.codigo = usuario.generaCodigo()
        usuario.update()

        return jsonify(usuario.serialize()),200
    
    ### Actualizar Usuario ###
    if request.method == "PUT":
        if id:
            usuario_actualizar = Usuario.query.get(id)
            if not usuario_actualizar:
                return jsonify({"msg": "Usuario no se encuentra registrado"})
            
            nombre = request.json.get("nombre", None)
            apellido = request.json.get("apellido", None)
            rut = request.json.get("rut", None)
            rol = request.json.get("rol", None)
            email = request.json.get("email", None)
            password = request.json.get("password", None)
            status = request.json.get("status", None)
        

            rut_ocupado = Usuario.query.filter_by(rut = rut)
            if rut_ocupado and rut is not None:
                return jsonify({"msg": "Rut ya se encuentra registrado."}),401
            email_ocupado = Usuario.query.filter_by(email = email)
            if email_ocupado and email is not None:
                return jsonify({"msg": "Correo ya se encuentra registrado."}),401

            if nombre is not None:
                if not nombre:
                    return jsonify({"msg": "Nombre no puede ir vacío."})
                usuario_actualizar.nombre = nombre

            if apellido is not None:
                if not apellido:
                    return jsonify({"msg": "Apellido no puede ir vacío."})
                usuario_actualizar.apellido = apellido 
                
            if rut is not None:
                if not rut:
                    return jsonify({"msg": "Rut no puede ir vacío."})
                usuario_actualizar.rut = rut

            if rol is not None:
                if not rol:
                    return jsonify({"msg": "Rol no puede ir vacío."})
                usuario_actualizar.rol = rol

            if email is not None:
                if not email:
                    return jsonify({"msg": "Email no puede ir vacío"})
                usuario_actualizar.email = email

            if password is not None:
                if not password:
                    return jsonify({"msg": "Password no puede ir vacío."})
                usuario_actualizar.password = password
            if status is not None:
                if status != False and status != True:
                    return jsonify("Status debe ser true o false")
                usuario_actualizar.status = status
            
            usuario_actualizar.update()
            data = {
                "msg": "Usuario Modificado",
                "usuario": usuario_actualizar.serialize()
            }
            return jsonify(data),200
            
        


        


@app.route("/api/login/", methods = ["POST"])
def login():
    rut = request.json.get("rut", None)
    password = request.json.get("password", None)

    if not rut:
        return jsonify({"msg": "Rut no puede estar vacío"}),400
    if not password:
        return jsonify({"msg": "Password no puede estar vacío"}),400

    userR = Usuario.query.filter_by(rut = rut).first()
    if not userR:
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

@app.route('/api/categorias', methods=['GET', "POST"])
@app.route('/api/categoria/<int:id>', methods=["GET", "PUT"])
def categorias(id = None):
    if request.method == 'GET':
        if not id:
            categorias = Categoria.query.all()
            if categorias:
                categorias = list(map(lambda categoria: categoria.serialize(), categorias))
                return jsonify (categorias),200
            return jsonify({"msg": "Categoria no existente"}),400
        categoria = Categoria.query.get(id)
        if id:
            categoria = Categoria.query.get(id)
            if categoria:
                return (categoria.serialize()),200
            else:
                return jsonify({"msg": "categoria no encontrada"}),400 
    
    if request.method == 'POST':
        nombre = request.json.get("nombre", None)
        if not nombre:
            return jsonify({"msg": "por favor ingresar nombre de categoria valido"})
        name_overlapped = Categoria.query.filter_by(nombre = nombre).first()
        if name_overlapped:
            return jsonify({"msg": "Categoria ya existe"})

        categoria = Categoria()
        categoria.nombre = nombre
        
        categoria.save()    
        return jsonify(categoria.serialize()), 200
    
    if request.method == 'PUT':
        
            nombre = request.json.get("nombre", None)
            
            if not nombre:
                return jsonify({"msg": "Categoria no puede estar vacío"}),400
                        
            categoria_update = Categoria.query.get(id)
            if not categoria_update:
                return jsonify({"msg": "Categoria no se encuentra en el sistema"}),401

           
            categoria_update.nombre = nombre
                    
            categoria_update.update()
            data = {"msg": "Categoria Modificada", "user": categoria_update.serialize()}
            return jsonify(data),200



@app.route("/api/proveedores", methods = ['GET', 'POST'])
@app.route("/api/proveedores/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
def proveedores(id = None):
    
    if request.method == 'GET':
        # DEVUELVE LISTADO CON TODOS LOS PROVEEDORES
        if not id:
            proveedores = Proveedor.query.all()
            proveedores = list(map(lambda proveedor: proveedor.serialize(), proveedores))
            return jsonify(proveedores), 200

        # DEVUELVE DETALLE DE EMPRESA POR ID
        if id:
            proveedor = Proveedor.query.get(id)
            if proveedor:
                return jsonify(proveedor.serialize()), 200
            else:
                return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 400

    # PERMITE CREAR NUEVO PROVEEDOR
    if request.method == 'POST':
        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)
        direccion = request.json.get("direccion", None)
        cuenta_corriente = request.json.get("cuenta_corriente", None)
        banco = request.json.get("banco", None)

        if not nombre:
            return jsonify({"msg": "Nombre no puede estar vacío"}), 400
        if not rut:
            return jsonify({"msg": "Rut no puede estar vacío"}), 400
        if not razon_social:
            return jsonify({"msg": "Razon Social no puede estar vacío"}), 400
        if not rubro:
            return jsonify({"msg": "Rubro no puede estar vacío"}), 400
        if not direccion:
            return jsonify({"msg": "Dirección no puede estar vacío"}), 400
        
        check_rut = Proveedor.query.filter_by(rut = rut).first()
        if check_rut:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 401
        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 401

        proveedor = Proveedor()
        proveedor.nombre = nombre
        proveedor.rut = rut
        proveedor.razon_social = razon_social
        proveedor.rubro = rubro
        proveedor.direccion = direccion
        proveedor.cuenta_corriente = cuenta_corriente
        proveedor.banco = banco

        proveedor.save()    
        return jsonify(proveedor.serialize()), 200
    
    if request.method == 'PUT':
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            return jsonify({"msg": "Empresa no se encuentra en el sistema"}), 401

        nombre = request.json.get("nombre", None)
        rut = request.json.get("rut", None)
        razon_social = request.json.get("razon_social", None)
        rubro = request.json.get("rubro", None)
        direccion = request.json.get("direccion", None)
        cuenta_corriente = request.json.get("cuenta_corriente", None)
        banco = request.json.get("banco", None)

        if not nombre:
            return jsonify({"msg": "Nombre no puede estar vacío"}), 400
        if not rut:
            return jsonify({"msg": "Rut no puede estar vacío"}), 400
        if not razon_social:
            return jsonify({"msg": "Razon Social no puede estar vacío"}), 400
        if not rubro:
            return jsonify({"msg": "Rubro no puede estar vacío"}), 400
        if not direccion:
            return jsonify({"msg": "Dirección no puede estar vacío"}), 400
        
        check_rut = Proveedor.query.filter_by(rut = rut).first()
        if check_rut:
            return jsonify({"msg": "Rut de empresa ya se encuentra registrado"}), 401

        check_razon_social = Proveedor.query.filter_by(razon_social = razon_social).first()
        if check_razon_social:
            return jsonify({"msg":"Razon social de empresa ya se encuentra registrado"}), 401
            
        proveedor.nombre = nombre
        proveedor.rut = rut
        proveedor.razon_social = razon_social
        proveedor.rubro = rubro
        proveedor.direccion = direccion
        proveedor.cuenta_corriente = cuenta_corriente
        proveedor.banco = banco

        proveedor.update()

        data = {
            "msg": "Proveedor Modificado",
            "data": proveedor.serialize()
        }
        return jsonify(data), 200

@app.route('/api/productos', methods = ['GET', "POST"])
@app.route("/api/productos/<int:id>", methods=["GET", "PUT", "DELETE"])
def productos(id=None):
    if request.method == 'GET':
        if id is None:
            productos = Producto.query.all()
            if productos:
                productos = list(map(lambda producto: producto.serialize(),productos))
                return jsonify(productos), 200
            else:
                return jsonify({"msg" : "No hay datos de productos"}), 400
        if id is not None:
            producto = Producto.query.get(id)
            if producto:
                return jsonify(producto.serialize()), 200
            else:
                return jsonify({"msg" : "Producto no encontrado"}), 400

    if request.method == 'POST':
        data = request.get_json()
        if not data["sku"]:
            return jsonify({"msg" : "SKU del producto nuevo no puede estar vacio"})
        
        if not data["descripcion"]:
            return jsonify({"msg" : "Descripcion del producto nuevo no puede estar vacio"})
        
        if not data["codigo_barra"]:
            return jsonify({"msg" : "Codigo de Barra del producto nuevo no puede estar vacio"})
        
        if not data["unidad_entrega"]:
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
        producto.categoria_id = data["categoria_id"] #revisar porque es una FK
        producto.save()
       
        return jsonify({"msg": "Producto creado exitosamente"}), 201

    if request.method == 'PUT':
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({"msg" : "Producto no encontrado"}), 400
        else:
            valor_descripcion = request.json.get("descripcion", None)
            valor_cantidad = request.json.get("cantidad", None)
            valor_precio_venta_unitario = request.json.get("precio_venta_unitario", None)

            producto.descripcion = valor_descripcion
            producto.precio_venta_unitario = valor_precio_venta_unitario
            producto.update()

            return jsonify({"msg": "Producto actualizado exitosamente"}), 201

    if request.method == 'DELETE':
        producto = Producto.query.get(id)
        if producto:
            return jsonify({"msg" : "Producto eliminado exitosamente"})
        else:
            return jsonify({"msg" : "Producto no encontrado"}), 200
            producto.delete()

@app.route("/api/cuadratura_caja", methods = ['GET', 'POST'])
@app.route("/api/cuadratura_caja/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
def cuadratura_caja(id = None):
    if request.method == 'GET':
        if not id:
            cuadraturas_cajas = Cuadratura_Caja.query.all()
            cuadraturas_cajas = list(map(lambda cuadratura_caja: cuadratura_caja.serialize(), cuadraturas_cajas))
            return jsonify(cuadraturas_cajas), 200

        if id:
            cuadratura_caja = Cuadratura_Caja.query.get(id)
            if proveedor:
                return jsonify(cuadratura_caja.serialize()), 200
            else:
                return jsonify({"msg": "id asociado a cuadratura de caja no encontrada"}), 400

    if request.method == 'POST':
        data = request.get_json()
        if not data["usuario_id"]:
            return jsonify({"msg" : "por favor ingresar user_id"})
        
        if not data["admin_id"]:
            return jsonify({"msg" : "por favor ingresar admin_id"})
        
        if not data["fecha_apertura"]:
            return jsonify({})
        
        if not data["fecha_cierre"]:
            return jsonify({})
        
        if not data["monto_apertura"]:
            return jsonify({"msg" : "por favor ingresar monto de apertura"})

        if not data["monto_transferencia"]:
            return jsonify({"msg" : "por favor ingresar monto efectuado por transferencia"})
        
        if not data["monto_efectivo"]:
            return jsonify({"msg" : "por favor ingresar monto efectuado en efectivo"})
        
        if not data["monto_tarjeta"]:
            return jsonify({"msg" : "por favor ingresar monto efectuado por tarjeta"})
        
        if not data["monto_cierre"]:
            return jsonify({})
        
        if not data["diferencia_en_caja"]:
            return jsonify({})

                
        cuadratura_caja = cuadratura_caja()
        cuadratura_caja.usuario_id = data["usuario_id"]
        cuadratura_caja.admin_id = data["admin_id"]
        cuadratura_caja.fecha_apertura = data["fecha_apertura"]
        cuadratura_caja.fecha_cierre = data["fecha_cierre"]
        cuadratura_caja.monto_apertura = data["monto_apertura"]
        cuadratura_caja.monto_transferencia = data["monto_transferencia"]
        cuadratura_caja.monto_efectivo = data["monto_efectivo"]
        cuadratura_caja.monto_tarjeta = data["monto_tarjeta"]
        cuadratura_caja.monto_cierre = data["monto_cierre"]
        cuadratura_caja.diferencia_en_caja = data["diferencia_en_caja"]




        producto.save()
       
        return jsonify({"msg": "Producto creado exitosamente"}), 201

if __name__ == "__main__":
    manager.run()
