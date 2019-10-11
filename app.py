import jwt
import json
from datetime import datetime
import bcrypt
from functools import wraps
import psycopg2
import psycopg2.pool

from flask import Flask
from flask import request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

import util 
import creds 
from db import *

app = Flask(__name__)

# creds.config sets the app.config variables with all the appropriate credentials
creds.config(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)
# Initialize the connection pool for the database
init_db(app)

@app.route('/auth/login', methods=['POST'])
def login():
    content = request.json
    try:
        email = content["email"]
        password = content["password"]
    except:
        return "Must have both email and password in JSON"

    with get_db_and_cursor() as (db, cur):
        cur.execute('SELECT id, password from users WHERE email = %s;', (email,))
        user = cur.fetchone()

        if user is None:
            return util.error_message('Invalid username or password', 401)

        if not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return util.error_message('Invalid username or password', 401)

    # Username and password have been verified
    user_id = util.id_to_string(user[0])
    token = create_access_token({'id': user_id,'email': email})

    return json.dumps({"token": token}, indent=4)

@app.route('/auth/register', methods=['POST'])
def register():
    content = request.json
    try:
        email = content["email"]
        password = content["password"]
    except:
        return "Must have both email and password in JSON"

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('ascii')
    
    with get_db_and_cursor() as (db, cur):
        try:
            cur.execute('INSERT INTO users (email, password) VALUES (%s, %s);', (email, hashed_password))
        except psycopg2.errors.UniqueViolation:
            db.rollback()
            return util.error_message('User with that email already exists', 400)

        cur.execute('SELECT id, password from users WHERE email = %s;', (email,))
        user = cur.fetchone()
        cur.execute('INSERT INTO teams (type) VALUES (%s) RETURNING id;', ('individual',))
        team_id = cur.fetchone()[0]
        cur.execute('INSERT INTO team_users (team, member) VALUES (%s, %s);', (team_id, user[0]))
        db.commit()

    return json.dumps({'msg': 'successful'}, indent=4)

@app.route('/teams', methods=['GET', 'POST'])
@jwt_required
def list_teams():
    current_user = get_jwt_identity()
    current_user_id = util.id_from_string(current_user['id'])
    
    with get_db_and_cursor() as (db, cur):
        if request.method == 'GET':
            cur.execute('SELECT teams.id, teams.name, teams.type FROM teams JOIN team_users ON team_users.team = teams.id WHERE team_users.member = %s;', (current_user_id,))
            results = cur.fetchall()
            cur.close()
            return json.dumps(results, indent=4) + '\r\n'
        if request.method == 'POST':
            try:
                team_name = request.json['name']
                team_type = request.json['type']
            except:
                return util.error_message('Must provide both a name and a type for the team', 412)

            cur.execute('INSERT INTO teams (name, type) VALUES (%s, %s) RETURNING id;', (team_name, team_type))
            team_id = cur.fetchone()[0]
            cur.execute('INSERT INTO team_users (team, member) VALUES (%s, %s);', (team_id, current_user_id))
            db.commit()

            return json.dumps({'location': '/teams/%s' % util.id_to_string(team_id)}) + '\r\n'

@app.route('/games')
@jwt_required
def list_games():
    current_user = get_jwt_identity()
    current_user_id = util.id_from_string(current_user['id'])
    
    with get_db_and_cursor() as (db, cur):
        if request.method == 'GET':
            cur.execute('SELECT * FROM games JOIN game_teams ON game_teams.game = games.id JOIN team_users ON team_users.team = game_teams.team WHERE team_users.member = %s;', (current_user_id,))
            results = cur.fetchall()
            return json.dumps(results, indent=4) + '\r\n'


