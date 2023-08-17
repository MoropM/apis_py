from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import pdfplumber
import re

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
# https://sqlitebrowser.org/dl/
# https://pypi.org/project/pdfplumber/



# Configuración Básica
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


@app.route('/contact', methods = ['POST'])
def create_contacts():
    data = request.get_json()
    contact = Contact( name = data['name'], email = data['email'], phone = data['phone'])
    db.session.add(contact)
    db.session.commit()
    return jsonify({ "message": "Contacto creado con éxito", "contact": contact.serialize()}), 201


@app.route('/contact/<int:id>', methods = ['GET'])
def get_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'message': "Contacto no encontrado"}), 404
    return jsonify(contact.serialize())


@app.route('/contact/<int:id>', methods = ['PUT', 'PATCH'])
def put_contact(id):
    contact = Contact.query.get_or_404(id)

    data = request.get_json()

    if 'name' in data:
        contact.name = data['name']
    if 'email' in data:
        contact.email = data['email']
    if 'phone' in data:
        contact.phone = data['phone']

    # Guardar los cambios en la base de datos
    db.session.commit()

    # if not contact:
    #     return jsonify({'message': "Contacto no encontrado"}), 404

    return jsonify({ "message": "Contacto actualizado con éxito", "contact": contact.serialize()})


@app.route('/contact/<int:id>', methods = ['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'message': "Contacto no encontrado"}), 404
    
    # Eliminamos el contacto desde la BD
    db.session.delete(contact)
    db.session.commit()

    return jsonify({ "message": "Contacto eliminado con éxito", "contact": contact.serialize()})



def parseMessage(message:str = '', description:str = '', data = [], codeHttp:int = 200):
    return jsonify({
        "message": message,
        "description": description,
        "data": data
    }), codeHttp

@app.route('/initialPDF', methods = ['GET','POST'])
def explorePDF():
    # Obtenemos el archivo y lo almacenamos en el proyecto
    if request.files['pdfDocto']:
        filePdf = request.files['pdfDocto']
        listTables = getTablesPdf(filePdf)
        result = processTables(listTables)
        return parseMessage(result['message'], result['description'], result['data'], result['code'])

    return parseMessage("No se encontró un archivo para procesar", "Seleccione una archivo .pdf para procesar", [], 400)
    # return jsonify({ "message": "Ingresamos", "data": filePdf })

# Obtenemos las tablas existentes en el PDF para validar el texto
def getTablesPdf(filePdf):
    tablesList = []
    with pdfplumber.open(filePdf) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            tablesDocto = page.extract_tables()

            if tablesDocto is not None:
                if len(tablesDocto) > 0:
                    tablesList.append(tablesDocto)
    return tablesList

"""
    Obtenemos las tablas generales del documento
    Son 2 regularmente
"""
def processTables(listTables):
    response = {
        "message": '',
        "description": '',
        "data": [],
        "code": 200,
    }

    tableByItem = []
    for indexTable in range(len(listTables)):
        table = listTables[indexTable]
        if table is not None:
            for indexTbl in range(len(table)):
                itemTbl = table[indexTbl]
                if itemTbl is not None:
                    tableByItem.append(itemTbl)

    # Verificamos que el PDF pertenezca a una Constancia fiscal
    firstTable = tableByItem[0][0]
    for indexList in range(len(firstTable)):
        item = firstTable[indexList]
        if item is not None:
            if item != 'CÉDULA DE IDENTIFICACIÓN FISCAL':
                # break
                response['message'] = "El PDF escaneado no es una Constancia de situción fiscal"
                response['data'] = tableByItem
                return response

    newList = []
    listIdentificationData = []
    registeredAddressInformation = []
    economicActivities = []
    regimes = []
    obligations = []
    for index in range(len(tableByItem)):
        if index > 0 :
            listTbl = tableByItem[index]
            if listTbl is not None:
                #newList.append(listTbl)
                firstItem = listTbl[0]
                # print(f"{index}:: \n {firstItem}\n")
                if "Datos de Identificación del Contribuyente" in firstItem[0]:
                    del listTbl[0]
                    # "title": "Datos de Identificación del Contribuyente",
                    auxList = listTbl
                    listTbl = []
                    newJson = {}
                    for iItem in range(len(auxList)):
                        arrayItem = auxList[iItem]
                        print(arrayItem)
                        word = arrayItem[0]
                        if "CURP" in word or "RFC" in word:
                            title = word
                        else:
                            partes = re.findall('[A-Z][^A-Z]*', word)
                            title = ' '.join(partes)

                        info = arrayItem[1]
                        newJson = { "title":title, "data": info }
                        listTbl.append(newJson)

                    firstData = { "taxpayer_data": listTbl }
                    listIdentificationData.append(firstData)
                if "Datos del domicilio registrado" in firstItem[0]:
                    del listTbl[0]
                    auxList = listTbl
                    listTbl = []
                    for iItem in range(len(auxList)):
                        arrayItem = auxList[iItem]
                        newJson = {}
                        for indexArr in range(len(arrayItem)):
                            newArrItem = arrayItem[indexArr].split(':')
                            word = newArrItem[0]
                            partes = re.findall('[A-Z][^A-Z]*', word)
                            title = ' '.join(partes)
                            info = newArrItem[1]
                            newJson = { "title":title, "data": info }

                        listTbl.append(newJson)

                    secondData = { "address_data": listTbl }
                    registeredAddressInformation.append(secondData)
                    # registeredAddressInformation.append(listTbl)
                if "YCalle" in firstItem[0]:
                    inAddressData = registeredAddressInformation[0]['address_data']
                    arrayItem = listTbl[1]
                    listTbl = []
                    for indexArr in range(len(arrayItem)):
                        newJson = {}
                        newArrItem = arrayItem[indexArr].split(':')
                        word = newArrItem[0]
                        partes = re.findall('[A-Z][^A-Z]*', word)
                        title = ' '.join(partes)
                        info = newArrItem[1]
                        newJson = { "title":title, "data": info }
                        listTbl.append(newJson)

                    inAddressData.append(listTbl)
                    # registeredAddressInformation['address_data'].append(listTbl)
                    pass
                if "Actividades Económicas:" in firstItem[0]:
                    del listTbl[0]

                    titles = listTbl[0]
                    infos = listTbl[1]
                    listTbl = []
                    for iItem in range(len(titles)):
                        # listTbl.append([ titles[iItem], info[iItem] ])
                        wordT = titles[iItem]
                        partesT = re.findall('[A-Z][^A-Z]*', wordT)
                        title = ' '.join(partesT)

                        wordI = infos[iItem]
                        partesI = re.findall('[A-Z][^A-Z]*', wordI)
                        info = ' '.join(partesI)
                        listTbl.append({ "title": title, "data": info })

                    thirdData = { "economicActivities": listTbl }
                    economicActivities.append(thirdData)
                    # economicActivities.append(listTbl)
                if "Regímenes:" in firstItem[0]:
                    del listTbl[0]
                    titles = listTbl[0]
                    info = listTbl[1]
                    listTbl = []
                    for iItem in range(len(titles)):
                        # listTbl.append([ titles[iItem], info[iItem] ])
                        listTbl.append({ "title":titles[iItem], "data": info[iItem] })
                    fourthData = { "regimes": listTbl }
                    regimes.append(fourthData)
                    # regimes.append(listTbl)
                # if "Obligaciones:" in firstItem[0]:
                #     obligations.append(listTbl)

                # print(f"{index}:: \n {firstItem[0]}\n\n")


    # newList = [listIdentificationData[0], registeredAddressInformation[0], economicActivities[0], regimes[0], obligations[0]]

    newList = [listIdentificationData[0], registeredAddressInformation[0], economicActivities[0], regimes[0]]

    response['message'] = "Archivo procesado"
    response['data'] = newList
    return response





# Iniciar proyecto en Debug
# flask --app app --debug run


# Crear archivo de requerimientos
# pip freeze > requirements.txt