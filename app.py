from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo

from werkzeug.security import generate_password_hash, check_password_hash

from bson import json_util

from config import MONGO_URI

from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
app.config['DEBUG'] = True

app_context = app.app_context()
app_context.push()

mongo = PyMongo(app)

col_users = mongo.db.users
col_questions = mongo.db.questions

@app.route('/', methods=['GET'])
def index():
    res = col_users.find({})
    return json_util.dumps(list(res)), 201

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    col_users.insert_one(data)
    return 'usuario ' + data['username'] + ' criado.', 201

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    return username, 200

# rota para exemplificar como utilizar obter variaveis
# de url. teste acessando 
# http://localhost:8088/questions/search?disciplina=BancoDeDados 
@app.route('/questions/search', methods=['GET'])
def search():
    disciplina = request.args.get('disciplina')
    return disciplina, 200

##Atividade - 00
@app.route('/v1/users', methods=['POST'])
def create_user_v1():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    usuario_encontrado = col_users.find_one({'username' : data['username']})
    if not usuario_encontrado:
        col_users.insert_one(data)
        return 'usuario ' + data['username'] + ' criado.', 201
    else : 
        return 'usuario '+ data['username'] + ' já existente.', 203

##Atividade - 01 
@app.route('/v1/users/<username>', methods=['GET'])
def get_user_v1(username):
    usuario_encontrado = col_users.find_one({'username' : username})
    if usuario_encontrado:
        return json_util.dumps(usuario_encontrado), 200
    else : 
        return 'usuario '+ username + ' não encontrado', 404

##Atividade - 02
@app.route('/v1/authenticate', methods=['POST'])
def authenticate_user_v1():
    data = request.get_json()
    if not request or 'username' not in data or 'password' not in data:
        return 'dados não informados', 401
    else:
        usuario_encontrado = col_users.find_one({"username" : data['username']})
        if usuario_encontrado and check_password_hash(usuario_encontrado['password'], data['password']):
            return 'usuario e senha válidos.', 200
        else:            
            return 'usuario ' + data['username'] + ' e/ou senha não encontrado.', 403

##Atividade - 03
@app.route('/v1/users/update', methods=['POST'])
def update_user_v1():
    data = request.get_json()
    if not request or 'username' not in data or 'email' not in data or 'phones' not in data:
        return 'Dados não informados e/ou não encontrados para atualização', 401
    else:
        usuario_encontrado = col_users.find_one({"username" : data['username'] })
        if usuario_encontrado:
            col_users.update({'username' : data['username']}, {'$set':{'email': data['email'], 'phones' : data['phones']}})
            return 'Dados atualizados com sucesso', 201
        else:
            return 'Usuário não encontrado', 403

##Atividade - 04
@app.route('/v1/users/<username>', methods=['PATCH'])
def update_password_user_v1(username):
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    usuario_encontrado = col_users.find_one({'username' : username})
    if usuario_encontrado:
        col_users.update({'username' : username}, {'$set':{'password': data['password']}})
        return 'usuario ' + username + ' senha definida com sucesso.', 201
    else : 
        return 'usuario '+ username + ' não encontrado para redefinição de senha', 404

##Atividade - 05 
@app.route('/v1/questions/<question_id>', methods=['GET'])
def get_questions_v1(question_id):
    questao_encontrada = col_questions.find_one({'_id' : ObjectId(question_id)})
    if questao_encontrada:
        return json_util.dumps(questao_encontrada), 200
    else : 
        return 'Questão '+ question_id + ' não encontrada', 404

##Atividade - 06
@app.route('/v1/questions/<question_id>', methods=['POST'])
def insert_comment_question_v1(question_id):
    data = request.get_json()
    if not question_id or not request or 'username' not in data or 'message' not in data:
        return 'Dados não informados e/ou não encontrados para atualização', 401
    else:
        usuario_encontrado = col_users.find_one({"username" : data['username'] })
        questao_encontrada = col_questions.find_one({'_id' : ObjectId(question_id)})
        if not usuario_encontrado or not questao_encontrada:
            return 'Usuário e/ou questão não encontrados', 403
        else:
            col_questions.update({'_id' : ObjectId(question_id)}, {'$set': {'comentarios' : data}})
            return 'Comentário inserido com sucesso', 201

##Atividade - 07
@app.route('/v1/questions/search', methods=['GET'])
def search_question_v1():
    disciplina = request.args.get('disciplina')
    ano = request.args.get('ano')

    if not disciplina and not ano:
        return 'Dados enviados estão inválidos', 400
    else:
        where = {}
        where['disciplina'] = disciplina
        where['ano'] = ano
        print(where)
        questions_encontradas = col_questions.find(where)
        if questions_encontradas:
            return json_util.dumps(list(questions_encontradas)), 200
        else:
            return 'Dados não encontrados', 404