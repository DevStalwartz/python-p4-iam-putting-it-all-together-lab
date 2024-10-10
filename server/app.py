from flask import Flask, request, session, jsonify
from flask_restful import Resource, Api
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Signup Resource
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio', '')
        image_url = data.get('image_url', '')

        new_user = User(username=username, bio=bio, image_url=image_url)
        new_user.set_password(password)  # Hash the password

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return jsonify(new_user.to_dict()), 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists'}, 422
        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": [str(e)]}), 422

# CheckSession Resource
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return jsonify(user.to_dict())
        return {'error': 'Not logged in'}, 401

# Login Resource
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            session['user_id'] = user.id
            return jsonify(user.to_dict())
        return {'error': 'Invalid username or password'}, 401

# Logout Resource
class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {'message': 'Successfully logged out'}, 200

# RecipeIndex Resource
class RecipeIndex(Resource):
    def get(self):
        recipes = Recipe.query.all()
        return jsonify([recipe.to_dict() for recipe in recipes])

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or not minutes_to_complete:
            return {'error': 'Missing required fields'}, 422

        new_recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id
        )

        db.session.add(new_recipe)
        db.session.commit()

        return jsonify(new_recipe.to_dict()), 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
