#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate

from models import db, Episode, Guest, Appearance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return f'<h1>Welcome to Late Show!<h1>'

@app.route('/episodes', methods=['GET'])
def episodes():
    if request.method == 'GET':
        all_episodes = [ ep.to_dict() for ep in Episode.query.all() ]
        return make_response( all_episodes, 200)
    
@app.route('/episodes/<int:id>', methods=['GET', 'DELETE'])
def episode_by_id(id):
    found_ep = Episode.query.filter(Episode.id == id).first()
    if not found_ep:
        return make_response({"error": "404: Episode not found"}, 404)
    elif request.method == 'GET':
        return make_response(found_ep.to_dict(rules=('guests.name','guests.id', 'guests.occupation')), 200)
    
    elif request.method == 'DELETE':
        db.session.delete(found_ep)
        db.session.commit()
        return make_response({}, 204)
    
@app.route('/guests', methods=['GET'])
def guests():
    if request.method == 'GET':
        all_guests = [ gu.to_dict() for gu in Guest.query.all() ]
        return make_response(all_guests, 200)
    
@app.route('/appearances', methods=['POST'])
def appearances():
    data = request.get_json()
    try:
        new_appearance = Appearance(
            rating = data['rating'],
            episode_id = data['episode_id'],
            guest_id = data['guest_id']
        )
        db.session.add(new_appearance)
        db.session.commit()
        return make_response(new_appearance.to_dict(rules=('episode', 'guest', '-episode_id', '-guest.id')), 201)
    except ValueError:
        return make_response({ "error": "400: Validation error."}, 400)
    
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)