from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
# https://sqlitebrowser.org/dl/


# COnfiguración Ba´sica
app = Flask(__name__)
# Ruta para MAC/Linux
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/contacts.db'
# Ruta para Windows
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:\\doctos\\proyectos\\python\\apis_py\\api-contact\\instance\\contacts.db'
db = SQLAlchemy(app)


# Crear modelo de base de datos
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

# Crear las tablas en la base de datos
# with app.app_context():
#     db.create_all()


# Crear Rutas

@app.route('/contacts', methods = ['GET'])
def get_contacts():
    contacts = Contact.query.all()

    # list_contact = []
    # for contact in contacts:
    #     list_contact.append(contact.serialize())

    return jsonify({'contacts': [ contact.serialize() for contact in contacts ]})


@app.route('/contacts', methods = ['POST'])
def create_contacts():
    data = request.get_json()
    contact = Contact( name = data['name'], email = data['email'], phone = data['phone'])
    db.session.add(contact)
    db.session.commit()
    return jsonify({ "message": "Contacto creado con éxito", "contact": contact.serialize()}), 201


@app.route('/initialPDF', methods = ['GET','POST'])
def explorePDF():
    # Obtenemos el archivo y lo almacenamos en el proyecto
    # if request.files['nombreCampo']:
        # variable = request.files['nombreCampo']
        # variable.save(f'static/docs/{secure_filename(variable.filename)}')

    pass



# Iniciar proyecto en Debug
# flask --app app --debug run
