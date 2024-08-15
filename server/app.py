# server/app.py
#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.orm import scoped_session
from models import db, Earthquake

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Using scoped_session to create a session
session = scoped_session(db.session)

@app.route('/')
def index():
    body = {'message': 'Flask SQLAlchemy Lab 1'}
    return make_response(jsonify(body), 200)

@app.route('/earthquakes/<int:id>', methods=['GET'])
def get_earthquake(id):
    with db.session() as session:
        earthquake = session.get(Earthquake, id)
        if earthquake is None:
            return jsonify({'message': f'Earthquake {id} not found.'}), 404
        return jsonify(earthquake.to_dict())

@app.route('/earthquakes/<int:id>', methods=['DELETE'])
def delete_earthquake(id):
    with db.session() as session:
        earthquake = session.get(Earthquake, id)
        if earthquake is None:
            return jsonify({'message': f'Earthquake {id} not found.'}), 404
        session.delete(earthquake)
        session.commit()
        return jsonify({'message': f'Earthquake {id} deleted.'})

@app.route('/earthquakes', methods=['GET'])
def get_earthquakes():
    earthquakes = Earthquake.query.all()
    return jsonify([earthquake.to_dict() for earthquake in earthquakes])

@app.route('/earthquakes', methods=['POST'])
def create_earthquake():
    data = request.get_json()
    if not data or not all(key in data for key in ('magnitude', 'location', 'year')):
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    earthquake = Earthquake(
        magnitude=data['magnitude'],
        location=data['location'],
        year=data['year']
    )
    db.session.add(earthquake)
    db.session.commit()
    return jsonify(earthquake.to_dict()), 201


@app.route('/earthquakes/magnitude/<float:magnitude>', methods=['GET'])
def get_earthquakes_by_magnitude(magnitude):
    earthquakes = Earthquake.query.filter(Earthquake.magnitude >= magnitude).all()
    quakes = [earthquake.to_dict() for earthquake in earthquakes]
    return jsonify({'count': len(quakes), 'quakes': quakes})
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(message="Resource not found"), 404


if __name__ == '__main__':
    app.run(port=5555, debug=True)